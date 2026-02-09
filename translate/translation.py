import openai
import json
import time
from tenacity import retry, stop_after_attempt, wait_exponential  # 建议安装这个库

# 使用 retry 装饰器处理网络波动和 API 限制
@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def call_llm_api(client, model_name, prompt):
    response = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        response_format={'type': 'json_object'},  # 强制 JSON
        temperature=0.5  # 降低随机性，使翻译更稳定
    )
    return response.choices[0].message.content

def translate_articles(articles, batch_size, translation_key, model_api, model_name):
    client = openai.OpenAI(api_key=translation_key, base_url=model_api)
    
    # 1. 将原列表转为字典，方便 O(1) 查找，提高效率
    article_map = {str(a['PMID']): a for a in articles}
    to_translate = articles

    for i in range(0, len(to_translate), batch_size):
        batch = to_translate[i:i + batch_size]
        batch_input = [{"PMID": a['PMID'], "TITLE": a['TITLE'], "ABSTRACT": a['ABSTRACT']} for a in batch]

        # 修复后的 Prompt
        prompt = f"""
        你是一位生物医学专家翻译官。请翻译以下文献至学术中文。
        要求：
        1. 必须返回 JSON 对象，格式为：{{{{ "translations": [{{{{ "PMID": "...", "TITLE_CN": "...", "ABSTRACT_CN": "..." }}}}] }}}}
        2. 确保每个传入的 PMID 都有对应的翻译条目。
        3. 翻译风格：正式、专业、符合中国生物医学学术语境。

        待翻译数据：
        {json.dumps(batch_input, ensure_ascii=False)}
        """

        try:
            content = call_llm_api(client, model_name, prompt)
            results = json.loads(content)
            
            # 获取翻译列表（增强容错：如果模型没按 key 返回，尝试拿第一个列表值）
            translated_list = results.get('translations') or list(results.values())[0]

            for t_item in translated_list:
                pmid_str = str(t_item.get('PMID'))
                if pmid_str in article_map:
                    article_map[pmid_str]['TITLE_CN'] = t_item.get('TITLE_CN')
                    article_map[pmid_str]['ABSTRACT_CN'] = t_item.get('ABSTRACT_CN')
            
            print(f"✅ 第 {i//batch_size + 1} 组成功")
            
        except Exception as e:
            print(f"❌ 第 {i//batch_size + 1} 组最终失败: {e}")
            # 这里可以考虑将失败的 PMID 记录下来，稍后重试

    return list(article_map.values())