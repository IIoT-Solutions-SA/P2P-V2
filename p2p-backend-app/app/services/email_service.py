"""
Email service for sending invitations and notifications
"""
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
from typing import List, Dict, Any
import os
from datetime import datetime

# TEST MODE: Override recipient email
TEST_MODE = False  # Set to True to redirect all emails to TEST_EMAIL
TEST_EMAIL = "hamzaferoze115+34@gmail.com"  # Using +34 suffix for test emails

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("MAIL_USERNAME", "p2p_c4ir@iiotsolutions.sa"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD", "mribowelxmoctfem"),  # Gmail App Password
    # MAIL_FROM=os.getenv("MAIL_FROM", "P2P Manufacturing Platform <noreply@p2p-manufacturing.com>"),  # Future: custom domain
    MAIL_FROM=os.getenv("MAIL_FROM", "P2P-C4IR <p2p_c4ir@iiotsolutions.sa>"),  # Using business Gmail
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)

fm = FastMail(conf)

async def send_invitation_email(
    recipient_email: str,
    recipient_name: str,
    invited_by_name: str,
    company_name: str,
    invite_link: str,
    expires_at: datetime
) -> None:
    """Send invitation email to new member"""
    
    # Override recipient in test mode
    actual_recipient = TEST_EMAIL if TEST_MODE else recipient_email
    
    # Calculate days until expiration
    days_until_expiry = (expires_at - datetime.utcnow()).days
    
    # HTML template with beautiful styling
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
            .benefits {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .benefits ul {{
                margin: 10px 0;
                padding-left: 20px;
            }}
            .benefits li {{
                margin: 8px 0;
            }}
            .footer {{
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 14px;
                background-color: #f8f9fa;
            }}
            .expires {{
                background-color: #e7f3ff;
                border-left: 4px solid #2196F3;
                padding: 10px;
                margin: 15px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 You're Invited to join {company_name}!</h1>
            </div>
            
            <div class="content">
                <h2>Hello {recipient_name or 'there'}!</h2>
                
                <p><strong>{invited_by_name}</strong> from <strong>{company_name}</strong> has invited you to join their organization on the P2P Manufacturing Platform as a team member.</p>
                
                <div class="benefits">
                    <h3>Join your team to:</h3>
                    <ul style="padding-left: 20px;">
                        <li>Connect with manufacturing professionals</li>
                        <li>Share and discover innovative solutions</li>
                        <li>Collaborate on industry challenges</li>
                    </ul>
                </div>
                
                <div class="expires">
                    ⏰ <strong>Important:</strong> This invitation expires in {days_until_expiry} days
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{invite_link}" class="button">Accept Invitation & Join Platform</a>
                </div>
                
                <div style="text-align: center; color: #666; font-size: 14px; margin-top: 20px;">
                    <p style="margin-bottom: 10px;">If the button doesn't work, copy and paste this link into your browser:</p>
                    <div style="background-color: #f8f9fa; padding: 12px; border-radius: 5px; margin: 10px auto; display: inline-block;">
                        <a href="{invite_link}" style="color: #667eea; text-decoration: none; font-family: monospace; font-size: 13px;">{invite_link}</a>
                    </div>
                </div>

                <div style="border-top: 1px solid #e5e7eb; margin-top: 30px; padding-top: 20px; text-align: center;">
                    <p style="color: #666; font-size: 13px; margin: 5px 0;">This invitation was sent by {invited_by_name} from {company_name}</p>
                    <p style="color: #666; font-size: 13px; margin: 5px 0;">If you didn't expect this invitation, please ignore this email.</p>
                    <p style="color: #888; font-size: 12px; margin: 10px 0; font-weight: 600;">⚠️ Do not reply - this is an automated message</p>
                    <p style="color: #999; font-size: 12px; margin-top: 10px;">© 2025 P2P Manufacturing Platform</p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    message = MessageSchema(
        subject=f"🎉 {invited_by_name} invited you to join {company_name} on P2P Platform",
        recipients=[actual_recipient],
        body=html,
        subtype=MessageType.html
    )
    
    await fm.send_message(message)

async def send_welcome_email(
    recipient_email: str,
    recipient_name: str,
    user_role: str
) -> None:
    """Send welcome email to newly registered user"""
    
    # Override recipient in test mode
    actual_recipient = TEST_EMAIL if TEST_MODE else recipient_email
    
    role_message = "an administrator" if user_role == "admin" else "a member"
    
    # HTML template
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
            .getting-started {{
                background-color: #f8f9fa;
                padding: 20px;
                border-radius: 5px;
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
                <h1>🎊 Welcome to P2P Manufacturing Platform!</h1>
            </div>
            
            <div class="content">
                <h2>Welcome aboard, {recipient_name}!</h2>
                
                <p>Your account has been successfully created as <strong>{role_message}</strong> on the P2P Manufacturing Platform.</p>
                
                
                <div class="getting-started">
                    <h3>🚀 Getting Started</h3>
                    <p>Here's what you can do next:</p>
                    <ul>
                        <li>Complete your profile with your expertise and interests</li>
                        <li>Browse existing use cases and solutions</li>
                        <li>Connect with other manufacturing professionals</li>
                        <li>Share your own innovations and experiences</li>
                        <li>Join discussions in the forums</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="http://localhost:5173/dashboard" class="button">Go to Dashboard</a>
                </div>
                
                <p>If you have any questions or need assistance, don't hesitate to reach out to our support team.</p>
            </div>
            
            <div class="footer">
                <p>Thank you for joining P2P Manufacturing Platform!</p>
                <p style="margin-top: 20px; font-weight: bold; color: #666;">⚠️ Please do not reply to this email. This is an automated message from an unmonitored inbox.</p>
                <p style="margin-top: 20px; color: #999;">© 2025 P2P Manufacturing Platform. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    message = MessageSchema(
        subject="Welcome to P2P Manufacturing Platform! 🎉",
        recipients=[actual_recipient],
        body=html,
        subtype=MessageType.html
    )
    
    await fm.send_message(message)