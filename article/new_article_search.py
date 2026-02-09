from Bio import Entrez
import os
import time
import json
from impact_factor.core import Factor
fa = Factor()


def search_and_fetch_pubmed(query, max_results=10):
    """
    搜索并直接返回完整的文章信息列表
    """
    try:
        # 第一步：搜索 PMID
        handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=max_results,
            sort="relevance"
        )
        record = Entrez.read(handle)
        handle.close()

        current_id_list = record.get("IdList", [])
        if not current_id_list:
            print("未找到任何相关文献。")
            return []

        print(f"🔍找到 {len(current_id_list)} 篇")

        # 1. 初始化：默认假设所有 ID 都是新的（针对第一次运行的情况）
        new_id_list = current_id_list 

        # 2. 判断：如果历史文件存在，则进行比对
        if os.path.exists("pubmed_history.json"):
            print("📂 发现历史记录文件: 'pubmed_history.json'")
            try:
                with open("pubmed_history.json", 'r', encoding='utf-8') as f:
                    old_id_list = json.load(f)
                    old_id_set = set(old_id_list) # 转为集合方便计算
                
                # 计算差集：今天搜到的 - 历史已有的
                current_id_set = set(current_id_list)
                new_ids_set = current_id_set - old_id_set
                new_id_list = list(new_ids_set)
                
                print(f"📊 比对完成：当前 {len(current_id_list)} 篇，历史 {len(old_id_set)} 篇，新增 {len(new_id_list)} 篇。")
            
            except Exception as e:
                print(f"⚠️ 读取历史文件出错 (将执行全量查询): {e}")
                # 如果读文件报错，new_id_list 保持为 current_id_list，相当于全量查询
        else:
            print("🆕 未发现历史记录文件，将执行全量查询并创建记录。")

        # --- 覆写历史文件 (为明天做准备) ---
        # 无论是否有新增，都把“今天搜到的所有ID”存进去，作为下一次的“历史”
        try:
            with open("pubmed_history.json", 'w', encoding='utf-8') as f:
                json.dump(current_id_list, f)
        except Exception as e:
            print(f"❌ 写入历史文件失败: {e}")

        # --- 如果没有新文章，直接结束 ---
        if not new_id_list:
            print("✅ 没有发现新文章，任务结束。")
            return []


        # 第二步：根据 PMID 抓取详细内容 (EFetch)
        print(f"找到 {len(new_id_list)} 篇新文献，正在获取详情...")
        
        # 抓取详细 XML
        fetch_handle = Entrez.efetch(
            db="pubmed",
            id=",".join(new_id_list), # 把 PMID 用逗号连起来一次性查询
            retmode="xml"
        )
        # 解析复杂的 PubMed XML
        full_records = Entrez.read(fetch_handle)
        fetch_handle.close()

        articles_data = []
        for article in full_records['PubmedArticle']:
            medline_citation = article.get('MedlineCitation', {})
            article_info = medline_citation.get('Article', {})
            journal_info = article_info.get('Journal', {})

            pub_type = article_info.get('PublicationTypeList', [])
            pub_type_str = ", ".join([str(pt) for pt in pub_type]) if pub_type else "Unknown"
            pmid = medline_citation.get('PMID', '?')
            title = article_info.get('ArticleTitle', 'No title')
            abstract_list = article_info.get('Abstract', {}).get('AbstractText', [])
            abstract = " ".join(abstract_list) if abstract_list else "No abstract"
            journal_ISSN = journal_info.get('ISSN', 'No ISSN')
            journal_title = journal_info.get('Title', 'No journal')

            paper = {
                'TYPE': str(pub_type_str),
                'PMID': str(pmid),
                'JOURNAL': str(journal_title),
                'IF': "N/A",
                "JCR":"N/A",
                'TITLE': str(title),
                'ABSTRACT': str(abstract),
                'JOURNAL': str(journal_title)
            }
            res = fa.search(journal_ISSN) or fa.search(journal_title)
            if res:
                 paper["IF"] = res[0].get('factor', '0')
                 paper["JCR"] = res[0].get('jcr', 'N/A')
            articles_data.append(paper)
        

        def get_sorting_value(article):
    
            val = article.get('IF', 'N/A')

            try:
                return float(val)
            except (ValueError, TypeError):
                 return -1.0
        articles_data.sort(key=get_sorting_value, reverse=True)
        return articles_data

    except Exception as e:
        print(f"❌ 出错: {e}")
        return []

# 测试运行





