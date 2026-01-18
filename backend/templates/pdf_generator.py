"""
PDF Generator - Uses ReportLab to generate professional PDFs.
ReportLab is a pure Python library with no system dependencies like gobject.
"""

import os
import io
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List
from jinja2 import Environment, FileSystemLoader, select_autoescape

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    ListFlowable, ListItem, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY

logger = logging.getLogger(__name__)

# Get template directory path (for HTML preview)
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'html')


class PDFGenerator:
    """Generate professional PDFs using ReportLab."""

    def __init__(self):
        """Initialize the PDF generator."""
        # Jinja2 for HTML preview only
        self.jinja_env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=select_autoescape(['html', 'xml'])
        )
        self._setup_styles()

    def _setup_styles(self):
        """Setup ReportLab paragraph styles."""
        self.styles = getSampleStyleSheet()

        # Modern template colors
        self.modern_blue = colors.HexColor('#3B82F6')
        self.modern_dark = colors.HexColor('#1F2937')
        self.modern_gray = colors.HexColor('#6B7280')

        # Name style - large and bold
        self.styles.add(ParagraphStyle(
            name='ResumeName',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=self.modern_dark,
            spaceAfter=6,
            alignment=TA_CENTER
        ))

        # Contact info style
        self.styles.add(ParagraphStyle(
            name='ContactInfo',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.modern_gray,
            alignment=TA_CENTER,
            spaceAfter=12
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=12,
            textColor=self.modern_blue,
            spaceBefore=16,
            spaceAfter=8,
            borderColor=self.modern_blue,
            borderWidth=0,
            borderPadding=0
        ))

        # Job title style
        self.styles.add(ParagraphStyle(
            name='JobTitle',
            parent=self.styles['Normal'],
            fontSize=11,
            textColor=self.modern_dark,
            fontName='Helvetica-Bold',
            spaceAfter=2
        ))

        # Company style
        self.styles.add(ParagraphStyle(
            name='Company',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.modern_gray,
            spaceAfter=4
        ))

        # Body text style (renamed to avoid conflict with default)
        self.styles.add(ParagraphStyle(
            name='ResumeBody',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.modern_dark,
            spaceAfter=4,
            leading=14
        ))

        # Bullet style
        self.styles.add(ParagraphStyle(
            name='BulletText',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=self.modern_dark,
            leftIndent=12,
            spaceAfter=2,
            leading=13
        ))

        # Skills tag style
        self.styles.add(ParagraphStyle(
            name='SkillTag',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=self.modern_blue
        ))

    def generate_resume_pdf(
        self,
        structured_resume: Dict[str, Any],
        template_id: str = 'modern'
    ) -> bytes:
        """
        Generate a PDF resume from structured data.

        Args:
            structured_resume: Parsed resume data with contact, experience, etc.
            template_id: Template to use ('modern' or 'classic')

        Returns:
            PDF file as bytes
        """
        try:
            buffer = io.BytesIO()

            # Create PDF document
            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=0.5*inch,
                leftMargin=0.5*inch,
                topMargin=0.5*inch,
                bottomMargin=0.5*inch
            )

            story = []

            # Extract data with defaults
            contact = structured_resume.get('contact', {})
            summary = structured_resume.get('summary', '')
            experience = structured_resume.get('experience', [])
            education = structured_resume.get('education', [])
            skills = structured_resume.get('skills', {})
            certifications = structured_resume.get('certifications', [])

            # Header - Name
            name = contact.get('name', 'Your Name')
            story.append(Paragraph(name, self.styles['ResumeName']))

            # Contact info line
            contact_parts = []
            if contact.get('email'):
                contact_parts.append(contact['email'])
            if contact.get('phone'):
                contact_parts.append(contact['phone'])
            if contact.get('location'):
                contact_parts.append(contact['location'])
            if contact.get('linkedin'):
                contact_parts.append(contact['linkedin'])

            if contact_parts:
                contact_line = ' | '.join(contact_parts)
                story.append(Paragraph(contact_line, self.styles['ContactInfo']))

            # Divider line
            story.append(HRFlowable(
                width="100%",
                thickness=1,
                color=self.modern_blue,
                spaceBefore=6,
                spaceAfter=12
            ))

            # Summary
            if summary:
                story.append(Paragraph('PROFESSIONAL SUMMARY', self.styles['SectionHeader']))
                story.append(Paragraph(summary, self.styles['ResumeBody']))

            # Experience
            if experience:
                story.append(Paragraph('EXPERIENCE', self.styles['SectionHeader']))
                for job in experience:
                    title = job.get('title', '')
                    company = job.get('company', '')
                    location = job.get('location', '')
                    start_date = job.get('start_date', '')
                    end_date = job.get('end_date', 'Present')
                    achievements = job.get('achievements', [])

                    # Job title
                    story.append(Paragraph(title, self.styles['JobTitle']))

                    # Company and dates
                    company_line = f"{company}"
                    if location:
                        company_line += f" - {location}"
                    if start_date:
                        company_line += f" | {start_date} - {end_date}"
                    story.append(Paragraph(company_line, self.styles['Company']))

                    # Achievements as bullets
                    for achievement in achievements:
                        if achievement:
                            bullet_text = f"• {achievement}"
                            story.append(Paragraph(bullet_text, self.styles['BulletText']))

                    story.append(Spacer(1, 8))

            # Education
            if education:
                story.append(Paragraph('EDUCATION', self.styles['SectionHeader']))
                for edu in education:
                    degree = edu.get('degree', '')
                    field = edu.get('field', '')
                    institution = edu.get('institution', '')
                    graduation_date = edu.get('graduation_date', '')
                    gpa = edu.get('gpa', '')

                    # Degree line
                    degree_line = f"{degree}"
                    if field:
                        degree_line += f" in {field}"
                    story.append(Paragraph(degree_line, self.styles['JobTitle']))

                    # Institution
                    inst_line = institution
                    if graduation_date:
                        inst_line += f" | {graduation_date}"
                    if gpa:
                        inst_line += f" | GPA: {gpa}"
                    story.append(Paragraph(inst_line, self.styles['Company']))

                    story.append(Spacer(1, 6))

            # Skills
            if skills:
                story.append(Paragraph('SKILLS', self.styles['SectionHeader']))

                skill_sections = []
                if skills.get('technical'):
                    skill_sections.append(f"<b>Technical:</b> {', '.join(skills['technical'])}")
                if skills.get('soft'):
                    skill_sections.append(f"<b>Soft Skills:</b> {', '.join(skills['soft'])}")
                if skills.get('languages'):
                    skill_sections.append(f"<b>Languages:</b> {', '.join(skills['languages'])}")

                for section in skill_sections:
                    story.append(Paragraph(section, self.styles['ResumeBody']))

            # Certifications
            if certifications:
                story.append(Paragraph('CERTIFICATIONS', self.styles['SectionHeader']))
                for cert in certifications:
                    cert_name = cert.get('name', '')
                    issuer = cert.get('issuer', '')
                    date = cert.get('date', '')

                    cert_line = f"• {cert_name}"
                    if issuer:
                        cert_line += f" - {issuer}"
                    if date:
                        cert_line += f" ({date})"
                    story.append(Paragraph(cert_line, self.styles['BulletText']))

            # Build PDF
            doc.build(story)

            pdf_bytes = buffer.getvalue()
            buffer.close()

            logger.info(f"Generated resume PDF using {template_id} template")
            return pdf_bytes

        except Exception as e:
            logger.error(f"PDF generation failed: {e}")
            raise

    def generate_cover_letter_pdf(
        self,
        cover_letter_text: str,
        contact: Dict[str, str],
        job_title: str,
        company_name: str,
        template_id: str = 'professional',
        hiring_manager: Optional[str] = None
    ) -> bytes:
        """
        Generate a PDF cover letter.

        Args:
            cover_letter_text: The cover letter content
            contact: Contact information dict
            job_title: The job title being applied for
            company_name: The company name
            template_id: Template to use
            hiring_manager: Optional hiring manager name

        Returns:
            PDF file as bytes
        """
        try:
            buffer = io.BytesIO()

            doc = SimpleDocTemplate(
                buffer,
                pagesize=letter,
                rightMargin=1*inch,
                leftMargin=1*inch,
                topMargin=1*inch,
                bottomMargin=1*inch
            )

            story = []

            # Header with contact info
            name = contact.get('name', 'Your Name')
            story.append(Paragraph(name, self.styles['ResumeName']))

            contact_parts = []
            if contact.get('email'):
                contact_parts.append(contact['email'])
            if contact.get('phone'):
                contact_parts.append(contact['phone'])
            if contact.get('location'):
                contact_parts.append(contact['location'])

            if contact_parts:
                contact_line = ' | '.join(contact_parts)
                story.append(Paragraph(contact_line, self.styles['ContactInfo']))

            story.append(Spacer(1, 24))

            # Date
            date_str = datetime.now().strftime('%B %d, %Y')
            story.append(Paragraph(date_str, self.styles['ResumeBody']))
            story.append(Spacer(1, 12))

            # Hiring manager / company
            if hiring_manager:
                story.append(Paragraph(f"Dear {hiring_manager},", self.styles['ResumeBody']))
            else:
                story.append(Paragraph(f"Dear Hiring Manager,", self.styles['ResumeBody']))

            story.append(Spacer(1, 12))

            # Body paragraphs
            paragraphs = cover_letter_text.strip().split('\n\n')
            for para in paragraphs:
                para = para.replace('\n', ' ').strip()
                if para:
                    # Create justified body style
                    body_style = ParagraphStyle(
                        name='CoverBody',
                        parent=self.styles['Normal'],
                        fontSize=11,
                        textColor=self.modern_dark,
                        spaceAfter=12,
                        leading=16,
                        alignment=TA_JUSTIFY
                    )
                    story.append(Paragraph(para, body_style))

            story.append(Spacer(1, 12))

            # Closing
            story.append(Paragraph("Sincerely,", self.styles['ResumeBody']))
            story.append(Spacer(1, 24))
            story.append(Paragraph(name, self.styles['JobTitle']))

            # Build PDF
            doc.build(story)

            pdf_bytes = buffer.getvalue()
            buffer.close()

            logger.info(f"Generated cover letter PDF using {template_id} template")
            return pdf_bytes

        except Exception as e:
            logger.error(f"Cover letter PDF generation failed: {e}")
            raise

    def preview_html(
        self,
        structured_resume: Dict[str, Any],
        template_id: str = 'modern'
    ) -> str:
        """
        Generate HTML preview (for frontend display).

        Args:
            structured_resume: Parsed resume data
            template_id: Template to use

        Returns:
            Rendered HTML string
        """
        template_file = f'resume_{template_id}.html'

        # Verify template exists
        template_path = os.path.join(TEMPLATE_DIR, template_file)
        if not os.path.exists(template_path):
            template_file = 'resume_modern.html'

        template = self.jinja_env.get_template(template_file)
        return template.render(**structured_resume)

    def preview_cover_letter_html(
        self,
        cover_letter_text: str,
        contact: Dict[str, str],
        job_title: str,
        company_name: str,
        template_id: str = 'professional',
        hiring_manager: Optional[str] = None
    ) -> str:
        """
        Generate cover letter HTML preview.

        Args:
            cover_letter_text: The cover letter content
            contact: Contact information
            job_title: Job title
            company_name: Company name
            template_id: Template to use
            hiring_manager: Optional hiring manager name

        Returns:
            Rendered HTML string
        """
        template_file = f'cover_letter_{template_id}.html'

        template_path = os.path.join(TEMPLATE_DIR, template_file)
        if not os.path.exists(template_path):
            template_file = 'cover_letter_professional.html'

        formatted_content = self._format_cover_letter_content(cover_letter_text)

        template_data = {
            'contact': contact,
            'content': formatted_content,
            'job_title': job_title,
            'company_name': company_name,
            'hiring_manager': hiring_manager,
            'date': datetime.now().strftime('%B %d, %Y'),
            'company_address': ''
        }

        template = self.jinja_env.get_template(template_file)
        return template.render(**template_data)

    def _format_cover_letter_content(self, text: str) -> str:
        """Format cover letter text into HTML paragraphs."""
        if not text:
            return ""

        paragraphs = text.strip().split('\n\n')
        formatted = []
        for para in paragraphs:
            para = para.replace('\n', ' ').strip()
            if para:
                formatted.append(f'<p>{para}</p>')

        return '\n'.join(formatted)


# Singleton instance
pdf_generator = PDFGenerator()
