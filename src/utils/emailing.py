from __future__ import annotations

import platform
import subprocess
import smtplib
import ssl
from dataclasses import dataclass
from email.message import EmailMessage
from email.utils import formataddr
from urllib.parse import urlencode

from src.config import Settings


@dataclass(frozen=True)
class EmailDeliveryResult:
    sent: bool
    status: str
    message: str


def _plain_text_confirmation_body(confirmation_link: str) -> str:
    return "\n".join(
        [
            "Thanks for subscribing to certAIn updates.",
            "",
            "Please confirm your subscription by clicking the link below:",
            confirmation_link,
            "",
            "If you did not request this, you can ignore this email.",
        ]
    )


def _mail_app_available() -> bool:
    if platform.system() != "Darwin":
        return False
    try:
        result = subprocess.run(
            ["osascript", "-e", 'tell application "Mail" to get name of every account'],
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except Exception:
        return False
    return bool(result.stdout.strip())


def _send_via_mail_app(
    recipient_email: str,
    subject: str,
    body: str,
) -> EmailDeliveryResult:
    script = """
    on run argv
      set recipientEmail to item 1 of argv
      set emailSubject to item 2 of argv
      set emailBody to item 3 of argv
      tell application "Mail"
        set newMessage to make new outgoing message with properties {subject:emailSubject, content:emailBody, visible:false}
        tell newMessage
          make new to recipient at end of to recipients with properties {address:recipientEmail}
          send
        end tell
      end tell
    end run
    """
    try:
        subprocess.run(
            ["osascript", "-e", script, recipient_email, subject, body],
            check=True,
            capture_output=True,
            text=True,
            timeout=20,
        )
    except Exception as exc:
        return EmailDeliveryResult(
            sent=False,
            status="error",
            message=f"Confirmation email could not be sent through Mail.app: {exc}",
        )
    return EmailDeliveryResult(
        sent=True,
        status="sent",
        message=f"A confirmation email was sent to {recipient_email}.",
    )


def _send_via_smtp(
    recipient_email: str,
    subject: str,
    plain_text_body: str,
    html_body: str,
    config: Settings,
) -> EmailDeliveryResult:
    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = formataddr((config.smtp_sender_name, config.smtp_sender_email))
    message["To"] = recipient_email
    message.set_content(plain_text_body)
    message.add_alternative(html_body, subtype="html")

    try:
        if config.smtp_use_ssl:
            with smtplib.SMTP_SSL(
                config.smtp_host,
                config.smtp_port,
                context=ssl.create_default_context(),
                timeout=20,
            ) as server:
                if config.smtp_username:
                    server.login(config.smtp_username, config.smtp_password)
                server.send_message(message)
        else:
            with smtplib.SMTP(config.smtp_host, config.smtp_port, timeout=20) as server:
                server.ehlo()
                if config.smtp_use_tls:
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()
                if config.smtp_username:
                    server.login(config.smtp_username, config.smtp_password)
                server.send_message(message)
    except Exception as exc:
        return EmailDeliveryResult(
            sent=False,
            status="error",
            message=f"Confirmation email could not be sent: {exc}",
        )

    return EmailDeliveryResult(
        sent=True,
        status="sent",
        message=f"A confirmation email was sent to {recipient_email}.",
    )


def build_subscription_confirmation_link(
    recipient_email: str,
    app_base_url: str,
    *,
    lang: str = "en",
) -> str:
    query = urlencode(
        {
            "page": "subscription-confirmation",
            "lang": lang,
            "newsletter_email": recipient_email,
            "newsletter_confirmed": "1",
        }
    )
    return f"{app_base_url.rstrip('/')}/?{query}"


def send_subscription_confirmation_email(
    recipient_email: str,
    confirmation_link: str,
    config: Settings,
) -> EmailDeliveryResult:
    if not recipient_email:
        return EmailDeliveryResult(
            sent=False,
            status="invalid",
            message="A valid recipient email address is required.",
        )
    subject = "Confirm your certAIn subscription"
    plain_text_body = _plain_text_confirmation_body(confirmation_link)
    html_body = f"""
    <html>
      <body style="font-family:Arial,sans-serif;background:#070d18;color:#eef5ff;padding:24px;">
        <div style="max-width:560px;margin:0 auto;background:#0b1220;border:1px solid rgba(109,165,255,0.24);border-radius:18px;padding:28px;">
          <p style="color:#75e7ff;font-size:12px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin:0 0 12px;">certAIn Newsletter</p>
          <h1 style="font-size:28px;line-height:1.2;margin:0 0 14px;">Confirm your subscription</h1>
          <p style="color:#dbe7fa;line-height:1.6;margin:0 0 22px;">
            Thanks for subscribing to certAIn updates. Confirm your email to start receiving product and release highlights.
          </p>
          <p style="margin:0 0 24px;">
            <a href="{confirmation_link}" style="display:inline-block;padding:14px 22px;border-radius:14px;background:linear-gradient(90deg,#7357ff 0%,#2fa2ff 100%);color:#ffffff;text-decoration:none;font-weight:700;">
              Confirm subscription
            </a>
          </p>
          <p style="color:#9eb0cb;line-height:1.6;margin:0;">
            If you did not request this, you can ignore this email.
          </p>
        </div>
      </body>
    </html>
    """

    if config.smtp_enabled:
        return _send_via_smtp(recipient_email, subject, plain_text_body, html_body, config)

    if _mail_app_available():
        return _send_via_mail_app(recipient_email, subject, plain_text_body)

    return EmailDeliveryResult(
        sent=False,
        status="disabled",
        message="Email delivery is not configured yet. Add SMTP settings or use Mail.app on macOS.",
    )


def send_registration_confirmation_email(
    recipient_email: str,
    config: Settings,
) -> EmailDeliveryResult:
    if not recipient_email:
        return EmailDeliveryResult(
            sent=False,
            status="invalid",
            message="A valid recipient email address is required.",
        )

    subject = "Your certAIn registration has been confirmed"
    plain_text_body = "\n".join(
        [
            "Your registration has been confirmed.",
            "",
            "You can now continue with certAIn.",
        ]
    )
    html_body = """
    <html>
      <body style="font-family:Arial,sans-serif;background:#070d18;color:#eef5ff;padding:24px;">
        <div style="max-width:560px;margin:0 auto;background:#0b1220;border:1px solid rgba(109,165,255,0.24);border-radius:18px;padding:28px;">
          <p style="color:#75e7ff;font-size:12px;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;margin:0 0 12px;">certAIn Registration</p>
          <h1 style="font-size:28px;line-height:1.2;margin:0 0 14px;">Your registration has been confirmed.</h1>
          <p style="color:#dbe7fa;line-height:1.6;margin:0;">
            You can now continue with certAIn.
          </p>
        </div>
      </body>
    </html>
    """

    if config.smtp_enabled:
        return _send_via_smtp(recipient_email, subject, plain_text_body, html_body, config)

    if _mail_app_available():
        return _send_via_mail_app(recipient_email, subject, plain_text_body)

    return EmailDeliveryResult(
        sent=False,
        status="disabled",
        message="Email delivery is not configured yet. Add SMTP settings or use Mail.app on macOS.",
    )
