import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)

class EmailService:
    """Abstracted email service supporting SMTP delivery with logging fallback."""
    
    @staticmethod
    def send_email(to_email: str, subject: str, body: str) -> bool:
        """Sends an email using SMTP if configured, otherwise falls back to logger."""
        # Provider configuration
        smtp_host = getattr(settings, "SMTP_HOST", None)
        smtp_port = getattr(settings, "SMTP_PORT", 587)
        smtp_user = getattr(settings, "SMTP_USERNAME", None)
        smtp_pass = getattr(settings, "SMTP_PASSWORD", None)
        from_email = getattr(settings, "SMTP_FROM_EMAIL", "no-reply@cybershakti.in")

        # Mock / Development mode logging fallback
        if not smtp_host or settings.ENVIRONMENT.lower() in ("dev", "development"):
            logger.info("=== [MOCK EMAIL SERVICE] ===")
            logger.info("To: %s", to_email)
            logger.info("Subject: %s", subject)
            logger.info("Body preview: %s", body[:150])
            logger.info("============================")
            return True

        try:
            msg = MIMEMultipart()
            msg["From"] = from_email
            msg["To"] = to_email
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            if smtp_user and smtp_pass:
                server.login(smtp_user, smtp_pass)
            server.sendmail(from_email, to_email, msg.as_string())
            server.quit()
            logger.info("Email sent successfully to %s", to_email)
            return True
        except Exception as e:
            logger.error("Failed to send email to %s: %s", to_email, str(e))
            return False

    @classmethod
    def send_verification_email(cls, to_email: str, token: str) -> bool:
        """Sends verification email with link containing token (token is NOT logged)."""
        # Form verification URL (port 8000 default or frontend URL)
        verification_link = f"http://localhost:8000/api/v1/auth/verify-email?token={token}"
        subject = "Verify your CyberShakti Account"
        body = f"Welcome to CyberShakti!\n\nPlease click the link below to verify your email address:\n\n{verification_link}\n\nThis link will expire in 24 hours."
        return cls.send_email(to_email, subject, body)

    @classmethod
    def send_password_reset_email(cls, to_email: str, token: str) -> bool:
        """Sends password reset email with reset token (token is NOT logged)."""
        # Password reset URL
        reset_link = f"http://localhost:3000/reset-password?token={token}"
        subject = "Reset your CyberShakti Password"
        body = f"Hello,\n\nYou requested a password reset for your CyberShakti account.\n\nPlease click the link below to set a new password:\n\n{reset_link}\n\nIf you did not request this, please ignore this email. This link will expire in 1 hour."
        return cls.send_email(to_email, subject, body)
