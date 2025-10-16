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

    def _generate_analysis_email_html(self, recipient_name: str, analysis_data: dict) -> str:
        """Generate HTML content for analysis results email"""
        match_score = analysis_data.get('match_score', 0)
        job_title = analysis_data.get('job_title', 'Position')
        company_name = analysis_data.get('company_name', 'Company')
        analysis_id = analysis_data.get('analysis_id', '')
        
        # Color coding for match score
        score_color = "#28a745" if match_score >= 70 else "#ffc107" if match_score >= 50 else "#dc3545"
        
        # Website URL
        website_url = os.getenv('FRONTEND_URL', 'http://localhost:3000')
        dashboard_url = f"{website_url}/dashboard" if analysis_id else website_url
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI Resume Analysis Results</title>
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
                .header p {{
                    margin: 0;
                    opacity: 0.9;
                }}
                .content {{ 
                    padding: 30px 20px;
                }}
                .score {{ 
                    font-size: 48px; 
                    font-weight: bold; 
                    color: {score_color}; 
                    text-align: center; 
                    margin: 20px 0;
                    padding: 20px;
                    background: #f8f9fa;
                    border-radius: 8px;
                }}
                .score-label {{
                    font-size: 14px;
                    color: #666;
                    display: block;
                    margin-bottom: 10px;
                }}
                .section {{ 
                    margin: 20px 0; 
                    padding: 20px; 
                    background: #f8f9fa; 
                    border-radius: 8px;
                    border-left: 4px solid #667eea;
                }}
                .section h3 {{
                    margin-top: 0;
                    color: #333;
                    font-size: 18px;
                }}
                .keywords {{ 
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
                    gap: 8px;
                    margin-top: 10px;
                }}
                .keyword {{ 
                    background: #e9ecef; 
                    padding: 8px 12px; 
                    border-radius: 6px; 
                    font-size: 13px;
                    text-align: center;
                    word-break: break-word;
                }}
                .missing {{ 
                    background: #f8d7da; 
                    color: #721c24; 
                    border: 1px solid #f5c6cb;
                }}
                .found {{ 
                    background: #d4edda; 
                    color: #155724; 
                    border: 1px solid #c3e6cb;
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
                    text-align: center;
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
                .footer p {{
                    margin: 5px 0;
                }}
                @media only screen and (max-width: 600px) {{
                    .container {{
                        margin: 0;
                        border-radius: 0;
                    }}
                    .content {{
                        padding: 20px 15px;
                    }}
                    .score {{
                        font-size: 36px;
                    }}
                    .keywords {{
                        grid-template-columns: repeat(auto-fill, minmax(100px, 1fr));
                    }}
                    .keyword {{
                        font-size: 12px;
                        padding: 6px 10px;
                    }}
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>AI Resume Analysis Complete</h1>
                    <p>Your personalized resume analysis for {job_title}</p>
                    {f'<p>at {company_name}</p>' if company_name and company_name != 'Company' else ''}
                </div>
                
                <div class="content">
                    <div class="score">
                        <span class="score-label">Match Score</span>
                        {match_score}%
                    </div>
                    
                    <div class="section">
                        <h3>Analysis Summary</h3>
                        <p><strong>Job Title:</strong> {job_title}</p>
                        {f'<p><strong>Company:</strong> {company_name}</p>' if company_name and company_name != 'Company' else ''}
                        <p><strong>Match Score:</strong> <span style="color: {score_color}; font-weight: bold;">{match_score}%</span></p>
                    </div>
                    
                    <div class="section">
                        <h3>Keywords Found ({len(analysis_data.get('keywords_found', []))})</h3>
                        <div class="keywords">
                            {self._format_keywords_grid(analysis_data.get('keywords_found', []), 'found')}
                        </div>
                    </div>
                    
                    <div class="section">
                        <h3>Missing Keywords ({len(analysis_data.get('keywords_missing', []))})</h3>
                        <div class="keywords">
                            {self._format_keywords_grid(analysis_data.get('keywords_missing', []), 'missing')}
                        </div>
                    </div>
                    
                    <div class="section">
                        <h3>AI Suggestions</h3>
                        <p style="margin: 0;">{analysis_data.get('suggestions', 'No specific suggestions available.')}</p>
                    </div>
                    
                    {f'''<div class="section">
                        <h3>AI Feedback</h3>
                        <p style="margin: 0; white-space: pre-line;">{analysis_data.get('ai_feedback', '')}</p>
                    </div>''' if analysis_data.get('ai_feedback') else ''}
                    
                    <div class="cta-container">
                        <p style="margin-bottom: 15px; font-size: 16px; color: #333;">
                            <strong>View detailed insights and unlock more AI-powered features</strong>
                        </p>
                        <a href="{dashboard_url}" class="cta-button">
                            View Full Analysis Dashboard
                        </a>
                        <p style="margin-top: 15px; font-size: 13px; color: #666;">
                            Get personalized feedback, optimized resume, and cover letter
                        </p>
                    </div>
                </div>
                
                <div class="footer">
                    <p><strong>ResuMatch AI</strong> - Your AI-Powered Career Assistant</p>
                    <p>This analysis was generated using advanced AI technology</p>
                    <p style="margin-top: 10px;">
                        <a href="{website_url}" style="color: #667eea; text-decoration: none;">Visit Website</a>
                    </p>
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
# Global email service instance
email_service = EmailService()
 