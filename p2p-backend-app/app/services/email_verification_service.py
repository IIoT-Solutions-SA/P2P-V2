"""
Email verification service for sending verification emails and OTP codes
"""
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from typing import Dict, Any
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Email configuration - centralized from settings
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fm = FastMail(conf)

async def send_email_verification(
    email: str,
    email_verify_url: str
) -> None:
    """
    Send email verification link to user

    Args:
        email: User's email address
        email_verify_url: Full URL for email verification (with token)
    """

    # Extract token from the URL
    import re
    from urllib.parse import urlparse, parse_qs
    parsed_url = urlparse(email_verify_url)
    query_params = parse_qs(parsed_url.query)
    token = query_params.get('token', [''])[0]
    tenant_id = query_params.get('tenantId', ['public'])[0]

    # Production URL for email (from central config)
    production_verify_url = f"{settings.PRODUCTION_URL}/auth/verify-email?token={token}&tenantId={tenant_id}"

    # Localhost URL for terminal logs
    localhost_verify_url = f"http://localhost:5173/auth/verify-email?token={token}&tenantId={tenant_id}"

    # Log localhost URL only in development. Do not print verification tokens in production/staging logs.
    if settings.ENVIRONMENT == "development":
        print(f"\n{'='*80}")
        print(f"📧 EMAIL VERIFICATION SENT TO: {email}")
        print(f"🔗 Localhost verification link (for dev testing):")
        print(f"   {localhost_verify_url}")
        print(f"{'='*80}\n")

    # HTML template matching invitation email style (uses production URL)
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 0;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                border-radius: 10px;
                overflow: hidden;
                margin: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
                font-weight: 600;
            }}
            .content {{
                padding: 30px;
            }}
            .button {{
                display: inline-block;
                padding: 14px 30px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white !important;
                text-decoration: none;
                border-radius: 5px;
                font-weight: 600;
                margin: 20px 0;
            }}
            .button:hover {{
                opacity: 0.9;
            }}
            .info-box {{
                background-color: #e7f3ff;
                border-left: 4px solid #2196F3;
                padding: 15px;
                margin: 20px 0;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 14px;
                background-color: #f8f9fa;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✉️ Verify Your Email Address</h1>
            </div>

            <div class="content">
                <h2>Welcome to P2P Manufacturing Platform!</h2>

                <p>Thank you for creating an account with us. To complete your registration and access the platform, please verify your email address.</p>

                <div class="info-box">
                    ⚠️ <strong>Important:</strong> You must verify your email before you can log in to the platform.
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{production_verify_url}" class="button">Verify My Email Address</a>
                </div>

                <div style="text-align: center; color: #666; font-size: 14px; margin-top: 20px;">
                    <p style="margin-bottom: 10px;">If the button doesn't work, copy and paste this link into your browser:</p>
                    <div style="background-color: #f8f9fa; padding: 12px; border-radius: 5px; margin: 10px auto; display: inline-block;">
                        <a href="{production_verify_url}" style="color: #667eea; text-decoration: none; font-family: monospace; font-size: 13px; word-break: break-all;">{production_verify_url}</a>
                    </div>
                </div>

                <div style="border-top: 1px solid #e5e7eb; margin-top: 30px; padding-top: 20px;">
                    <h3 style="color: #667eea; margin-bottom: 10px;">What's Next?</h3>
                    <p style="color: #666; font-size: 14px;">Once you verify your email, you'll be able to:</p>
                    <ul style="color: #666; font-size: 14px; padding-left: 20px;">
                        <li>Access your organization dashboard</li>
                        <li>Invite team members to join</li>
                        <li>Share and collaborate on use cases</li>
                        <li>Connect with manufacturing professionals</li>
                    </ul>
                </div>

                <div style="border-top: 1px solid #e5e7eb; margin-top: 30px; padding-top: 20px; text-align: center;">
                    <p style="color: #666; font-size: 13px; margin: 5px 0;">If you didn't create this account, please ignore this email.</p>
                    <p style="color: #888; font-size: 12px; margin: 10px 0; font-weight: 600;">⚠️ Do not reply - this is an automated message</p>
                    <p style="color: #999; font-size: 12px; margin-top: 10px;">© 2025 P2P Manufacturing Platform</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="🔐 Verify your email address - P2P Platform",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )

    await fm.send_message(message)


async def send_otp_email(
    email: str,
    code: str,
    purpose: str,  # 'signup_verify' | 'login_mfa'
) -> None:
    """
    Send a 6-digit OTP code to the user's email.

    In development mode, the code is ALWAYS printed to Docker/terminal logs
    with a visible banner (regardless of email settings). Email is only sent
    when settings.DEV_SEND_EMAILS is True or ENVIRONMENT != 'development'.

    Args:
        email: Recipient email address
        code: The plaintext 6-digit OTP code
        purpose: 'signup_verify' or 'login_mfa'
    """
    purpose_label = "Email Verification" if purpose == "signup_verify" else "Login"
    subject_emoji = "🔐"
    expires_text = f"This code expires in {settings.OTP_EXPIRY_MINUTES} minutes."

    if purpose == "signup_verify":
        header_title = "🎉 Welcome to P2P Platform!"
        body_intro = "<p>Welcome to P2P Manufacturing Platform! We're excited to have you on board.</p><p>Use the code below to verify your email address:</p>"
        extra_alert = ""
    else:
        header_title = "🔐 Login Verification Required"
        body_intro = "<p>A sign-in attempt was made to your account. Use the code below to complete login:</p>"
        extra_alert = """
                <div class="warning" style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 12px 16px; margin: 16px 0 0 0; font-size: 14px; border-radius: 0 6px 6px 0;">
                    ⚠️ <strong>Didn't request this code?</strong><br>
                    Someone may be trying to sign in to your account. If this wasn't you, please reset your password immediately.
                </div>
                """

    # ── Log OTP to terminal in development mode only ────────────────────────
    if settings.ENVIRONMENT == "development":
        print(f"\n{'='*70}")
        print(f"{subject_emoji} OTP CODE FOR: {email}")
        print(f"   Purpose : {purpose_label}")
        print(f"   Code    : {code}")
        print(f"   Expires : {settings.OTP_EXPIRY_MINUTES} minutes")
        print(f"{'='*70}\n")
    logger.info(f"OTP generated for {email} (purpose={purpose})")

    # ── Skip actual email send in local development/acceptance environments ──
    if settings.ENVIRONMENT in {"development", "test"} and not settings.DEV_SEND_EMAILS:
        logger.info("DEV_SEND_EMAILS is False — skipping email send in local environment.")
        return

    # ── Build HTML email ─────────────────────────────────────────────────────
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 600px;
                margin: 0 auto;
                padding: 0;
                background-color: #f5f5f5;
            }}
            .container {{
                background-color: white;
                border-radius: 10px;
                overflow: hidden;
                margin: 20px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 30px;
                text-align: center;
            }}
            .header h1 {{ margin: 0; font-size: 26px; font-weight: 600; }}
            .content {{ padding: 30px; }}
            .code-box {{
                background: linear-gradient(135deg, #f0f4ff 0%, #f5f0ff 100%);
                border: 2px solid #667eea;
                border-radius: 12px;
                padding: 16px;
                text-align: center;
                margin: 20px 0;
            }}
            .code {{
                font-size: 32px;
                font-weight: 800;
                letter-spacing: 8px;
                color: #667eea;
                font-family: 'Courier New', Courier, monospace;
            }}
            .code-label {{
                font-size: 13px;
                color: #888;
                margin-top: 8px;
            }}
            .warning {{
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
                padding: 12px 16px;
                margin: 16px 0;
                font-size: 14px;
                border-radius: 0 6px 6px 0;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 13px;
                background-color: #f8f9fa;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{header_title}</h1>
            </div>
            <div class="content">
                {body_intro}
                <div class="code-box">
                    <div class="code">{code}</div>
                    <div class="code-label">{expires_text} Do not share this code.</div>
                </div>
                <p style="color: #666; font-size: 14px;">
                    This code can only be used once and will expire in
                    <strong>{settings.OTP_EXPIRY_MINUTES} minutes</strong>.
                    You have a maximum of {settings.OTP_MAX_ATTEMPTS} attempts.
                </p>
                <div class="warning">
                    ⚠️ <strong>Security notice:</strong> We will never ask for this code by phone or chat.
                    If you did not request this code, ignore this email.
                </div>
                {extra_alert}
            </div>
            <div class="footer">
                <p style="font-weight: bold;">⚠️ Do not reply — this is an automated message</p>
                <p style="color: #999;">© 2025 P2P Manufacturing Platform</p>
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="🎉 Welcome! Verify Your Email — P2P Platform" if purpose == "signup_verify" else "🔐 Login Verification Required — P2P Platform",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )

    await fm.send_message(message)
    logger.info(f"OTP email sent to {email} (purpose={purpose})")
