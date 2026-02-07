for i in range(0, len(results), 2):
        batch = results[i:i + 2]
        
        # 构造输入格式
        batch_input = []
        for a in batch:
            batch_input.append({
                "PMID": a['PMID'],
                "TITLE": a['TITLE'],
                "ABSTRACT": a['ABSTRACT'] # 限制摘要长度防止超过 Token 限制
            })
        print(batch_input)
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
        print(batch_input)


response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[{"role": "user", "content": prompt}],
    response_format={'type': 'json_object'} # 强制返回 JSON 格式
            )
            
# 3. 解析并对号入座
results2 = json.loads(response.choices[0].message.content)
            # 假设返回格式是 {"results": [{"pmid": "...", "title_cn": "...", "abstract_cn": "..."}, ...]}
translated_list = results2.get('translations', [])

print(translated_list)
