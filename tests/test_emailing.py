from __future__ import annotations

from src.config import Settings
from src.utils import emailing


def test_build_subscription_confirmation_link_contains_expected_query_params() -> None:
    link = emailing.build_subscription_confirmation_link(
        "user+demo@example.com",
        "http://localhost:8501",
        lang="de",
    )

    assert link.startswith("http://localhost:8501/?")
    assert "page=subscription-confirmation" in link
    assert "lang=de" in link
    assert "newsletter_confirmed=1" in link
    assert "newsletter_email=user%2Bdemo%40example.com" in link


def test_send_subscription_confirmation_email_returns_disabled_when_smtp_not_configured(monkeypatch) -> None:
    monkeypatch.setattr(emailing, "_mail_app_available", lambda: False)
    config = Settings(
        smtp_host="",
        smtp_sender_email="",
    )

    result = emailing.send_subscription_confirmation_email(
        "user@example.com",
        "http://localhost:8501/?page=subscription-confirmation",
        config,
    )

    assert result.sent is False
    assert result.status == "disabled"


def test_send_subscription_confirmation_email_uses_smtp(monkeypatch) -> None:
    captured: dict[str, object] = {}

    class FakeSMTP:
        def __init__(self, host: str, port: int, timeout: int) -> None:
            captured["host"] = host
            captured["port"] = port
            captured["timeout"] = timeout

        def __enter__(self) -> "FakeSMTP":
            return self

        def __exit__(self, exc_type, exc, tb) -> None:
            return None

        def ehlo(self) -> None:
            captured["ehlo"] = True

        def starttls(self, context=None) -> None:
            captured["starttls"] = context is not None

        def login(self, username: str, password: str) -> None:
            captured["username"] = username
            captured["password"] = password

        def send_message(self, message) -> None:
            captured["subject"] = message["Subject"]
            captured["to"] = message["To"]

    monkeypatch.setattr(emailing.smtplib, "SMTP", FakeSMTP)

    config = Settings(
        smtp_host="smtp.example.com",
        smtp_port=587,
        smtp_username="smtp-user",
        smtp_password="smtp-pass",
        smtp_sender_email="no-reply@example.com",
        smtp_sender_name="certAIn",
        smtp_use_tls=True,
        smtp_use_ssl=False,
    )

    result = emailing.send_subscription_confirmation_email(
        "user@example.com",
        "http://localhost:8501/?page=subscription-confirmation",
        config,
    )

    assert result.sent is True
    assert result.status == "sent"
    assert captured["host"] == "smtp.example.com"
    assert captured["port"] == 587
    assert captured["username"] == "smtp-user"
    assert captured["password"] == "smtp-pass"
    assert captured["to"] == "user@example.com"


def test_send_subscription_confirmation_email_falls_back_to_mail_app(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_mail_app_available() -> bool:
        return True

    def fake_run(command, check, capture_output, text, timeout):
        captured["command"] = command
        return None

    monkeypatch.setattr(emailing, "_mail_app_available", fake_mail_app_available)
    monkeypatch.setattr(emailing.subprocess, "run", fake_run)

    config = Settings(
        smtp_host="",
        smtp_sender_email="",
    )

    result = emailing.send_subscription_confirmation_email(
        "user@example.com",
        "http://localhost:8501/?page=subscription-confirmation",
        config,
    )

    assert result.sent is True
    assert result.status == "sent"
    assert captured["command"][0] == "osascript"


def test_send_registration_confirmation_email_returns_disabled_when_no_sender(monkeypatch) -> None:
    monkeypatch.setattr(emailing, "_mail_app_available", lambda: False)
    config = Settings(
        smtp_host="",
        smtp_sender_email="",
    )

    result = emailing.send_registration_confirmation_email("user@example.com", config)

    assert result.sent is False
    assert result.status == "disabled"


def test_send_registration_confirmation_email_falls_back_to_mail_app(monkeypatch) -> None:
    captured: dict[str, object] = {}

    def fake_mail_app_available() -> bool:
        return True

    def fake_run(command, check, capture_output, text, timeout):
        captured["command"] = command
        return None

    monkeypatch.setattr(emailing, "_mail_app_available", fake_mail_app_available)
    monkeypatch.setattr(emailing.subprocess, "run", fake_run)

    config = Settings(
        smtp_host="",
        smtp_sender_email="",
    )

    result = emailing.send_registration_confirmation_email("user@example.com", config)

    assert result.sent is True
    assert result.status == "sent"
    assert captured["command"][0] == "osascript"
