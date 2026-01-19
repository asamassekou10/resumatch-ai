"""
Email service module for sending AI analysis results to users
Uses Resend API for email delivery
"""
import os
import logging
from typing import Optional, List
import base64
from io import BytesIO
from itsdangerous import URLSafeTimedSerializer, BadSignature

# Configure logging first
logger = logging.getLogger(__name__)

# Try importing resend - Resend 2.x uses module-level API
RESEND_AVAILABLE = False
_resend_module = None

def _check_resend_availability():
    """Check if Resend package is available and import it"""
    global RESEND_AVAILABLE, _resend_module
    try:
        # Resend 2.x uses: import resend; resend.api_key = "..."; resend.Emails.send(...)
        import resend
        
        # Verify that Emails class exists
        if not hasattr(resend, 'Emails'):
            raise ImportError("Resend.Emails not found in resend module")
        
        _resend_module = resend
        RESEND_AVAILABLE = True
        logger.info("Resend package successfully imported")
        return True
    except ImportError as e:
        RESEND_AVAILABLE = False
        _resend_module = None
        logger.warning(f"Resend package not available: {e}")
        return False
    except Exception as e:
        RESEND_AVAILABLE = False
        _resend_module = None
        logger.error(f"Unexpected error importing Resend: {e}")
        return False

# Initial check
_check_resend_availability()

