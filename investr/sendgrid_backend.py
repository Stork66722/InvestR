"""
Custom email backend using SendGrid Web API instead of SMTP.
This avoids port 587 which is blocked on Render free tier.
"""
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content
from django.core.mail.backends.base import BaseEmailBackend


class SendGridBackend(BaseEmailBackend):
    """
    Email backend that uses SendGrid's Web API instead of SMTP.
    Supports both HTML and plain text emails.
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.api_key = os.getenv('SENDGRID_API_KEY') or os.getenv('EMAIL_HOST_PASSWORD')
        self.default_from = os.getenv('DEFAULT_FROM_EMAIL', 'investr.sim.noreply@gmail.com')
        
    def send_messages(self, email_messages):
        """
        Send one or more EmailMessage objects and return the number sent.
        """
        if not email_messages:
            return 0
            
        if not self.api_key:
            raise ValueError("SendGrid API key not configured")
            
        num_sent = 0
        sg = SendGridAPIClient(self.api_key)
        
        for message in email_messages:
            try:
                # Build SendGrid message
                from_email = Email(message.from_email or self.default_from)
                to_emails = [To(email) for email in message.to]
                subject = message.subject
                
                # Handle multipart messages (HTML + plain text)
                if hasattr(message, 'alternatives') and message.alternatives:
                    # Has HTML alternative
                    plain_content = Content("text/plain", message.body)
                    html_content = Content("text/html", message.alternatives[0][0])
                    mail = Mail(from_email, to_emails[0], subject, plain_content, html_content)
                elif message.content_subtype == 'html':
                    # HTML only
                    content = Content("text/html", message.body)
                    mail = Mail(from_email, to_emails[0], subject, content)
                else:
                    # Plain text only
                    content = Content("text/plain", message.body)
                    mail = Mail(from_email, to_emails[0], subject, content)
                
                # Add additional recipients
                if len(to_emails) > 1:
                    for to_email in to_emails[1:]:
                        mail.add_to(to_email)
                
                # Send via Web API
                response = sg.send(mail)
                
                if response.status_code in [200, 201, 202]:
                    num_sent += 1
                    
            except Exception as e:
                if not self.fail_silently:
                    raise
                    
        return num_sent