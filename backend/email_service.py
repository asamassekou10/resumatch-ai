"""
Email service module for sending AI analysis results to users
"""
import os
import logging
from typing import Optional, List
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
from io import BytesIO

# Configure logging
logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@resumatch-ai.com')
        
        if self.sendgrid_api_key:
            self.sg = SendGridAPIClient(api_key=self.sendgrid_api_key)
        else:
            self.sg = None
            logger.warning("SendGrid API key not found. Email functionality will be disabled.")

    def send_analysis_results(
        self, 
        recipient_email: str, 
        recipient_name: str,
        analysis_data: dict,
        attachments: Optional[List[dict]] = None
    ) -> bool:
        """
        Send AI analysis results to user's email
        
        Args:
            recipient_email: User's email address
            recipient_name: User's name
            analysis_data: Dictionary containing analysis results
            attachments: Optional list of attachment dictionaries with 'content', 'filename', 'type'
        
        Returns:
            bool: True if email sent successfully, False otherwise
        """
        if not self.sg:
            logger.error("SendGrid not configured. Cannot send email.")
            return False

        try:
            # Create email content
            subject = f"Your AI Resume Analysis Results - {analysis_data.get('job_title', 'Position')}"
            
            # Generate HTML email content
            html_content = self._generate_analysis_email_html(recipient_name, analysis_data)
            
            # Create email message
            message = Mail(
                from_email=self.from_email,
                to_emails=recipient_email,
                subject=subject,
                html_content=html_content
            )
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    if all(key in attachment for key in ['content', 'filename', 'type']):
                        file_content = base64.b64encode(attachment['content']).decode()
                        attached_file = Attachment(
                            FileContent(file_content),
                            FileName(attachment['filename']),
                            FileType(attachment['type']),
                            Disposition('attachment')
                        )
                        message.attachment = attached_file
            
            # Send email
            response = self.sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send email. Status code: {response.status_code}")
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
        company_name: str
    ) -> bool:
        """Send generated cover letter to user"""
        if not self.sg:
            logger.error("SendGrid not configured. Cannot send email.")
            return False

        try:
            subject = f"Your AI-Generated Cover Letter - {job_title} at {company_name}"
            
            html_content = self._generate_cover_letter_email_html(
                recipient_name, cover_letter, job_title, company_name
            )
            
            message = Mail(
                from_email=self.from_email,
                to_emails=recipient_email,
                subject=subject,
                html_content=html_content
            )
            
            response = self.sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Cover letter email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send cover letter email. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending cover letter email to {recipient_email}: {str(e)}")
            return False

    def send_verification_email(self, recipient_email: str, recipient_name: str, verification_link: str) -> bool:
        """Send email verification link to new user"""
        if not self.sg:
            logger.error("SendGrid not configured. Cannot send email.")
            return False

        try:
            subject = "Welcome to ResuMatch AI - Verify Your Email"
            
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
                        <h1>Welcome to ResuMatch AI!</h1>
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
                        <p><strong>ResuMatch AI</strong></p>
                        <p>This is an automated message, please do not reply to this email.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            message = Mail(
                from_email=self.from_email,
                to_emails=recipient_email,
                subject=subject,
                html_content=html_content
            )
            
            response = self.sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Verification email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send verification email. Status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending verification email to {recipient_email}: {str(e)}")
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
        if not self.sg:
            logger.error("SendGrid not configured. Cannot send email.")
            return False

        try:
            subject = f"Your AI-Optimized Resume - {job_title}"
            
            html_content = self._generate_optimized_resume_email_html(
                recipient_name, optimized_resume, job_title
            )
            
            message = Mail(
                from_email=self.from_email,
                to_emails=recipient_email,
                subject=subject,
                html_content=html_content
            )
            
            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    if all(key in attachment for key in ['content', 'filename', 'type']):
                        file_content = base64.b64encode(attachment['content']).decode()
                        attached_file = Attachment(
                            FileContent(file_content),
                            FileName(attachment['filename']),
                            FileType(attachment['type']),
                            Disposition('attachment')
                        )
                        message.attachment = attached_file
            
            response = self.sg.send(message)
            
            if response.status_code in [200, 201, 202]:
                logger.info(f"Optimized resume email sent successfully to {recipient_email}")
                return True
            else:
                logger.error(f"Failed to send optimized resume email. Status code: {response.status_code}")
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
                    <p><strong>ResuMatch AI</strong></p>
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
                    <p><strong>ResuMatch AI</strong></p>
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

# In email_service.py

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
                        <p style="color: #475569; margin-bottom: 20px;">Your resume was scanned for crucial keywords from the job description. Here’s how you stack up:</p>
                        
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
                    <p>ResuMatch AI &copy; 2025</p>
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
        """Format keywords in a grid layout"""
        if not keywords:
            return f"<div class='keyword {keyword_type}'>None found</div>"
        
        # Limit to 21 keywords (3 rows of 7)
        display_keywords = keywords[:21]
        keyword_html = ""
        
        for keyword in display_keywords:
            # Truncate very long keywords
            display_keyword = keyword if len(keyword) <= 25 else keyword[:22] + "..."
            keyword_html += f"<div class='keyword {keyword_type}'>{display_keyword}</div>"
        
        if len(keywords) > 21:
            remaining = len(keywords) - 21
            keyword_html += f"<div class='keyword {keyword_type}' style='font-weight: bold;'>+{remaining} more</div>"
        
        return keyword_html


# Global email service instance
email_service = EmailService()
 