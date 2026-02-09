# config.py
import datetime
now = datetime.datetime.now()
yesterday = now - datetime.timedelta(days=3)
yesterday_str = yesterday.strftime("%Y/%m/%d")


# --- 1. DeepSeek / OpenAI 配置 ---
API_KEY = ""  
API_BASE = ""
MODEL_NAME = ""

# --- 2. 邮箱发送配置 ---
SMTP_SERVER = ""
SMTP_PORT = None
SENDER_EMAIL = ""
SENDER_PASS = ""  # 你的真实授权码

# --- 3. 接收人列表 ---
# 可以是单个字符串，也可以是列表
RECEIVERS = ""
CONTROLLER = ""


# --- 4. 搜索参数 ---
# 这里的日期可以用 datetime 动态生成，也可以写死

SEARCH_QUERY = f'(Hypertension, Pulmonary[MeSH Terms]) AND ("{yesterday_str}"[CRDT] : "3000"[CRDT])'
MAX_RESULTS = 20
BATCH_SIZE = 5

# --- 5. PUBMED ---
PUBMED_EMAIL = ""