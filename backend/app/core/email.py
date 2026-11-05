import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import settings

logger = logging.getLogger("homeserve.email")

def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """
    Dispatches a password reset email containing the 15-minute token.
    If SMTP credentials are provided in environment variables, sends via real SMTP.
    Otherwise, logs securely to application log for local test/dev environments.
    """
    subject = "HomeServe Password Reset Token (Valid for 15 minutes)"
    text_content = f"""Hello,

You recently requested to reset your password for your HomeServe account.
Your password reset token is:

    {reset_token}

This token is valid for 15 minutes from the time of this request.
If you did not request a password reset, please ignore this email.

Best regards,
The HomeServe Security Team
"""

    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
        <div style="max-width: 600px; margin: 0 auto; padding: 20px; border: 1px solid #e2e8f0; rounded: 8px;">
          <h2 style="color: #2563eb;">HomeServe Account Security</h2>
          <p>You requested to reset your password. Use the verification token below to proceed:</p>
          <div style="background-color: #f1f5f9; padding: 12px 20px; border-radius: 6px; font-size: 20px; font-family: monospace; font-weight: bold; letter-spacing: 2px; color: #1e293b; text-align: center; margin: 20px 0;">
            {reset_token}
          </div>
          <p style="color: #64748b; font-size: 13px;">This token expires in <strong>15 minutes</strong>.</p>
          <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;" />
          <p style="color: #94a3b8; font-size: 12px;">If you did not make this request, your account remains secure and no further action is required.</p>
        </div>
      </body>
    </html>
    """

    if settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD:
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{settings.EMAILS_FROM_NAME} <{settings.EMAILS_FROM_EMAIL}>"
            msg["To"] = to_email

            part1 = MIMEText(text_content, "plain")
            part2 = MIMEText(html_content, "html")
            msg.attach(part1)
            msg.attach(part2)

            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.sendmail(settings.EMAILS_FROM_EMAIL, [to_email], msg.as_string())
            logger.info(f"Password reset email sent to {to_email}")
            return True
        except Exception as e:
            logger.error(f"Failed to send password reset email to {to_email}: {e}")
            return False
    else:
        logger.info(f"[DEV/TEST SIMULATION] Password reset email prepared for {to_email}. Token: {reset_token[:2]}**** (Valid 15m)")
        return True
