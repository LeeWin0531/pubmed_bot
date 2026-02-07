from Bio import Entrez
import time
from ..config import config
import json
from impact_factor.core import Factor
fa = Factor()



# 必须设置 Email
Entrez.email = config.pubmed_email
# 如果有 API Key，建议也加上
# Entrez.api_key = "your_api_key_here"

def search_and_fetch_pubmed(query, max_results=50):
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

        id_list = record.get("IdList", [])
        if not id_list:
            return []

        # 第二步：根据 PMID 抓取详细内容 (EFetch)
        print(f"找到 {len(id_list)} 篇文献，正在获取详情...")
        
        # 抓取详细 XML
        fetch_handle = Entrez.efetch(
            db="pubmed",
            id=",".join(id_list), # 把 PMID 用逗号连起来一次性查询
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

query = "(Hypertension, Pulmonary[MeSH Terms])"

results = search_and_fetch_pubmed(query, max_results=10)




