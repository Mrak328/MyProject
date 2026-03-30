import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
from app.core.config import settings


class EmailService:
    """Сервис для отправки email"""

    SMTP_HOST = "smtp.gmail.com"
    SMTP_PORT = 587
    SMTP_USER = "your-email@gmail.com"
    SMTP_PASSWORD = "your-password"

    @staticmethod
    def send_email(
            to: str,
            subject: str,
            body: str,
            html: Optional[str] = None
    ) -> bool:
        """Отправка email"""
        try:
            msg = MIMEMultipart()
            msg["From"] = EmailService.SMTP_USER
            msg["To"] = to
            msg["Subject"] = subject

            msg.attach(MIMEText(body, "plain"))
            if html:
                msg.attach(MIMEText(html, "html"))

            with smtplib.SMTP(EmailService.SMTP_HOST, EmailService.SMTP_PORT) as server:
                server.starttls()
                server.login(EmailService.SMTP_USER, EmailService.SMTP_PASSWORD)
                server.send_message(msg)

            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    @staticmethod
    def send_welcome_email(to: str, name: str) -> bool:
        """Отправка приветственного письма"""
        subject = "Добро пожаловать!"
        body = f"Здравствуйте, {name}! Спасибо за регистрацию."
        html = f"""
        <h2>Добро пожаловать!</h2>
        <p>Здравствуйте, {name}!</p>
        <p>Спасибо за регистрацию на нашем сайте.</p>
        """
        return EmailService.send_email(to, subject, body, html)

    @staticmethod
    def send_verification_code(to: str, code: str) -> bool:
        """Отправка кода подтверждения"""
        subject = "Код подтверждения"
        body = f"Ваш код подтверждения: {code}"
        html = f"""
        <h2>Код подтверждения</h2>
        <p>Ваш код: <strong>{code}</strong></p>
        <p>Введите его на сайте для подтверждения.</p>
        """
        return EmailService.send_email(to, subject, body, html)

    @staticmethod
    def send_new_listing_notification(to: str, listing_title: str, listing_url: str) -> bool:
        """Уведомление о новом объявлении (для подписчиков)"""
        subject = f"Новое объявление: {listing_title}"
        body = f"Появилось новое объявление: {listing_title}\nСсылка: {listing_url}"
        html = f"""
        <h2>Новое объявление</h2>
        <p><a href="{listing_url}">{listing_title}</a></p>
        <p>Посмотрите скорее!</p>
        """
        return EmailService.send_email(to, subject, body, html)


email_service = EmailService()