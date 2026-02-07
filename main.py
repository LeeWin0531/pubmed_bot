# main.py
import sys
import datetime
import my_config  # 你的配置文件

# --- 导入你的四个功能模块 ---
from Bio import Entrez
from article.new_article_search import search_and_fetch_pubmed
from translate.translation import translate_articles
from export.export_html2 import format_articles_to_mobile_html
from send_email.send_email import send_html_email

def run_pipeline():
    print(f"🚀 [{datetime.datetime.now()}] 任务启动...")
    
    # --- 1. 全局配置注入 ---
    Entrez.email = my_config.PUBMED_EMAIL
    print(f"🔧 全局配置已设置: Entrez Email = {Entrez.email}")

    # --- 2. 获取文献 ---
    print(f"🔍 Step 1: 正在搜索文献 query: {my_config.SEARCH_QUERY}")
    results = search_and_fetch_pubmed(
        my_config.SEARCH_QUERY, 
        max_results=my_config.MAX_RESULTS
    )

    # 🛑 关键逻辑：如果没有文献，直接结束
    if not results:
        print("⚠️ 今天没有检索到相关文献，任务结束。")
        return  # 直接退出函数

    print(f"✅ 成功获取 {len(results)} 篇文献，准备翻译...")

    # --- 3. 翻译文献 ---
    print("🤖 Step 2: AI 翻译中 (请耐心等待)...")
    results_translated = translate_articles(
        articles=results,  # 传入刚才获取的列表
        batch_size=my_config.BATCH_SIZE,
        translation_key=my_config.API_KEY,
        model_api=my_config.API_BASE,
        model_name=my_config.MODEL_NAME
    )

    # --- 4. 格式化 HTML ---
    print("🎨 Step 3: 生成 HTML 报告...")
    html_report = format_articles_to_mobile_html(results_translated)
    
    # (可选) 本地保存一份副本用于检查
    with open("latest_report.html", "w", encoding="utf-8") as f:
        f.write(html_report)
    print("💾 副本已保存至 local: latest_report.html")

    # --- 5. 发送邮件 ---
    print("📧 Step 4: 开始发送邮件...")

    # 1️⃣ 【数据归一化】判断类型，统一转为列表
    # 获取原始配置
    raw_receivers = my_config.RECEIVERS
    
    receivers_list = []
    
    if isinstance(raw_receivers, str):
        # 情况A：如果是字符串 (例如 "boss@lab.com")
        # 直接把它装进列表里，变成 ["boss@lab.com"]
        receivers_list = [raw_receivers]
        print(f"ℹ️ 检测到单个收件人: {raw_receivers}")
        
    elif isinstance(raw_receivers, list):
        # 情况B：如果是列表 (例如 ["a@qq.com", "b@163.com"])
        # 直接使用
        receivers_list = raw_receivers
        print(f"ℹ️ 检测到收件人列表，共 {len(receivers_list)} 人")
        
    else:
        # 情况C：格式不对 (例如 None 或 数字)
        print("❌ 配置错误：RECEIVERS 必须是字符串或列表，跳过发送。")
        receivers_list = []

    # 2️⃣ 【循环发送】现在 receivers_list 必定是列表，放心循环
    for person in receivers_list:
        # 去除可能存在的空格 (容错处理)
        person = person.strip()
        if not person: continue # 跳过空字符串

        try:
            print(f"   -> 正在发送给: {person} ...")
            success = send_html_email(
                html_content=html_report, 
                receiver_email=person,          
                sender_email=my_config.SENDER_EMAIL,
                sender_pass=my_config.SENDER_PASS,
                smtp_server=my_config.SMTP_SERVER,
                smtp_port=my_config.SMTP_PORT
            )
            
            if success:
                print("      ✅ 发送成功")
            else:
                print("      ❌ 发送失败 (请检查授权码或网络)")
                
        except Exception as e:
            print(f"      ❌ 发送过程出错: {e}")

    print(f"🏁 [{datetime.datetime.now()}] 所有任务圆满完成！")
# --- 程序入口 ---
# 只有直接运行这个文件时，才会执行下面的代码
if __name__ == "__main__":
    try:
        run_pipeline()
    except KeyboardInterrupt:
        print("\n🛑 用户强制停止任务")
    except Exception as e:
        print(f"\n❌ 程序发生未捕获的异常: {e}")
        # 这里可以加代码：发生严重错误时给自己发个报警邮件


        