"""
PDF Generator - Uses xhtml2pdf to generate PDFs from HTML templates.
This ensures the PDF matches exactly what users see in the preview.
xhtml2pdf is pure Python with no system dependencies like gobject.
"""

import os
import io
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

from xhtml2pdf import pisa

logger = logging.getLogger(__name__)

# Get template directory path
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'html')


class PDFGenerator:
    """Generate professional PDFs from HTML templates using xhtml2pdf."""

    def __init__(self):
        """Initialize the PDF generator with Jinja2 environment."""
        self.jinja_env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def _html_to_pdf(self, html_content: str) -> bytes:
        """
        Convert HTML content to PDF bytes.

        Args:
            html_content: Rendered HTML string

        Returns:
            PDF file as bytes
        """
        buffer = io.BytesIO()

        # Convert HTML to PDF
        pisa_status = pisa.CreatePDF(
            src=html_content,
            dest=buffer,
            encoding='UTF-8'
        )

        if pisa_status.err:
            logger.error(f"PDF generation error: {pisa_status.err}")
            raise RuntimeError("Failed to generate PDF")

        pdf_bytes = buffer.getvalue()
        buffer.close()

        return pdf_bytes

    def generate_resume_pdf(
        self,
        structured_resume: Dict[str, Any],
        template_id: str = 'modern'
    ) -> bytes:
        """
        Generate a PDF resume from structured data.
        Uses the same HTML template as the preview for consistency.

        Args:
            structured_resume: Parsed resume data with contact, experience, etc.
            template_id: Template to use ('modern' or 'classic')

        Returns:
            PDF file as bytes
        """
        try:
            # Generate HTML using the same template as preview
            html_content = self.preview_html(structured_resume, template_id)

            # Convert HTML to PDF
            pdf_bytes = self._html_to_pdf(html_content)

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
        Uses the same HTML template as the preview for consistency.

        Args:
            cover_letter_text: The cover letter content
            contact: Contact information dict
            job_title: The job title being applied for
            company_name: The company name
            template_id: Template to use ('professional' or 'simple')
            hiring_manager: Optional hiring manager name

        Returns:
            PDF file as bytes
        """
        try:
            # Generate HTML using the same template as preview
            html_content = self.preview_cover_letter_html(
                cover_letter_text=cover_letter_text,
                contact=contact,
                job_title=job_title,
                company_name=company_name,
                template_id=template_id,
                hiring_manager=hiring_manager
            )

            # Convert HTML to PDF
            pdf_bytes = self._html_to_pdf(html_content)

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
        Generate HTML preview (for frontend display and PDF generation).

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
