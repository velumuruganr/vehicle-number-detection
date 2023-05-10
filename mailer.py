import smtplib, ssl
import os
from dotenv import load_dotenv

load_dotenv()

port = 587  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = os.environ.get('SMTP_EMAIL')
receiver_email = "your@gmail.com"  # Enter receiver address
password = os.environ.get('SMTP_PASSWORD')
message = """Your video is processed and the vehicle numbers are detected."""
context = ssl.create_default_context()

with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)