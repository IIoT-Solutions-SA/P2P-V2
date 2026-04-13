"""
Email verification service for sending verification emails
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

    # Log localhost URL to terminal
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
