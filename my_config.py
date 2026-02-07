# config.py
import datetime
now = datetime.datetime.now()
yesterday = now - datetime.timedelta(days=1)
yesterday_str = yesterday.strftime("%Y/%m/%d")


# --- 1. DeepSeek / OpenAI 配置 ---
API_KEY = "sk-86db1656b5a34daf8d856c58dd064530"  # 你的真实 Key
API_BASE = "https://api.deepseek.com"
MODEL_NAME = "deepseek-chat"

# --- 2. 邮箱发送配置 ---
SMTP_SERVER = "smtp.163.com"
SMTP_PORT = 465
SENDER_EMAIL = "ahmulwh@163.com"
SENDER_PASS = "AL2itGnWK8MgcGfi"  # 你的真实授权码

# --- 3. 接收人列表 ---
# 可以是单个字符串，也可以是列表
RECEIVERS = "ahmulwh@163.com"


# --- 4. 搜索参数 ---
# 这里的日期可以用 datetime 动态生成，也可以写死

SEARCH_QUERY = f'(Hypertension, Pulmonary[MeSH Terms]) AND ("{yesterday_str}"[EDAT] : "3000"[EDAT])'
MAX_RESULTS = 20
BATCH_SIZE = 5

# --- 5. PUBMED ---
PUBMED_EMAIL = "lwh20000531@gmail.com"