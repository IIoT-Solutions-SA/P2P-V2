"""
Email service for sending password reset emails
"""
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from typing import Dict, Any
from app.core.config import settings

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

async def send_password_reset_email(
    email: str,
    password_reset_url: str
) -> None:
    """
    Send password reset link to user

    Args:
        email: User's email address
        password_reset_url: Full URL for password reset (with token)
    """

    # Extract token from the URL
    import re
    from urllib.parse import urlparse, parse_qs
    parsed_url = urlparse(password_reset_url)
    query_params = parse_qs(parsed_url.query)
    token = query_params.get('token', [''])[0]
    tenant_id = query_params.get('tenantId', ['public'])[0]

    # Production URL for email (from central config)
    production_reset_url = f"{settings.PRODUCTION_URL}/reset-password?token={token}&tenantId={tenant_id}"

    # Localhost URL for terminal logs
    localhost_reset_url = f"http://localhost:5173/reset-password?token={token}&tenantId={tenant_id}"

    # Log localhost URL to terminal
    print(f"\n{'='*80}")
    print(f"🔐 PASSWORD RESET EMAIL SENT TO: {email}")
    print(f"🔗 Localhost reset link (for dev testing):")
    print(f"   {localhost_reset_url}")
    print(f"{'='*80}\n")

    # HTML template matching email verification style
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
                background-color: #fff3cd;
                border-left: 4px solid #ffc107;
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
                <h1>🔐 Reset Your Password</h1>
            </div>

            <div class="content">
                <h2>Password Reset Request</h2>

                <p>We received a request to reset your password for your P2P Manufacturing Platform account.</p>

                <div class="info-box">
                    ⏰ <strong>Important:</strong> This password reset link will expire in 1 hour for security reasons.
                </div>

                <div style="text-align: center; margin: 30px 0;">
                    <a href="{production_reset_url}" class="button">Reset My Password</a>
                </div>

                <div style="text-align: center; color: #666; font-size: 14px; margin-top: 20px;">
                    <p style="margin-bottom: 10px;">If the button doesn't work, copy and paste this link into your browser:</p>
                    <div style="background-color: #f8f9fa; padding: 12px; border-radius: 5px; margin: 10px auto; display: inline-block;">
                        <a href="{production_reset_url}" style="color: #667eea; text-decoration: none; font-family: monospace; font-size: 13px; word-break: break-all;">{production_reset_url}</a>
                    </div>
                </div>

                <div style="border-top: 1px solid #e5e7eb; margin-top: 30px; padding-top: 20px;">
                    <h3 style="color: #667eea; margin-bottom: 10px;">Security Tips</h3>
                    <ul style="color: #666; font-size: 14px; padding-left: 20px;">
                        <li>Choose a strong, unique password</li>
                        <li>Use a combination of letters, numbers, and symbols</li>
                        <li>Avoid using common words or personal information</li>
                        <li>Don't reuse passwords from other accounts</li>
                    </ul>
                </div>

                <div style="border-top: 1px solid #e5e7eb; margin-top: 30px; padding-top: 20px; text-align: center;">
                    <p style="color: #666; font-size: 13px; margin: 5px 0;">If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
                    <p style="color: #888; font-size: 12px; margin: 10px 0; font-weight: 600;">⚠️ Do not reply - this is an automated message</p>
                    <p style="color: #999; font-size: 12px; margin-top: 10px;">© 2025 P2P Manufacturing Platform</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """

    message = MessageSchema(
        subject="🔐 Reset your password - P2P Platform",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )

    await fm.send_message(message)
