from email.message import EmailMessage
from email.utils import formataddr
import ssl
import smtplib
from dotenv import load_dotenv
import os
from datetime import date
from pathlib import Path

PORT=465
EMAIL_SERVER = "smtp.gmail.com"

# Load the environment variables
current_dir = Path(__file__).resolve().parent if "__file__" in locals() else Path.cwd()
envars = current_dir / ".env"
load_dotenv(envars)
  #read info
sender_email = os.getenv("EMAIL")
password_email = os.getenv("PASSWORD")

def post_email(recipient, name, filedir, formlink):
  today = str(date.today())
  subject = today + " 학습지"
  em = EmailMessage()
  em['From'] = formataddr(("예산명지병원 유승모 병원장", f"{sender_email}"))
  em['To'] = recipient
  em['Subject'] = subject
  em.set_content(
    f"""\
    안녕하세요 {name}님\
    퀴즈: {formlink}\
    좋은 하루 되세요!
    """
  )

  with open(filedir, 'rb') as f:
      file_data = f.read()
      file_name = os.path.basename(filedir)
      em.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)

  context = ssl.create_default_context()
  with smtplib.SMTP_SSL(EMAIL_SERVER,PORT,context=context) as smtp:
    smtp.login(sender_email, password_email)
    smtp.sendmail(sender_email, recipient, em.as_string())

if __name__ == "__main__":
    post_email(
      recipient="kimtyoun8849@gmail.com",
      name="김태윤",
      filedir="https://drive.google.com/drive/folders/1vR0rbKZFcGnZx9Bp71ANwuWM6bPeFYPh",
      formlink="forms.google.com"
  )
