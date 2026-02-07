import smtplib
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formataddr


def send_html_email(html_content, receiver_email,sender_email,sender_pass,smtp_server,smtp_port):
    """
    发送 HTML 格式的邮件
    :param html_content: 你的 format_articles_to_mobile_html 函数生成的 HTML 字符串
    :param receiver_email: 接收者的邮箱地址
    """
    # 1. 配置你的发件人信息 (建议放入 config 或环境变量)
    my_sender = sender_email    # 发件人邮箱账号
    my_pass = sender_pass          # ⚠️ 注意：这里填授权码，不是登录密码！
    smtp_server = smtp_server     # QQ邮箱服务器
    smtp_port = smtp_port                # SSL 端口

    # 2. 构建邮件对象
    # ⚠️ 关键点：第二个参数必须是 'html'，如果是 'plain' 就会显示代码乱码
    msg = MIMEText(html_content, 'html', 'utf-8')
    
    # 3. 设置邮件头 (让收件人看到漂亮的昵称)
    msg['From'] = formataddr(["LWH's PubMed Bot", my_sender])  # 发件人昵称 <邮箱>
    msg['To'] = formataddr(["Researcher", receiver_email]) # 收件人昵称 <邮箱>
    msg['Subject'] = Header("今日文献推送 (含 JCR 分区)", 'utf-8') # 邮件标题

    ret = True
    try:
        # 4. 连接服务器并发送
        server = smtplib.SMTP_SSL(smtp_server, smtp_port) 
        server.login(my_sender, my_pass)  
        server.sendmail(my_sender, [receiver_email,], msg.as_string()) 
        server.quit() 
        print(f"✅ 邮件已成功发送给 {receiver_email}")
    except Exception as e:
        ret = False
        print(f"❌ 邮件发送失败: {e}")
    
    return ret

