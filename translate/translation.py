import openai
import json
import time

def translate_high_impact_articles(articles, batch_size=3):

    to_translate = articles

    client = openai.OpenAI(api_key="sk-86db1656b5a34daf8d856c58dd064530", base_url="https://api.deepseek.com")

    # 2. 分批处理
    for i in range(0, len(to_translate), batch_size):
        batch = to_translate[i:i + batch_size]
        
        # 构造输入格式
        batch_input = []
        for a in batch:
            batch_input.append({
                "PMID": a['PMID'],
                "TITLE": a['TITLE'],
                "ABSTRACT": a['ABSTRACT'] # 限制摘要长度防止超过 Token 限制
            })

        prompt = f"""
        你是一位生物医学专家翻译官。请将以下 JSON 列表中的文献标题(TITLE)和摘要(ABSTRACT)翻译成学术中文。
        
        要求：
        1. 严格按 JSON 格式返回。
        2. 返回的 JSON 数组中必须包含 'PMID' 字段，以便我匹配。
        3. 翻译后的字段名为 'TITLE_CN' 和 'ABSTRACT_CN'。
        4. 不要包含任何多余的解释。

        待翻译数据：
        {json.dumps(batch_input, ensure_ascii=False)}
        """
        try:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                response_format={'type': 'json_object'} # 强制返回 JSON 格式
            )
            
            # 3. 解析并对号入座
            results = json.loads(response.choices[0].message.content)
            # 假设返回格式是 {"results": [{"pmid": "...", "title_cn": "...", "abstract_cn": "..."}, ...]}
            translated_list = results.get('translations', [])


            # 将翻译内容填回原始列表
            for t_item in translated_list:
                for original_art in articles:
                    if str(original_art['PMID']) == str(t_item['PMID']):
                        original_art['TITLE_CN'] = t_item.get('TITLE_CN')
                        original_art['ABSTRACT_CN'] = t_item.get('ABSTRACT_CN')
            
            print(f"✅ 已完成第 {i//batch_size + 1} 组翻译")
            time.sleep(1) # 避免触发频率限制

        except Exception as e:
            print(f"❌ 第 {i//batch_size + 1} 组翻译失败: {e}")

    return articles


result2 = translate_high_impact_articles(results)
