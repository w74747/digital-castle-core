import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class EmailService:
    def __init__(self):
        self.sender = os.getenv("SMTP_USER", "noreply@digitalcastle.io")
        self.password = os.getenv("SMTP_PASSWORD", "")
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
    
    async def send_email(self, to: str, subject: str, body: str):
        try:
            msg = MIMEMultipart()
            msg["From"] = self.sender
            msg["To"] = to
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "html"))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender, self.password)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            print(f"Email error: {e}")
            return False
    
    async def send_task_notification(self, email: str, task_title: str, status: str):
        subject = f"Task Update: {task_title}"
        body = f"""
        <h2>Task: {task_title}</h2>
        <p>Status: <strong>{status}</strong></p>
        <p>Visit your dashboard to view more details.</p>
        """
        return await self.send_email(email, subject, body)

email_service = EmailService()