class EmailService:
    def __init__(self):
        self.resend_api_key = os.getenv('RESEND_API_KEY')
        # Use professional sender identity
        self.from_email = 'Resume Analyzer AI <support@resumeanalyzerai.com>'
        self.reply_to = 'support@resumeanalyzerai.com'
        self.unsubscribe_secret = os.getenv('UNSUBSCRIBE_SECRET', os.getenv('SECRET_KEY', 'dev-unsubscribe-secret'))
        
        # Re-check Resend availability in case package was installed after module load
        _check_resend_availability()
        
        if self.resend_api_key and RESEND_AVAILABLE and _resend_module:
            try:
                # Resend 2.x: Set API key at module level
                _resend_module.api_key = self.resend_api_key
                self.resend = _resend_module  # Store reference to module for convenience
                logger.info("Resend email service initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Resend: {e}")
                self.resend = None
        else:
            self.resend = None
            if not RESEND_AVAILABLE:
                logger.warning("Resend package not installed. Email functionality will be disabled.")
            elif not self.resend_api_key:
                logger.warning("Resend API key not found. Email functionality will be disabled.")

    @staticmethod
    def _apply_unsubscribe_footer(html_content: str, unsubscribe_link: str = None) -> str:
        """Append unsubscribe footer if link provided"""
        if not unsubscribe_link:
            return html_content
        footer = f"""
        <div style="text-align: center; padding: 16px; color: #94a3b8; font-size: 12px;">
            Prefer fewer emails? <a href="{unsubscribe_link}" style="color: #6366f1;">Unsubscribe</a>
        </div>
        """
        if '</body>' in html_content:
            return html_content.replace('</body>', f'{footer}</body>')
        return html_content + footer

    def send_analysis_results(
        self, 
        recipient_email: str, 
        recipient_name: str,
        analysis_data: dict,
        attachments: Optional[List[dict]] = None,
        unsubscribe_link: str = None
    ) -> bool:
        """
        Send AI analysis results to user's email
        
        Args:
            recipient_email: User's email address
            recipient_name: User's name
            analysis_data: Dictionary containing analysis results
            attachments: Optional list of attachment dictionaries with 'content', 'filename', 'type'
            unsubscribe_link: Optional unsubscribe link to add to email footer
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.resend:
            if not self.resend_api_key:
                logger.error("Resend API key not configured. Set RESEND_API_KEY environment variable.")
            elif not RESEND_AVAILABLE:
                logger.error("Resend package not installed. Run: pip install resend")
            else:
                logger.error("Resend not configured. Cannot send email.")
            return False

        try:
            # Create email content
            subject = f"Your AI Resume Analysis Results - {analysis_data.get('job_title', 'Position')}"
            
            # Generate HTML email content
            html_content = self._generate_analysis_email_html(recipient_name, analysis_data)
            
            # Add unsubscribe footer if link provided
            html_content = self._apply_unsubscribe_footer(html_content, unsubscribe_link)
            
            # Prepare email params
            email_params = {
                "from": self.from_email,
                "to": [recipient_email],
                "subject": subject,
                "html": html_content,
                "reply_to": self.reply_to
            }
            
            # Add attachments if provided
            if attachments:
                email_attachments = []
                for attachment in attachments:
                    if all(key in attachment for key in ['content', 'filename', 'type']):
                        email_attachments.append({
                            "filename": attachment['filename'],
                            "content": base64.b64encode(attachment['content']).decode('utf-8')
                        })
                if email_attachments:
                    email_params["attachments"] = email_attachments
            
            # Send email using Resend 2.x API
            response = self.resend.Emails.send(email_params)
            
            # Resend returns a dict with 'id' key on success, or raises an exception on error
            if response and isinstance(response, dict) and 'id' in response:
                logger.info(f"Email sent successfully to {recipient_email} (ID: {response.get('id')})")
                return True
            else:
                logger.error(f"Failed to send email. Response: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email to {recipient_email}: {str(e)}")
            return False

    def send_cover_letter(
        self,
        recipient_email: str,
        recipient_name: str,
        cover_letter: str,
        job_title: str,
        company_name: str,
        unsubscribe_link: str = None
    ) -> bool:
        """Send generated cover letter to user"""
        if not self.resend:
            if not self.resend_api_key:
                logger.error("Resend API key not configured. Set RESEND_API_KEY environment variable.")
            elif not RESEND_AVAILABLE:
                logger.error("Resend package not installed. Run: pip install resend")
            else:
                logger.error("Resend not configured. Cannot send email.")
            return False

        try:
            subject = f"Your AI-Generated Cover Letter - {job_title} at {company_name}"
            
            html_content = self._generate_cover_letter_email_html(
                recipient_name, cover_letter, job_title, company_name
            )
            
            html_content = self._apply_unsubscribe_footer(html_content, unsubscribe_link)

            response = self.resend.Emails.send({
                "from": self.from_email,
                "to": [recipient_email],
                "subject": subject,
                "html": html_content,
                "reply_to": self.reply_to
            })
            
            if response and isinstance(response, dict) and 'id' in response:
                logger.info(f"Cover letter email sent successfully to {recipient_email} (ID: {response.get('id')})")
                return True
            else:
                logger.error(f"Failed to send cover letter email. Response: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending cover letter email to {recipient_email}: {str(e)}")
            return False

    def send_verification_email(self, recipient_email: str, recipient_name: str, verification_link: str) -> bool:
        """Send email verification link to new user"""
        if not self.resend:
            if not self.resend_api_key:
                logger.error("Resend API key not configured. Set RESEND_API_KEY environment variable.")
            elif not RESEND_AVAILABLE:
                logger.error("Resend package not installed. Run: pip install resend")
            else:
                logger.error("Resend not configured. Cannot send email.")
            return False

        try:
            subject = "Welcome to ResumeAnalyzer AI - Verify Your Email"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Verify Your Email</title>
                <style>
                    body {{ 
                        font-family: Arial, sans-serif; 
                        line-height: 1.6; 
                        color: #333;
                        margin: 0;
                        padding: 0;
                        background-color: #f4f4f4;
                    }}
                    .container {{ 
                        max-width: 600px; 
                        margin: 20px auto; 
                        background: white;
                        border-radius: 8px;
                        overflow: hidden;
                        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                    }}
                    .header {{ 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white; 
                        padding: 40px 20px; 
                        text-align: center;
                    }}
                    .header h1 {{
                        margin: 0 0 10px 0;
                        font-size: 28px;
                    }}
                    .content {{ 
                        padding: 40px 30px;
                    }}
                    .welcome-text {{
                        font-size: 18px;
                        color: #333;
                        margin-bottom: 20px;
                    }}
                    .cta-button {{
                        display: inline-block;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white !important;
                        padding: 16px 40px;
                        text-decoration: none;
                        border-radius: 25px;
                        font-weight: bold;
                        font-size: 16px;
                        margin: 30px 0;
                        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                    }}
                    .cta-container {{
                        text-align: center;
                        margin: 30px 0;
                    }}
                    .info-box {{
                        background: #f8f9fa;
                        padding: 20px;
                        border-radius: 8px;
                        margin: 20px 0;
                        border-left: 4px solid #667eea;
                    }}
                    .footer {{ 
                        text-align: center; 
                        padding: 20px;
                        background: #f8f9fa;
                        color: #6c757d; 
                        font-size: 13px;
                        border-top: 1px solid #dee2e6;
                    }}
                    .link-text {{
                        word-break: break-all;
                        color: #667eea;
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to ResumeAnalyzer AI!</h1>
                        <p style="margin: 0; opacity: 0.9;">Your AI-Powered Career Assistant</p>
                    </div>
                    
                    <div class="content">
                        <p class="welcome-text">Hi {recipient_name},</p>
                        
                        <p>Thank you for signing up! We're excited to help you optimize your resume and land your dream job.</p>
                        
                        <p><strong>To get started, please verify your email address by clicking the button below:</strong></p>
                        
                        <div class="cta-container">
                            <a href="{verification_link}" class="cta-button">
                                Verify Email Address
                            </a>
                        </div>
                        
                        <div class="info-box">
                            <p style="margin: 0 0 10px 0;"><strong>What you'll get:</strong></p>
                            <ul style="margin: 0; padding-left: 20px;">
                                <li>AI-powered resume analysis</li>
                                <li>Keyword optimization for ATS systems</li>
                                <li>Personalized improvement suggestions</li>
                                <li>Cover letter generation</li>
                                <li>Resume optimization tools</li>
                            </ul>
                        </div>
                        
                        <p style="margin-top: 30px; font-size: 14px; color: #666;">
                            If the button doesn't work, copy and paste this link into your browser:
                        </p>
                        <p class="link-text">{verification_link}</p>
                        
                        <p style="margin-top: 30px; font-size: 14px; color: #666;">
                            This link will expire in 24 hours. If you didn't create an account, you can safely ignore this email.
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p><strong>ResumeAnalyzer AI</strong></p>
                        <p>This is an automated message, please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            logger.info(f"Attempting to send verification email to {recipient_email}")
            logger.debug(f"Resend client initialized: {self.resend is not None}, API key present: {bool(self.resend_api_key)}")
            
            response = self.resend.Emails.send({
                "from": self.from_email,
                "to": [recipient_email],
                "subject": subject,
                "html": html_content,
                "reply_to": self.reply_to
            })
            
            logger.debug(f"Resend API response: {response}, type: {type(response)}")
            
            # Resend can return different response formats
            if response:
                # Check if it's a dict with 'id' (success)
                if isinstance(response, dict):
                    if 'id' in response:
                        logger.info(f"Verification email sent successfully to {recipient_email} (ID: {response.get('id')})")
                        return True
                    elif 'error' in response:
                        logger.error(f"Resend API error: {response.get('error')}")
                        return False
                    else:
                        # Some versions return response object with .id attribute
                        email_id = getattr(response, 'id', None)
                        if email_id:
                            logger.info(f"Verification email sent successfully to {recipient_email} (ID: {email_id})")
                            return True
                
                # Check if it's an object with id attribute
                email_id = getattr(response, 'id', None)
                if email_id:
                    logger.info(f"Verification email sent successfully to {recipient_email} (ID: {email_id})")
                    return True
            
            logger.error(f"Failed to send verification email. Unexpected response format: {response} (type: {type(response)})")
            return False
                
        except Exception as e:
            error_type = type(e).__name__
            error_msg = str(e)
            logger.error(f"Exception sending verification email to {recipient_email}: {error_type}: {error_msg}", exc_info=True)
            
            # Check for specific Resend errors
            if 'domain' in error_msg.lower() or 'unauthorized' in error_msg.lower():
                logger.error("Resend API key may be invalid or domain not verified in Resend dashboard")
            elif 'rate limit' in error_msg.lower():
                logger.error("Resend rate limit exceeded")
            
            return False


    def send_optimized_resume(
        self,
        recipient_email: str,
        recipient_name: str,
        optimized_resume: str,
        job_title: str,
        attachments: Optional[List[dict]] = None
    ) -> bool:
        """Send optimized resume to user"""
        if not self.resend:
            if not self.resend_api_key:
                logger.error("Resend API key not configured. Set RESEND_API_KEY environment variable.")
            elif not RESEND_AVAILABLE:
                logger.error("Resend package not installed. Run: pip install resend")
            else:
                logger.error("Resend not configured. Cannot send email.")
            return False

        try:
            subject = f"Your AI-Optimized Resume - {job_title}"
            
            html_content = self._generate_optimized_resume_email_html(
                recipient_name, optimized_resume, job_title
            )
            
            email_params = {
                "from": self.from_email,
                "to": [recipient_email],
                "subject": subject,
                "html": html_content,
                "reply_to": self.reply_to
            }
            
            # Add attachments if provided
            if attachments:
                email_attachments = []
                for attachment in attachments:
                    if all(key in attachment for key in ['content', 'filename', 'type']):
                        email_attachments.append({
                            "filename": attachment['filename'],
                            "content": base64.b64encode(attachment['content']).decode('utf-8')
                        })
                if email_attachments:
                    email_params["attachments"] = email_attachments
            
            response = self.resend.Emails.send(email_params)
            
            if response and isinstance(response, dict) and 'id' in response:
                logger.info(f"Optimized resume email sent successfully to {recipient_email} (ID: {response.get('id')})")
                return True
            else:
                logger.error(f"Failed to send optimized resume email. Response: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending optimized resume email to {recipient_email}: {str(e)}")
            return False
            
    def _generate_cover_letter_email_html(self, recipient_name: str, cover_letter: str, job_title: str, company_name: str) -> str:
        """Generate HTML content for cover letter email"""
        website_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI-Generated Cover Letter</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    line-height: 1.6; 
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 20px auto; 
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; 
                    padding: 30px 20px; 
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0 0 10px 0;
                    font-size: 24px;
                }}
                .content {{ 
                    padding: 30px 20px;
                }}
                .cover-letter {{ 
                    background: #f8f9fa; 
                    padding: 20px; 
                    border-radius: 8px; 
                    white-space: pre-line;
                    border-left: 4px solid #667eea;
                    line-height: 1.8;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white !important;
                    padding: 15px 40px;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: bold;
                    font-size: 16px;
                    margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
                }}
                .cta-container {{
                    text-align: center;
                    margin: 30px 0;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 8px;
                }}
                .footer {{ 
                    text-align: center; 
                    padding: 20px;
                    background: #f8f9fa;
                    color: #6c757d; 
                    font-size: 13px;
                    border-top: 1px solid #dee2e6;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Your AI-Generated Cover Letter</h1>
                    <p>Tailored for {job_title} at {company_name}</p>
                </div>
                
                <div class="content">
                    <div class="cover-letter">
                        {cover_letter}
                    </div>
                    
                    <div class="cta-container">
                        <p style="margin-bottom: 15px; color: #333;">
                            <strong>Explore more AI-powered career tools</strong>
                        </p>
                        <a href="{website_url}/dashboard" class="cta-button">
                            Go to Dashboard
                        </a>
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>ResumeAnalyzer AI</strong></p>
                    <p>Remember to review and personalize before sending</p>
                    <p style="margin-top: 10px;">
                        <a href="{website_url}" style="color: #667eea; text-decoration: none;">Visit Website</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return html
        
    def _generate_optimized_resume_email_html(self, recipient_name: str, optimized_resume: str, job_title: str) -> str:
        """Generate HTML content for optimized resume email"""
        website_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI-Optimized Resume</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    line-height: 1.6; 
                    color: #333;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{ 
                    max-width: 600px; 
                    margin: 20px auto;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                .header {{ 
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white; 
                    padding: 30px 20px; 
                    text-align: center;
                }}
                .header h1 {{
                    margin: 0 0 10px 0;
                    font-size: 24px;
                }}
                .content {{ 
                    padding: 30px 20px;
                }}
                .resume {{ 
                    background: #f8f9fa; 
                    padding: 20px; 
                    border-radius: 8px; 
                    white-space: pre-line;
                    border-left: 4px solid #10b981;
                    line-height: 1.8;
                }}
                .cta-button {{
                    display: inline-block;
                    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
                    color: white !important;
                    padding: 15px 40px;
                    text-decoration: none;
                    border-radius: 25px;
                    font-weight: bold;
                    font-size: 16px;
                    margin: 20px 0;
                    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4);
                }}
                .cta-container {{
                    text-align: center;
                    margin: 30px 0;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 8px;
                }}
                .footer {{ 
                    text-align: center; 
                    padding: 20px;
                    background: #f8f9fa;
                    color: #6c757d; 
                    font-size: 13px;
                    border-top: 1px solid #dee2e6;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Your AI-Optimized Resume</h1>
                    <p>Enhanced for {job_title}</p>
                </div>
                
                <div class="content">
                    <div class="resume">
                        {optimized_resume}
                    </div>
                    
                    <div class="cta-container">
                        <p style="margin-bottom: 15px; color: #333;">
                            <strong>Get more career insights and tools</strong>
                        </p>
                        <a href="{website_url}/dashboard" class="cta-button">
                            Go to Dashboard
                        </a>
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>ResumeAnalyzer AI</strong></p>
                    <p>Review and format according to your preferences</p>
                    <p style="margin-top: 10px;">
                        <a href="{website_url}" style="color: #10b981; text-decoration: none;">Visit Website</a>
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        return html

    def _generate_analysis_email_html(self, recipient_name: str, analysis_data: dict) -> str:
        """Generate HTML content for analysis results email"""
        match_score = analysis_data.get('match_score', 0)
        job_title = analysis_data.get('job_title', 'Position')
        company_name = analysis_data.get('company_name', 'Company')
        analysis_id = analysis_data.get('analysis_id', '')
        
        # Color coding for match score
        score_color = "#10B981" if match_score >= 70 else "#F59E0B" if match_score >= 50 else "#EF4444"
        score_text_color = "#ffffff" # White text for better contrast on colored backgrounds
        
        # Website URL
        website_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        dashboard_url = f"{website_url}/dashboard" if analysis_id else website_url
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Your AI Resume Analysis Results</title>
            <style>
                body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f8fafc; }}
                .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; }}
                .header {{ background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%); color: white; padding: 40px 20px; text-align: center; }}
                .header h1 {{ margin: 0 0 10px 0; font-size: 28px; font-weight: 700; }}
                .header p {{ margin: 0; opacity: 0.9; font-size: 16px; }}
                .content {{ padding: 30px 25px; }}
                .score-card {{ text-align: center; margin: 20px 0; padding: 25px; background-color: #f1f5f9; border-radius: 10px; }}
                .score-label {{ font-size: 16px; color: #64748b; font-weight: 500; margin-bottom: 10px; }}
                .score-value {{ font-size: 64px; font-weight: 800; color: {score_color}; line-height: 1; }}
                .section {{ margin: 30px 0; }}
                .section h3 {{ margin-top: 0; margin-bottom: 15px; color: #1e293b; font-size: 20px; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; }}
                .keywords-grid {{ display: flex; flex-wrap: wrap; gap: 8px; }}
                .keyword {{ padding: 6px 14px; border-radius: 20px; font-size: 14px; font-weight: 500; }}
                .found {{ background-color: #dcfce7; color: #166534; border: 1px solid #bbf7d0; }}
                .missing {{ background-color: #ffedd5; color: #9a3412; border: 1px solid #fed7aa; }}
                .suggestions-box {{ background: #f8fafc; border: 1px solid #e2e8f0; padding: 20px; border-radius: 8px; border-left: 4px solid #4f46e5; }}
                .suggestions-box p {{ margin: 0; color: #334155; }}
                .cta-section {{ margin: 40px 0; padding: 25px; background-color: #4f46e5; color: white; border-radius: 10px; text-align: center; }}
                .cta-section h3 {{ margin-top: 0; margin-bottom: 10px; font-size: 22px; }}
                .cta-section p {{ margin: 0 0 20px 0; opacity: 0.9; }}
                .cta-button {{ display: inline-block; background: #ffffff; color: #4f46e5 !important; padding: 14px 30px; text-decoration: none; border-radius: 8px; font-weight: 700; font-size: 16px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }}
                .footer {{ text-align: center; padding: 25px; color: #94a3b8; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Your AI Resume Analysis is Ready</h1>
                    <p>Analysis for: <strong>{job_title}</strong></p>
                </div>
                
                <div class="content">
                    <div class="score-card">
                        <div class="score-label">Resume Match Score</div>
                        <div class="score-value">{match_score}%</div>
                    </div>
                    
                    <div class="section">
                        <h3>Keyword Analysis</h3>
                        <p style="color: #475569; margin-bottom: 20px;">Your resume was scanned for crucial keywords from the job description. Here's how you stack up:</p>
                        
                        <strong><span style="color: #16a34a;">Keywords Found ({len(analysis_data.get('keywords_found', []))}):</span></strong>
                        <div class="keywords-grid" style="margin-top: 10px; margin-bottom: 20px;">
                            {self._format_keywords_grid(analysis_data.get('keywords_found', []), 'found')}
                        </div>

                        <strong><span style="color: #d97706;">Missing Keywords ({len(analysis_data.get('keywords_missing', []))}):</span></strong>
                        <div class="keywords-grid" style="margin-top: 10px;">
                            {self._format_keywords_grid(analysis_data.get('keywords_missing', []), 'missing')}
                        </div>
                    </div>
                    
                    <div class="section">
                        <h3>AI-Powered Suggestions</h3>
                        <div class="suggestions-box">
                            <p>{analysis_data.get('suggestions', 'No specific suggestions available.')}</p>
                        </div>
                    </div>

                    <div class="cta-section">
                        <h3>Take the Next Step to Get Hired</h3>
                        <p>Your analysis is a great start. Now, let our AI do the hard work for you. Unlock premium tools to land your dream job.</p>
                        <a href="{dashboard_url}" class="cta-button">
                            Upgrade to Pro
                        </a>
                        <ul style="text-align: left; margin-top: 20px; padding-left: 20px; font-size: 14px; opacity: 0.9;">
                            <li><strong>Get Personalized Feedback:</strong> Detailed, line-by-line advice on how to improve.</li>
                            <li><strong>Optimize Your Resume:</strong> Let AI rewrite sections to include missing keywords naturally.</li>
                            <li><strong>Generate a Cover Letter:</strong> Create a compelling, tailored cover letter in seconds.</li>
                        </ul>
                    </div>
                </div>
                
                <div class="footer">
                    <p>ResumeAnalyzer AI &copy; 2025</p>
                </div>
            </div>
        </body>
        </html>
        """
        return html


    def _format_keywords(self, keywords: List[str], keyword_type: str) -> str:
        """Format keywords for HTML display with better wrapping"""
        if not keywords:
            return f"<span class='keyword {keyword_type}'>None found</span>"
        
        # Limit to 20 keywords to avoid overwhelming the email
        display_keywords = keywords[:20]
        keyword_html = ""
        
        for keyword in display_keywords:
            # Truncate very long keywords
            display_keyword = keyword if len(keyword) <= 30 else keyword[:27] + "..."
            keyword_html += f"<span class='keyword {keyword_type}'>{display_keyword}</span>"
        
        if len(keywords) > 20:
            remaining = len(keywords) - 20
            keyword_html += f"<span class='keyword {keyword_type}' style='font-weight: bold;'>+{remaining} more</span>"
        
        return keyword_html

    def _format_keywords_grid(self, keywords: List[str], keyword_type: str) -> str:
        """Format keywords in a grid layout with 5 keywords per line"""
        if not keywords:
            return f"<div class='keyword {keyword_type}'>None found</div>"
        
        # Limit to 20 keywords
        display_keywords = keywords[:20]
        keyword_html = ""
        
        for i, keyword in enumerate(display_keywords):
            # Truncate very long keywords
            display_keyword = keyword if len(keyword) <= 25 else keyword[:22] + "..."
            keyword_html += f"<div class='keyword {keyword_type}'>{display_keyword}</div>"
            
            # Add line break after every 5 keywords (but not after the last one)
            if (i + 1) % 5 == 0 and (i + 1) < len(display_keywords):
                keyword_html += "<div style='width: 100%; height: 0;'></div>"
        
        if len(keywords) > 20:
            remaining = len(keywords) - 20
            keyword_html += f"<div class='keyword' style='background-color: #e2e8f0; color: #475569;'>+{remaining} more</div>"
        
        return keyword_html

    def send_welcome_email(self, recipient_email: str, recipient_name: str, verification_required: bool = False, unsubscribe_link: str = None) -> bool:
        """Send welcome email to new user"""
        if not self.resend:
            logger.warning("Resend not configured. Cannot send welcome email.")
            return False

        try:
            subject = "Welcome to ResumeAnalyzer AI! 🎉"
            website_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            
            verification_section = ""
            if verification_required:
                verification_section = """
                <div class="info-box" style="background: #f0f9ff; border-left: 4px solid #3b82f6; padding: 20px; margin: 20px 0; border-radius: 8px;">
                    <p style="margin: 0 0 10px 0; font-weight: 600; color: #1e40af;">📧 Verify Your Email</p>
                    <p style="margin: 0; color: #1e3a8a;">Please check your inbox for a verification email to activate your account.</p>
                </div>
                """
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Welcome to ResumeAnalyzer AI</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f8fafc; }}
                    .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }}
                    .header h1 {{ margin: 0 0 10px 0; font-size: 28px; font-weight: 700; }}
                    .content {{ padding: 40px 30px; }}
                    .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white !important; padding: 16px 40px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 16px; margin: 30px 0; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }}
                    .cta-container {{ text-align: center; margin: 30px 0; }}
                    .footer {{ text-align: center; padding: 25px; color: #94a3b8; font-size: 12px; background: #f8fafc; border-top: 1px solid #e2e8f0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome to ResumeAnalyzer AI!</h1>
                        <p style="margin: 0; opacity: 0.9;">Your AI-Powered Career Assistant</p>
                    </div>
                    <div class="content">
                        <p style="font-size: 18px; color: #333; margin-bottom: 20px;">Hi {recipient_name},</p>
                        <p>Thank you for joining ResumeAnalyzer AI! We're thrilled to have you on board and excited to help you optimize your resume and land your dream job.</p>
                        {verification_section}
                        <p><strong>What you can do with ResumeAnalyzer AI:</strong></p>
                        <ul style="color: #475569; line-height: 1.8;">
                            <li>Get AI-powered resume analysis and scoring</li>
                            <li>Discover missing keywords from job descriptions</li>
                            <li>Receive personalized improvement suggestions</li>
                            <li>Generate professional cover letters</li>
                            <li>Optimize your resume for ATS systems</li>
                        </ul>
                        <div class="cta-container">
                            <a href="{website_url}/dashboard" class="cta-button">Get Started</a>
                        </div>
                    </div>
                    <div class="footer">
                        <p><strong>ResumeAnalyzer AI</strong></p>
                        <p>This is an automated message, please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_content = self._apply_unsubscribe_footer(html_content, unsubscribe_link)

            response = self.resend.Emails.send({
                "from": self.from_email,
                "to": [recipient_email],
                "subject": subject,
                "html": html_content,
                "reply_to": self.reply_to
            })
            
            if response and isinstance(response, dict) and 'id' in response:
                logger.info(f"Welcome email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send welcome email. Response: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending welcome email to {recipient_email}: {str(e)}")
            return False

    def send_trial_activation_email(self, recipient_email: str, recipient_name: str, trial_end_date, unsubscribe_link: str = None) -> bool:
        """Send trial activation email with features and benefits"""
        if not self.resend:
            logger.warning("Resend not configured. Cannot send trial activation email.")
            return False

        try:
            subject = "🎁 Your 7-Day Free Trial is Active - Start Standing Out!"
            website_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            trial_end_str = trial_end_date.strftime('%B %d, %Y') if hasattr(trial_end_date, 'strftime') else str(trial_end_date)
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Your Free Trial is Active</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f8fafc; }}
                    .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
                    .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 40px 20px; text-align: center; }}
                    .header h1 {{ margin: 0 0 10px 0; font-size: 28px; font-weight: 700; }}
                    .content {{ padding: 40px 30px; }}
                    .trial-badge {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 15px 30px; border-radius: 25px; display: inline-block; font-weight: bold; margin: 20px 0; }}
                    .feature-box {{ background: #f0fdf4; border-left: 4px solid #10b981; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                    .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white !important; padding: 16px 40px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 16px; margin: 30px 0; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }}
                    .cta-container {{ text-align: center; margin: 30px 0; }}
                    .footer {{ text-align: center; padding: 25px; color: #94a3b8; font-size: 12px; background: #f8fafc; border-top: 1px solid #e2e8f0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Your Free Trial is Active!</h1>
                        <p style="margin: 0; opacity: 0.9;">100 Credits • Pro Features • No Credit Card Required</p>
                    </div>
                    <div class="content">
                        <p style="font-size: 18px; color: #333; margin-bottom: 20px;">Hi {recipient_name},</p>
                        <p>Great news! Your <strong>7-day free trial</strong> with Pro tier benefits is now active. You have full access to all premium features until <strong>{trial_end_str}</strong>.</p>
                        
                        <div style="text-align: center;">
                            <div class="trial-badge">100 Credits Available</div>
                        </div>
                        
                        <div class="feature-box">
                            <h3 style="margin-top: 0; color: #059669;">🚀 How You'll Stand Out in the Job Market</h3>
                            <p style="margin-bottom: 15px;"><strong>With ResumeAnalyzer AI, you'll:</strong></p>
                            <ul style="color: #166534; line-height: 1.8; margin: 0;">
                                <li><strong>Beat ATS Systems:</strong> Optimize your resume to pass Applicant Tracking Systems that reject 75% of resumes</li>
                                <li><strong>Match Job Descriptions:</strong> Get instant feedback on keyword gaps and how to improve your match score</li>
                                <li><strong>Save Time:</strong> Generate tailored cover letters in seconds instead of hours</li>
                                <li><strong>Get Hired Faster:</strong> Our users see 3x more interview callbacks after optimizing their resumes</li>
                            </ul>
                        </div>
                        
                        <h3 style="color: #1e293b; margin-top: 30px;">✨ Pro Features You Now Have Access To:</h3>
                        <ul style="color: #475569; line-height: 1.8;">
                            <li><strong>Unlimited Resume Analyses:</strong> Analyze your resume against any job description</li>
                            <li><strong>AI-Powered Insights:</strong> Get detailed, personalized feedback on how to improve</li>
                            <li><strong>Cover Letter Generation:</strong> Create professional, tailored cover letters instantly</li>
                            <li><strong>Resume Optimization:</strong> Let AI enhance your resume with missing keywords naturally</li>
                            <li><strong>ATS Compatibility Checks:</strong> Ensure your resume format works with ATS systems</li>
                            <li><strong>Score Breakdown:</strong> Understand exactly how your resume is scored</li>
                        </ul>
                        
                        <div class="cta-container">
                            <a href="{website_url}/analyze" class="cta-button">Start Analyzing Your Resume</a>
                        </div>
                        
                        <p style="color: #64748b; font-size: 14px; margin-top: 30px; text-align: center;">
                            <strong>No credit card required.</strong> Your trial ends on {trial_end_str}. Upgrade anytime to keep your Pro benefits!
                        </p>
                    </div>
                    <div class="footer">
                        <p><strong>ResumeAnalyzer AI</strong></p>
                        <p>Questions? Reply to this email or visit our help center.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            response = self.resend.Emails.send({
                "from": self.from_email,
                "to": [recipient_email],
                "subject": subject,
                "html": html_content,
                "reply_to": self.reply_to
            })
            
            if response and isinstance(response, dict) and 'id' in response:
                logger.info(f"Trial activation email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send trial activation email. Response: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending trial activation email to {recipient_email}: {str(e)}")
            return False

    def send_followup_email(self, recipient_email: str, recipient_name: str, feedback_link: str = None, unsubscribe_link: str = None) -> bool:
        """Send 2-day follow-up email with feedback option"""
        if not self.resend:
            logger.warning("Resend not configured. Cannot send follow-up email.")
            return False

        try:
            subject = "How's your trial going? We'd love your feedback! 💬"
            website_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            if not feedback_link:
                feedback_link = f"{website_url}/help?feedback=true"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>How's Your Trial Going?</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f8fafc; }}
                    .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
                    .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 40px 20px; text-align: center; }}
                    .header h1 {{ margin: 0 0 10px 0; font-size: 28px; font-weight: 700; }}
                    .content {{ padding: 40px 30px; }}
                    .tip-box {{ background: #fffbeb; border-left: 4px solid #f59e0b; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                    .feedback-button {{ display: inline-block; background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white !important; padding: 14px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 16px; margin: 20px 0; }}
                    .cta-container {{ text-align: center; margin: 30px 0; }}
                    .footer {{ text-align: center; padding: 25px; color: #94a3b8; font-size: 12px; background: #f8fafc; border-top: 1px solid #e2e8f0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>How's It Going? 👋</h1>
                        <p style="margin: 0; opacity: 0.9;">We'd Love to Hear From You</p>
                    </div>
                    <div class="content">
                        <p style="font-size: 18px; color: #333; margin-bottom: 20px;">Hi {recipient_name},</p>
                        <p>You've been using ResumeAnalyzer AI for a couple of days now. We hope you're finding it helpful in optimizing your resume!</p>
                        
                        <div class="tip-box">
                            <h3 style="margin-top: 0; color: #92400e;">💡 Tips to Get the Most Out of Your Trial</h3>
                            <ul style="color: #78350f; line-height: 1.8; margin: 0;">
                                <li>Analyze your resume against multiple job descriptions to see different perspectives</li>
                                <li>Use the AI feedback feature to get detailed improvement suggestions</li>
                                <li>Generate cover letters tailored to each job application</li>
                                <li>Check your ATS compatibility score to ensure your resume passes screening</li>
                            </ul>
                        </div>
                        
                        <p><strong>We'd love to hear about your experience!</strong> Your feedback helps us improve and helps other job seekers too.</p>
                        
                        <div class="cta-container">
                            <a href="{feedback_link}" class="feedback-button">Share Your Feedback</a>
                        </div>
                        
                        <p style="color: #64748b; font-size: 14px; text-align: center; margin-top: 30px;">
                            <strong>Success Story:</strong> "I used ResumeAnalyzer AI before applying to 10 jobs. Got 8 interviews! The keyword optimization made all the difference." - Sarah M., Software Engineer
                        </p>
                    </div>
                    <div class="footer">
                        <p><strong>ResumeAnalyzer AI</strong></p>
                        <p>Questions? We're here to help - just reply to this email!</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_content = self._apply_unsubscribe_footer(html_content, unsubscribe_link)

            response = self.resend.Emails.send({
                "from": self.from_email,
                "to": [recipient_email],
                "subject": subject,
                "html": html_content,
                "reply_to": self.reply_to
            })
            
            if response and isinstance(response, dict) and 'id' in response:
                logger.info(f"Follow-up email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send follow-up email. Response: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending follow-up email to {recipient_email}: {str(e)}")
            return False

    def send_reengagement_email(self, recipient_email: str, recipient_name: str, days_inactive: int = None, unsubscribe_link: str = None) -> bool:
        """Send re-engagement email to inactive users"""
        if not self.resend:
            logger.warning("Resend not configured. Cannot send re-engagement email.")
            return False

        try:
            website_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            subject = "We Miss You at ResumeAnalyzer AI – Let's Get You Back on Track"
            inactivity_text = f"It’s been {days_inactive} days" if days_inactive else "It's been a little while"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>We Miss You</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #0f172a; margin: 0; padding: 0; background-color: #f8fafc; }}
                    .container {{ max-width: 620px; margin: 24px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 8px 24px rgba(15, 23, 42, 0.08); }}
                    .header {{ background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%); color: white; padding: 36px 28px; text-align: center; }}
                    .header h1 {{ margin: 0 0 10px 0; font-size: 26px; font-weight: 800; }}
                    .content {{ padding: 36px 32px; }}
                    .card {{ background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px 20px; margin: 16px 0; }}
                    .cta-button {{ display: inline-block; background: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%); color: white !important; padding: 14px 28px; text-decoration: none; border-radius: 9999px; font-weight: 700; font-size: 16px; margin: 22px 0; box-shadow: 0 10px 20px rgba(99, 102, 241, 0.25); }}
                    .cta-container {{ text-align: center; margin: 30px 0; }}
                    .footer {{ text-align: center; padding: 24px; color: #94a3b8; font-size: 12px; background: #f8fafc; border-top: 1px solid #e2e8f0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Welcome Back, {recipient_name} 👋</h1>
                        <p style="margin: 0; opacity: 0.92;">{inactivity_text} since your last visit. Here’s what’s new.</p>
                    </div>
                    <div class="content">
                        <p style="font-size: 17px; color: #0f172a;">We’ve shipped a lot of improvements to help you land interviews faster:</p>
                        <div class="card">
                            <h3 style="margin: 0 0 8px 0; color: #0ea5e9;">AI Resume Rewrite</h3>
                            <p style="margin: 0; color: #334155;">Rewrite bullet points with missing keywords while keeping your voice.</p>
                        </div>
                        <div class="card">
                            <h3 style="margin: 0 0 8px 0; color: #0ea5e9;">Weekly Check-ins</h3>
                            <p style="margin: 0; color: #334155;">Stay on track with a quick weekly plan tailored to your target roles.</p>
                        </div>
                        <div class="card">
                            <h3 style="margin: 0 0 8px 0; color: #0ea5e9;">Cover Letter Generator</h3>
                            <p style="margin: 0; color: #334155;">Create tailored cover letters in seconds for your top applications.</p>
                        </div>

                        <div class="cta-container">
                            <a href="{website_url}/analyze" class="cta-button">Run an Analysis</a>
                        </div>
                    </div>
                    <div class="footer">
                        <p><strong>ResumeAnalyzer AI</strong></p>
                        <p>Need help? Reply and we’ll assist.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            html_content = self._apply_unsubscribe_footer(html_content, unsubscribe_link)

            response = self.resend.Emails.send({
                "from": self.from_email,
                "to": [recipient_email],
                "subject": subject,
                "html": html_content,
                "reply_to": self.reply_to
            })

            if response and isinstance(response, dict) and 'id' in response:
                logger.info(f"Re-engagement email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send re-engagement email. Response: {response}")
                return False

        except Exception as e:
            logger.error(f"Error sending re-engagement email to {recipient_email}: {str(e)}")
            return False

    # -----------------------
    # Unsubscribe management
    # -----------------------
    def _get_unsubscribe_serializer(self):
        return URLSafeTimedSerializer(self.unsubscribe_secret, salt='unsubscribe-email')

    def generate_unsubscribe_token(self, user_id: int) -> str:
        try:
            serializer = self._get_unsubscribe_serializer()
            return serializer.dumps({'user_id': user_id})
        except Exception as e:
            logger.error(f"Failed to generate unsubscribe token: {e}")
            return None

    def verify_unsubscribe_token(self, token: str, max_age: int = 60 * 60 * 24 * 30):
        try:
            serializer = self._get_unsubscribe_serializer()
            data = serializer.loads(token, max_age=max_age)
            return data.get('user_id')
        except BadSignature:
            logger.warning("Invalid unsubscribe token signature")
            return None
        except Exception as e:
            logger.error(f"Failed to verify unsubscribe token: {e}")
            return None

    def send_weekly_checkin_email(self, recipient_email: str, recipient_name: str, days_remaining: int = None, unsubscribe_link: str = None) -> bool:
        """Send weekly check-in email for engagement"""
        if not self.resend:
            logger.warning("Resend not configured. Cannot send weekly check-in email.")
            return False

        try:
            days_text = f"{days_remaining} days" if days_remaining else "time"
            subject = f"Your Weekly Check-in: Make the Most of Your Trial ⚡"
            website_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            
            days_remaining_section = ""
            if days_remaining and days_remaining > 0:
                days_remaining_section = f"""
                <div style="background: #fef3c7; border-left: 4px solid #f59e0b; padding: 15px; margin: 20px 0; border-radius: 8px; text-align: center;">
                    <p style="margin: 0; color: #92400e; font-weight: 600;">⏰ {days_remaining} days left in your trial</p>
                </div>
                """
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Weekly Check-in</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f8fafc; }}
                    .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
                    .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px 20px; text-align: center; }}
                    .header h1 {{ margin: 0 0 10px 0; font-size: 28px; font-weight: 700; }}
                    .content {{ padding: 40px 30px; }}
                    .feature-spotlight {{ background: #f0f4ff; border-left: 4px solid #667eea; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                    .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white !important; padding: 14px 30px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 16px; margin: 20px 0; }}
                    .cta-container {{ text-align: center; margin: 30px 0; }}
                    .footer {{ text-align: center; padding: 25px; color: #94a3b8; font-size: 12px; background: #f8fafc; border-top: 1px solid #e2e8f0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Weekly Check-in 📊</h1>
                        <p style="margin: 0; opacity: 0.9;">Keep Your Job Search Momentum Going</p>
                    </div>
                    <div class="content">
                        <p style="font-size: 18px; color: #333; margin-bottom: 20px;">Hi {recipient_name},</p>
                        <p>Hope you're making great progress with your job search! Here's your weekly check-in to help you stay on track.</p>
                        {days_remaining_section}
                        <div class="feature-spotlight">
                            <h3 style="margin-top: 0; color: #4c1d95;">✨ This Week's Feature Spotlight</h3>
                            <p style="color: #5b21b6; margin-bottom: 10px;"><strong>AI-Powered Resume Optimization:</strong></p>
                            <p style="color: #6b21a8; margin: 0;">Did you know you can get AI to rewrite sections of your resume? Our optimization feature naturally incorporates missing keywords while maintaining your unique voice. Try it on your next analysis!</p>
                        </div>
                        
                        <h3 style="color: #1e293b;">💼 Engagement Tips</h3>
                        <ul style="color: #475569; line-height: 1.8;">
                            <li>Analyze your resume against 3-5 different job descriptions to see patterns</li>
                            <li>Use the cover letter generator for your top job applications</li>
                            <li>Review your score breakdown to understand what's working</li>
                            <li>Optimize your resume based on AI feedback before applying</li>
                        </ul>
                        
                        <div class="cta-container">
                            <a href="{website_url}/analyze" class="cta-button">Run Another Analysis</a>
                        </div>
                    </div>
                    <div class="footer">
                        <p><strong>ResumeAnalyzer AI</strong></p>
                        <p>Keep up the great work! 🚀</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_content = self._apply_unsubscribe_footer(html_content, unsubscribe_link)

            response = self.resend.Emails.send({
                "from": self.from_email,
                "to": [recipient_email],
                "subject": subject,
                "html": html_content,
                "reply_to": self.reply_to
            })
            
            if response and isinstance(response, dict) and 'id' in response:
                logger.info(f"Weekly check-in email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send weekly check-in email. Response: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending weekly check-in email to {recipient_email}: {str(e)}")
            return False

    def send_trial_expiry_email(self, recipient_email: str, recipient_name: str, trial_end_date, unsubscribe_link: str = None) -> bool:
        """Send trial expiry email on expiration day"""
        if not self.resend:
            logger.warning("Resend not configured. Cannot send trial expiry email.")
            return False

        try:
            subject = "⏰ Your Free Trial Ends Today - Don't Lose Your Pro Benefits!"
            website_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            pricing_url = f"{website_url}/pricing"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Trial Ending Today</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f8fafc; }}
                    .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
                    .header {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; padding: 40px 20px; text-align: center; }}
                    .header h1 {{ margin: 0 0 10px 0; font-size: 28px; font-weight: 700; }}
                    .content {{ padding: 40px 30px; }}
                    .warning-box {{ background: #fef2f2; border-left: 4px solid #ef4444; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                    .benefits-box {{ background: #f0fdf4; border-left: 4px solid #10b981; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                    .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white !important; padding: 16px 40px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 16px; margin: 30px 0; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }}
                    .cta-container {{ text-align: center; margin: 30px 0; }}
                    .footer {{ text-align: center; padding: 25px; color: #94a3b8; font-size: 12px; background: #f8fafc; border-top: 1px solid #e2e8f0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>⏰ Your Trial Ends Today</h1>
                        <p style="margin: 0; opacity: 0.9;">Don't Lose Your Pro Benefits</p>
                    </div>
                    <div class="content">
                        <p style="font-size: 18px; color: #333; margin-bottom: 20px;">Hi {recipient_name},</p>
                        <p>Your 7-day free trial ends today. You have a <strong>3-day grace period</strong> to upgrade and keep all your Pro features.</p>
                        
                        <div class="warning-box">
                            <h3 style="margin-top: 0; color: #991b1b;">What You'll Lose:</h3>
                            <ul style="color: #7f1d1d; line-height: 1.8; margin: 0;">
                                <li>Unlimited resume analyses (downgrade to 5 credits)</li>
                                <li>AI-powered feedback and insights</li>
                                <li>Cover letter generation</li>
                                <li>Resume optimization features</li>
                                <li>Detailed score breakdowns</li>
                            </ul>
                        </div>
                        
                        <div class="benefits-box">
                            <h3 style="margin-top: 0; color: #065f46;">What You'll Keep by Upgrading:</h3>
                            <ul style="color: #047857; line-height: 1.8; margin: 0;">
                                <li><strong>100 credits/month</strong> for unlimited analyses</li>
                                <li>All Pro features you've been using</li>
                                <li>Priority support</li>
                                <li>Regular feature updates</li>
                            </ul>
                        </div>
                        
                        <div class="cta-container">
                            <a href="{pricing_url}" class="cta-button">Upgrade to Pro Now</a>
                        </div>
                        
                        <p style="color: #64748b; font-size: 14px; text-align: center; margin-top: 30px;">
                            <strong>Grace Period:</strong> You have 3 more days to upgrade before your account is downgraded to the free tier.
                        </p>
                    </div>
                    <div class="footer">
                        <p><strong>ResumeAnalyzer AI</strong></p>
                        <p>Questions about upgrading? Reply to this email - we're here to help!</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_content = self._apply_unsubscribe_footer(html_content, unsubscribe_link)

            response = self.resend.Emails.send({
                "from": self.from_email,
                "to": [recipient_email],
                "subject": subject,
                "html": html_content,
                "reply_to": self.reply_to
            })
            
            if response and isinstance(response, dict) and 'id' in response:
                logger.info(f"Trial expiry email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send trial expiry email. Response: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending trial expiry email to {recipient_email}: {str(e)}")
            return False

    def send_trial_expired_email(self, recipient_email: str, recipient_name: str, unsubscribe_link: str = None) -> bool:
        """Send final email after trial expired (3 days after expiry)"""
        if not self.resend:
            logger.warning("Resend not configured. Cannot send trial expired email.")
            return False

        try:
            subject = "Final Opportunity: Upgrade Before Your Account is Downgraded"
            website_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
            pricing_url = f"{website_url}/pricing"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Final Upgrade Opportunity</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f8fafc; }}
                    .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }}
                    .header {{ background: linear-gradient(135deg, #64748b 0%, #475569 100%); color: white; padding: 40px 20px; text-align: center; }}
                    .header h1 {{ margin: 0 0 10px 0; font-size: 28px; font-weight: 700; }}
                    .content {{ padding: 40px 30px; }}
                    .info-box {{ background: #f1f5f9; border-left: 4px solid #64748b; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                    .free-tier-box {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 20px; margin: 20px 0; border-radius: 8px; }}
                    .cta-button {{ display: inline-block; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white !important; padding: 16px 40px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 16px; margin: 30px 0; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }}
                    .cta-container {{ text-align: center; margin: 30px 0; }}
                    .footer {{ text-align: center; padding: 25px; color: #94a3b8; font-size: 12px; background: #f8fafc; border-top: 1px solid #e2e8f0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Last Chance to Upgrade</h1>
                        <p style="margin: 0; opacity: 0.9;">Your Account Will Be Downgraded Soon</p>
                    </div>
                    <div class="content">
                        <p style="font-size: 18px; color: #333; margin-bottom: 20px;">Hi {recipient_name},</p>
                        <p>Your grace period is ending. This is your <strong>final opportunity</strong> to upgrade and keep your Pro benefits.</p>
                        
                        <div class="info-box">
                            <h3 style="margin-top: 0; color: #334155;">What Happens Next:</h3>
                            <p style="color: #475569; margin: 0;">If you don't upgrade, your account will be automatically downgraded to the free tier with 5 credits. You'll lose access to all Pro features.</p>
                        </div>
                        
                        <div class="free-tier-box">
                            <h3 style="margin-top: 0; color: #92400e;">Free Tier Includes:</h3>
                            <ul style="color: #78350f; line-height: 1.8; margin: 0;">
                                <li>5 credits (enough for 5 analyses)</li>
                                <li>Basic resume analysis</li>
                                <li>Keyword matching</li>
                            </ul>
                            <p style="color: #92400e; margin-top: 10px; margin-bottom: 0;"><strong>You'll lose:</strong> AI feedback, cover letters, resume optimization, and unlimited analyses.</p>
                        </div>
                        
                        <div class="cta-container">
                            <a href="{pricing_url}" class="cta-button">Upgrade Now - Keep Pro Benefits</a>
                        </div>
                        
                        <p style="color: #64748b; font-size: 14px; text-align: center; margin-top: 30px;">
                            Thank you for trying ResumeAnalyzer AI! We hope you found it helpful. You can always upgrade later from your dashboard.
                        </p>
                    </div>
                    <div class="footer">
                        <p><strong>ResumeAnalyzer AI</strong></p>
                        <p>We're here if you have any questions - just reply to this email!</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            html_content = self._apply_unsubscribe_footer(html_content, unsubscribe_link)

            response = self.resend.Emails.send({
                "from": self.from_email,
                "to": [recipient_email],
                "subject": subject,
                "html": html_content,
                "reply_to": self.reply_to
            })
            
            if response and isinstance(response, dict) and 'id' in response:
                logger.info(f"Trial expired email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send trial expired email. Response: {response}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending trial expired email to {recipient_email}: {str(e)}")
            return False

    def send_feature_announcement_email(self, recipient_email: str, recipient_name: str, unsubscribe_link: str = None) -> bool:
        """
        Send feature announcement email about new features:
        1. URL Job Description Fetching
        2. Application Tracking
        3. Download Optimized Resume with Templates
        """
        if not self.resend:
            logger.warning("Resend not configured. Cannot send feature announcement email.")
            return False

        try:
            subject = "🚀 New Features: Smart JD Import, Application Tracker & PDF Templates!"
            website_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>New Features Announcement</title>
                <style>
                    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.6; color: #0f172a; margin: 0; padding: 0; background-color: #f8fafc; }}
                    .container {{ max-width: 620px; margin: 24px auto; background: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 8px 30px rgba(15, 23, 42, 0.1); }}
                    .header {{ background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #a855f7 100%); color: white; padding: 48px 28px; text-align: center; }}
                    .header h1 {{ margin: 0 0 12px 0; font-size: 28px; font-weight: 800; }}
                    .header p {{ margin: 0; opacity: 0.95; font-size: 16px; }}
                    .content {{ padding: 40px 32px; }}
                    .intro {{ font-size: 17px; color: #334155; margin-bottom: 32px; }}
                    .feature-card {{ background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border: 1px solid #e2e8f0; border-radius: 12px; padding: 24px; margin: 20px 0; position: relative; overflow: hidden; }}
                    .feature-card::before {{ content: ''; position: absolute; top: 0; left: 0; width: 4px; height: 100%; }}
                    .feature-1::before {{ background: linear-gradient(180deg, #3b82f6, #1d4ed8); }}
                    .feature-2::before {{ background: linear-gradient(180deg, #10b981, #059669); }}
                    .feature-3::before {{ background: linear-gradient(180deg, #f59e0b, #d97706); }}
                    .feature-icon {{ font-size: 32px; margin-bottom: 12px; }}
                    .feature-title {{ font-size: 18px; font-weight: 700; color: #1e293b; margin: 0 0 8px 0; }}
                    .feature-desc {{ color: #475569; margin: 0; font-size: 15px; line-height: 1.7; }}
                    .feature-benefits {{ margin-top: 12px; padding-left: 20px; }}
                    .feature-benefits li {{ color: #64748b; font-size: 14px; margin: 6px 0; }}
                    .cta-section {{ text-align: center; margin: 40px 0 20px 0; padding: 32px; background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); border-radius: 12px; }}
                    .cta-section h3 {{ color: white; margin: 0 0 12px 0; font-size: 22px; font-weight: 700; }}
                    .cta-section p {{ color: rgba(255,255,255,0.9); margin: 0 0 24px 0; font-size: 15px; }}
                    .cta-button {{ display: inline-block; background: #ffffff; color: #6366f1 !important; padding: 16px 40px; text-decoration: none; border-radius: 50px; font-weight: 700; font-size: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.15); transition: transform 0.2s; }}
                    .cta-button:hover {{ transform: translateY(-2px); }}
                    .footer {{ text-align: center; padding: 28px; color: #94a3b8; font-size: 13px; background: #f8fafc; border-top: 1px solid #e2e8f0; }}
                    .footer a {{ color: #6366f1; text-decoration: none; }}
                    .badge {{ display: inline-block; background: #dbeafe; color: #1d4ed8; padding: 4px 12px; border-radius: 20px; font-size: 12px; font-weight: 600; margin-bottom: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <p style="margin-bottom: 8px; font-size: 14px; opacity: 0.9;">✨ Product Update</p>
                        <h1>3 Powerful New Features Just Dropped!</h1>
                        <p>Making your job search faster and easier than ever</p>
                    </div>

                    <div class="content">
                        <p class="intro">Hi {recipient_name},</p>
                        <p class="intro">We've been working hard to make ResumeAnalyzer AI even better for your job search. Here's what's new:</p>

                        <!-- Feature 1: URL JD Fetching -->
                        <div class="feature-card feature-1">
                            <div class="feature-icon">🔗</div>
                            <span class="badge">Time Saver</span>
                            <h3 class="feature-title">Smart Job Description Import</h3>
                            <p class="feature-desc">No more copy-pasting! Simply paste a job posting URL and we'll automatically extract the job description for you. Works with LinkedIn, Indeed, Glassdoor, and most job boards.</p>
                            <ul class="feature-benefits">
                                <li>Paste any job URL to auto-import the description</li>
                                <li>Works with 50+ job boards worldwide</li>
                                <li>Saves 2-3 minutes per analysis</li>
                            </ul>
                        </div>

                        <!-- Feature 2: Application Tracking -->
                        <div class="feature-card feature-2">
                            <div class="feature-icon">📊</div>
                            <span class="badge" style="background: #d1fae5; color: #059669;">Stay Organized</span>
                            <h3 class="feature-title">Application Tracker</h3>
                            <p class="feature-desc">Keep track of all your job applications in one place! After each analysis, you can add the job to your application tracker with status updates, notes, and follow-up reminders.</p>
                            <ul class="feature-benefits">
                                <li>Track application status: Applied, Interview, Offer, etc.</li>
                                <li>Add notes and follow-up dates</li>
                                <li>Never lose track of where you applied</li>
                            </ul>
                        </div>

                        <!-- Feature 3: PDF Download with Templates -->
                        <div class="feature-card feature-3">
                            <div class="feature-icon">📄</div>
                            <span class="badge" style="background: #fef3c7; color: #d97706;">Professional Output</span>
                            <h3 class="feature-title">Download Optimized Resume as PDF</h3>
                            <p class="feature-desc">Transform your AI-optimized resume into a beautifully formatted PDF! Choose from our professional templates designed to pass ATS systems while looking great to human recruiters.</p>
                            <ul class="feature-benefits">
                                <li><strong>Modern Template:</strong> Clean, contemporary design for tech & creative roles</li>
                                <li><strong>Classic Template:</strong> Traditional format with 100% ATS compatibility</li>
                                <li>Edit your details before downloading</li>
                                <li>PDF text is fully selectable for ATS parsing</li>
                            </ul>
                        </div>

                        <div class="cta-section">
                            <h3>Ready to Try These Features?</h3>
                            <p>Log in now and supercharge your job search!</p>
                            <a href="{website_url}/dashboard" class="cta-button">Go to Dashboard</a>
                        </div>

                        <p style="color: #64748b; font-size: 14px; text-align: center; margin-top: 24px;">
                            Have questions or feedback? Just reply to this email – we read every message!
                        </p>
                    </div>

                    <div class="footer">
                        <p><strong>ResumeAnalyzer AI</strong></p>
                        <p>Helping you land your dream job, one resume at a time.</p>
                        <p style="margin-top: 12px;">
                            <a href="{website_url}">Visit Website</a> &nbsp;|&nbsp;
                            <a href="{website_url}/dashboard">Dashboard</a>
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """

            html_content = self._apply_unsubscribe_footer(html_content, unsubscribe_link)

            response = self.resend.Emails.send({
                "from": self.from_email,
                "to": [recipient_email],
                "subject": subject,
                "html": html_content,
                "reply_to": self.reply_to
            })

            if response and isinstance(response, dict) and 'id' in response:
                logger.info(f"Feature announcement email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send feature announcement email. Response: {response}")
                return False

        except Exception as e:
            logger.error(f"Error sending feature announcement email to {recipient_email}: {str(e)}")
            return False


# Global email service instance
email_service = EmailService()
