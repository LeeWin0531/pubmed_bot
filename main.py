# main.py
import my_config
import sys
import datetime
import subprocess
import io
import traceback
# 注意：这里千万不要导入 article, translate 等模块！
# from article.new_article_search import ... (❌ 不要写在这里)
class DualLogger:
    def __init__(self):
        self.terminal = sys.stdout          # 记住原本的屏幕输出渠道
        self.log_capture = io.StringIO()    # 创建一个内存缓冲区来存日志

    def write(self, message):
        self.terminal.write(message)        # 照常打印到屏幕
        self.log_capture.write(message)     # 同时写入内存

    def flush(self):
        self.terminal.flush()
        self.log_capture.flush()

    def get_log_content(self):
        return self.log_capture.getvalue()

def log(message):
    """带时间的打印函数"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def auto_update_library():
    """自动更新 impact_factor 库"""
    package = "impact-factor"
    log(f"🔄 正在检查 {package} 更新...")
    try:
        # 使用当前 Python 环境的 pip 进行更新
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "--upgrade", package],
            stdout=subprocess.DEVNULL, # 让它安静点，别打印一堆安装日志
            stderr=subprocess.DEVNULL
        )
        log(f"✅ {package} 检查完毕 (已是最新)")
    except Exception as e:
        log(f"⚠️ 自动更新失败: {e}")

def run_pipeline():
    # --- 1. 先跑更新 ---
    auto_update_library()
    
    # --- 2. 更新完之后，再导入业务模块 (关键！) ---
    # 这叫“延迟导入”，确保加载的是刚刚更新好的新包
    log("🚀 正在加载功能模块...")
    from Bio import Entrez
    from article.new_article_search import search_and_fetch_pubmed
    from translate.translation import translate_articles
    from export.export_html2 import format_articles_to_mobile_html
    from send_email.send_email import send_html_email
    # --- 3. 全局配置注入 ---
    Entrez.email = my_config.PUBMED_EMAIL
    log(f"🔧 全局配置已设置: Entrez Email = {Entrez.email}")

    # --- 4. 获取文献 ---
    log(f"🔍 Step 1: 正在搜索文献 query: {my_config.SEARCH_QUERY}")
    results = search_and_fetch_pubmed(
        my_config.SEARCH_QUERY, 
        max_results=my_config.MAX_RESULTS
    )

    # 🛑 关键逻辑：如果没有文献，直接结束
    if not results:
        log("⚠️ 今天没有检索到相关文献，任务结束。")
        return  # 直接退出函数

    log(f"✅ 成功获取 {len(results)} 篇文献，准备翻译...")

    # --- 5. 翻译文献 ---
    log("🤖 Step 2: AI 翻译中 (请耐心等待)...")
    results_translated = translate_articles(
        articles=results,  # 传入刚才获取的列表
        batch_size=my_config.BATCH_SIZE,
        translation_key=my_config.API_KEY,
        model_api=my_config.API_BASE,
        model_name=my_config.MODEL_NAME
    )

    # --- 6. 格式化 HTML ---
    log("🎨 Step 3: 生成 HTML 报告...")
    html_report = format_articles_to_mobile_html(results_translated)
    
    # (可选) 本地保存一份副本用于检查
    with open("latest_report.html", "w", encoding="utf-8") as f:
        f.write(html_report)
    log("💾 副本已保存至 local: latest_report.html")

    # --- 7. 发送邮件 ---
    log("📧 Step 4: 开始发送邮件...")

    # 1️⃣ 【数据归一化】判断类型，统一转为列表
    # 获取原始配置
    raw_receivers = my_config.RECEIVERS
    
    receivers_list = []
    
    if isinstance(raw_receivers, str):
        # 情况A：如果是字符串 (例如 "boss@lab.com")
        # 直接把它装进列表里，变成 ["boss@lab.com"]
        receivers_list = [raw_receivers]
        log(f"ℹ️ 检测到单个收件人: {raw_receivers}")
        
    elif isinstance(raw_receivers, list):
        # 情况B：如果是列表 (例如 ["a@qq.com", "b@163.com"])
        # 直接使用
        receivers_list = raw_receivers
        log(f"ℹ️ 检测到收件人列表，共 {len(receivers_list)} 人")
        
    else:
        # 情况C：格式不对 (例如 None 或 数字)
        log("❌ 配置错误：RECEIVERS 必须是字符串或列表，跳过发送。")
        receivers_list = []

    # 2️⃣ 【循环发送】现在 receivers_list 必定是列表，放心循环
    for person in receivers_list:
        # 去除可能存在的空格 (容错处理)
        person = person.strip()
        if not person: continue # 跳过空字符串

        try:
            log(f"   -> 正在发送给: {person} ...")
            success = send_html_email(
                html_content=html_report, 
                receiver_email=person,          
                sender_email=my_config.SENDER_EMAIL,
                sender_pass=my_config.SENDER_PASS,
                smtp_server=my_config.SMTP_SERVER,
                smtp_port=my_config.SMTP_PORT
            )
            
            if success:
                log("      ✅ 发送成功")
            else:
                log("      ❌ 发送失败 (请检查授权码或网络)")
                
        except Exception as e:
            log(f"      ❌ 发送过程出错: {e}")

    log(f"🏁 [{datetime.datetime.now()}] 所有任务圆满完成！")

if __name__ == "__main__":

    from send_email.send_email import send_log_email

    logger = DualLogger()
    # 把标准输出（print）和错误输出（报错）都接管过来
    sys.stdout = logger
    sys.stderr = logger

    run_status = "SUCCESS"
  
    try:
        run_pipeline()
    except Exception :
        run_status = "ERROR"
        traceback.print_exc()
    finally:
        # --- D. 无论成功失败，最后发送日志 ---
        # 恢复系统的标准输出，防止发送邮件函数里的 print 出问题
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__
        
        # 获取刚才所有的打印内容
        final_log = logger.get_log_content()
        
        # 发送给管理者
        send_log_email(final_log,                 
                       receiver_email=my_config.CONTROLLER_EMAIL,          
                       sender_email=my_config.SENDER_EMAIL,
                       sender_pass=my_config.SENDER_PASS,
                       smtp_server=my_config.SMTP_SERVER,
                       smtp_port=my_config.SMTP_PORT,status=run_status)