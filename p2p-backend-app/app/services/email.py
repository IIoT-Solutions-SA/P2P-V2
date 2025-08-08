"""Email service for sending invitations and notifications."""

import smtplib
from typing import Optional, Dict, Any, List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import asyncio
from jinja2 import Environment, FileSystemLoader, Template
import os
from pathlib import Path

from app.core.config import settings
from app.core.logging import get_logger
from app.models.invitation import UserInvitation
from app.models.organization import Organization
from app.models.user import User

logger = get_logger(__name__)


class EmailService:
    """Service for sending emails with support for invitations and notifications."""
    
    def __init__(self):
        self.smtp_server = settings.SMTP_SERVER
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.smtp_use_tls = settings.SMTP_USE_TLS
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME
        
        # Initialize Jinja2 template engine
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        if template_dir.exists():
            self.jinja_env = Environment(loader=FileSystemLoader(str(template_dir)))
        else:
            self.jinja_env = None
            logger.warning(f"Email templates directory not found: {template_dir}")
    
    def _create_smtp_connection(self) -> smtplib.SMTP:
        """Create SMTP connection."""
        if not self.smtp_server:
            raise ValueError("SMTP server not configured")
        
        if self.smtp_use_tls:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
        else:
            server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
        
        if self.smtp_username and self.smtp_password:
            server.login(self.smtp_username, self.smtp_password)
        
        return server
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send an email asynchronously."""
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{self.from_name} <{self.from_email}>"
            msg['To'] = to_email
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain', 'utf-8')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # Add attachments if any
            if attachments:
                for attachment in attachments:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(attachment['content'])
                    encoders.encode_base64(part)
                    part.add_header(
                        'Content-Disposition',
                        f'attachment; filename= {attachment["filename"]}'
                    )
                    msg.attach(part)
            
            # Send email in executor to avoid blocking
            def send_sync():
                try:
                    with self._create_smtp_connection() as server:
                        server.send_message(msg)
                    return True
                except Exception as e:
                    logger.error(f"Failed to send email to {to_email}: {str(e)}")
                    return False
            
            # Run in thread pool to avoid blocking async operations
            loop = asyncio.get_event_loop()
            success = await loop.run_in_executor(None, send_sync)
            
            if success:
                logger.info(f"Email sent successfully to {to_email}")
            else:
                logger.error(f"Failed to send email to {to_email}")
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending email to {to_email}: {str(e)}")
            return False
    
    def _render_template(
        self, 
        template_name: str, 
        context: Dict[str, Any]
    ) -> tuple[str, str]:
        """Render HTML and text email templates."""
        html_content = ""
        text_content = ""
        
        if self.jinja_env:
            try:
                # Try to load HTML template
                html_template = self.jinja_env.get_template(f"{template_name}.html")
                html_content = html_template.render(**context)
            except Exception as e:
                logger.warning(f"Could not load HTML template {template_name}.html: {e}")
            
            try:
                # Try to load text template
                text_template = self.jinja_env.get_template(f"{template_name}.txt")
                text_content = text_template.render(**context)
            except Exception as e:
                logger.warning(f"Could not load text template {template_name}.txt: {e}")
        
        # Fallback to simple template if Jinja2 templates not available
        if not html_content:
            html_content = self._get_fallback_template(template_name, context)
        
        return html_content, text_content
    
    def _get_fallback_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Get fallback HTML template when Jinja2 templates are not available."""
        if template_name == "invitation":
            return self._get_invitation_fallback_template(context)
        elif template_name == "welcome":
            return self._get_welcome_fallback_template(context)
        else:
            return f"""
            <html>
                <body>
                    <h1>Notification from {context.get('organization_name', 'P2P Sandbox')}</h1>
                    <p>{context.get('message', 'You have a new notification.')}</p>
                </body>
            </html>
            """
    
    def _get_invitation_fallback_template(self, context: Dict[str, Any]) -> str:
        """Fallback invitation email template."""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px;">
                    <h1 style="color: #333; text-align: center; margin-bottom: 30px;">
                        You're Invited to Join {context.get('organization_name', 'P2P Sandbox')}!
                    </h1>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #555;">
                        Hello {context.get('first_name', '')},
                    </p>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #555;">
                        <strong>{context.get('inviter_name', 'Someone')}</strong> has invited you to join 
                        <strong>{context.get('organization_name')}</strong> on P2P Sandbox.
                    </p>
                    
                    {f'<p style="font-size: 16px; line-height: 1.6; color: #555;"><em>"{context.get("personal_message")}"</em></p>' if context.get('personal_message') else ''}
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{context.get('invitation_url')}" 
                           style="background-color: #007bff; color: white; padding: 12px 30px; 
                                  text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold;">
                            Accept Invitation
                        </a>
                    </div>
                    
                    <div style="background-color: #e9ecef; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #333;">What's Next?</h3>
                        <ul style="color: #555;">
                            <li>Click the button above to accept your invitation</li>
                            <li>Create your account with a secure password</li>
                            <li>Complete your profile information</li>
                            <li>Start collaborating with your team!</li>
                        </ul>
                    </div>
                    
                    <p style="font-size: 14px; color: #666;">
                        This invitation will expire on <strong>{context.get('expires_at')}</strong>.
                        If you don't accept by then, you'll need to request a new invitation.
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #888; text-align: center;">
                        If you weren't expecting this invitation, you can safely ignore this email.
                        <br>
                        This invitation was sent to {context.get('email')}.
                    </p>
                </div>
            </body>
        </html>
        """
    
    def _get_welcome_fallback_template(self, context: Dict[str, Any]) -> str:
        """Fallback welcome email template."""
        return f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; padding: 30px; border-radius: 10px;">
                    <h1 style="color: #28a745; text-align: center; margin-bottom: 30px;">
                        Welcome to {context.get('organization_name', 'P2P Sandbox')}!
                    </h1>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #555;">
                        Hi {context.get('user_name', 'there')},
                    </p>
                    
                    <p style="font-size: 16px; line-height: 1.6; color: #555;">
                        Congratulations! You've successfully joined <strong>{context.get('organization_name')}</strong> 
                        on P2P Sandbox. You're now part of a collaborative platform designed to help 
                        Saudi Arabia's industrial SMEs share knowledge and grow together.
                    </p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{context.get('dashboard_url')}" 
                           style="background-color: #28a745; color: white; padding: 12px 30px; 
                                  text-decoration: none; border-radius: 5px; font-size: 16px; font-weight: bold;">
                            Go to Dashboard
                        </a>
                    </div>
                    
                    <div style="background-color: #e7f3ff; padding: 15px; border-radius: 5px; margin: 20px 0;">
                        <h3 style="margin-top: 0; color: #333;">Get Started:</h3>
                        <ul style="color: #555;">
                            <li>Complete your profile with photo and professional details</li>
                            <li>Explore the forum to see what others are discussing</li>
                            <li>Share your first use case or ask a question</li>
                            <li>Connect with colleagues in your organization</li>
                        </ul>
                    </div>
                    
                    <p style="font-size: 14px; color: #666;">
                        If you have any questions, don't hesitate to reach out to your administrator 
                        or explore our help section.
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 30px 0;">
                    
                    <p style="font-size: 12px; color: #888; text-align: center;">
                        You're receiving this because you joined {context.get('organization_name')}.
                        <br>
                        P2P Sandbox - Empowering Saudi Industrial SMEs
                    </p>
                </div>
            </body>
        </html>
        """
    
    async def send_invitation_email(
        self,
        invitation: UserInvitation,
        organization: Organization,
        inviter: User,
        invitation_url: str
    ) -> bool:
        """Send invitation email."""
        context = {
            "email": invitation.email,
            "first_name": invitation.first_name or "there",
            "last_name": invitation.last_name or "",
            "organization_name": organization.name,
            "inviter_name": inviter.full_name,
            "invitation_url": invitation_url,
            "expires_at": invitation.expires_at.strftime("%B %d, %Y"),
            "personal_message": invitation.personal_message,
            "role": invitation.invited_role.value.title()
        }
        
        html_content, text_content = self._render_template("invitation", context)
        
        subject = f"You're invited to join {organization.name} on P2P Sandbox"
        
        return await self.send_email(
            to_email=invitation.email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_welcome_email(
        self,
        user: User,
        organization: Organization
    ) -> bool:
        """Send welcome email to new user."""
        context = {
            "user_name": user.full_name,
            "organization_name": organization.name,
            "dashboard_url": f"{settings.FRONTEND_URL}/dashboard"
        }
        
        html_content, text_content = self._render_template("welcome", context)
        
        subject = f"Welcome to {organization.name} on P2P Sandbox!"
        
        return await self.send_email(
            to_email=user.email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )
    
    async def send_notification_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        notification_id: Optional[str] = None
    ) -> bool:
        """Send notification email."""
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="background-color: #f8f9fa; padding: 20px; border-radius: 10px;">
                    <h2 style="color: #333; margin-bottom: 20px;">{subject}</h2>
                    <p style="font-size: 16px; line-height: 1.6; color: #555;">{body}</p>
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="font-size: 12px; color: #888; text-align: center;">
                        P2P Sandbox - Empowering Saudi Industrial SMEs
                    </p>
                </div>
            </body>
        </html>
        """
        
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=body
        )
    
    def is_configured(self) -> bool:
        """Check if email service is properly configured."""
        return bool(
            self.smtp_server and 
            self.from_email and 
            (not self.smtp_username or self.smtp_password)  # Password required only if username provided
        )


# Create singleton instance
email_service = EmailService()


# Mock email service for development
class MockEmailService:
    """Mock email service for development and testing."""
    
    def __init__(self):
        self.sent_emails = []
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Mock send email - just log the email."""
        email_data = {
            "to_email": to_email,
            "subject": subject,
            "html_content": html_content,
            "text_content": text_content,
            "attachments": attachments,
            "sent_at": asyncio.get_event_loop().time()
        }
        
        self.sent_emails.append(email_data)
        
        logger.info(f"[MOCK EMAIL] To: {to_email} | Subject: {subject}")
        logger.debug(f"[MOCK EMAIL] Content preview: {html_content[:200]}...")
        
        return True
    
    async def send_invitation_email(
        self,
        invitation: UserInvitation,
        organization: Organization,
        inviter: User,
        invitation_url: str
    ) -> bool:
        """Mock send invitation email."""
        subject = f"You're invited to join {organization.name} on P2P Sandbox"
        content = f"Invitation for {invitation.email} to join {organization.name}"
        
        return await self.send_email(
            to_email=invitation.email,
            subject=subject,
            html_content=content
        )
    
    async def send_welcome_email(
        self,
        user: User,
        organization: Organization
    ) -> bool:
        """Mock send welcome email."""
        subject = f"Welcome to {organization.name} on P2P Sandbox!"
        content = f"Welcome {user.full_name} to {organization.name}"
        
        return await self.send_email(
            to_email=user.email,
            subject=subject,
            html_content=content
        )
    
    async def send_notification_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        notification_id: Optional[str] = None
    ) -> bool:
        """Mock send notification email."""
        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=body
        )
    
    def is_configured(self) -> bool:
        """Mock is always configured."""
        return True
    
    def get_sent_emails(self) -> List[Dict[str, Any]]:
        """Get all sent emails for testing."""
        return self.sent_emails.copy()
    
    def clear_sent_emails(self) -> None:
        """Clear sent emails list."""
        self.sent_emails.clear()


# Use mock email service if real email is not configured
if not email_service.is_configured():
    logger.info("Email service not configured, using mock email service")
    email_service = MockEmailService()