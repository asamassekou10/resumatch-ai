"""
PDF Generator - Uses WeasyPrint to generate professional PDFs from HTML templates.
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from jinja2 import Environment, FileSystemLoader, select_autoescape

logger = logging.getLogger(__name__)

# Get template directory path
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'html')


class PDFGenerator:
    """Generate professional PDFs from HTML templates using WeasyPrint."""

    def __init__(self):
        """Initialize the PDF generator with Jinja2 environment."""
        self.jinja_env = Environment(
            loader=FileSystemLoader(TEMPLATE_DIR),
            autoescape=select_autoescape(['html', 'xml'])
        )

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
            # Import WeasyPrint here to handle import errors gracefully
            from weasyprint import HTML, CSS

            template_file = f'resume_{template_id}.html'

            # Verify template exists
            template_path = os.path.join(TEMPLATE_DIR, template_file)
            if not os.path.exists(template_path):
                logger.warning(f"Template {template_file} not found, using modern")
                template_file = 'resume_modern.html'

            # Load and render template
            template = self.jinja_env.get_template(template_file)
            html_content = template.render(**structured_resume)

            # Generate PDF
            html = HTML(string=html_content)
            pdf_bytes = html.write_pdf()

            logger.info(f"Generated resume PDF using {template_id} template")
            return pdf_bytes

        except ImportError as e:
            logger.error(f"WeasyPrint not installed: {e}")
            raise RuntimeError(
                "PDF generation requires WeasyPrint. "
                "Install it with: pip install weasyprint"
            )
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
            cover_letter_text: The cover letter content (can include paragraphs)
            contact: Contact information dict with name, email, phone, etc.
            job_title: The job title being applied for
            company_name: The company name
            template_id: Template to use ('professional' or 'simple')
            hiring_manager: Optional hiring manager name

        Returns:
            PDF file as bytes
        """
        try:
            from weasyprint import HTML

            template_file = f'cover_letter_{template_id}.html'

            # Verify template exists
            template_path = os.path.join(TEMPLATE_DIR, template_file)
            if not os.path.exists(template_path):
                logger.warning(f"Template {template_file} not found, using professional")
                template_file = 'cover_letter_professional.html'

            # Format the cover letter content
            # Convert line breaks to paragraph tags
            formatted_content = self._format_cover_letter_content(cover_letter_text)

            # Prepare template data
            template_data = {
                'contact': contact,
                'content': formatted_content,
                'job_title': job_title,
                'company_name': company_name,
                'hiring_manager': hiring_manager,
                'date': datetime.now().strftime('%B %d, %Y'),
                'company_address': ''  # Can be added later if needed
            }

            # Load and render template
            template = self.jinja_env.get_template(template_file)
            html_content = template.render(**template_data)

            # Generate PDF
            html = HTML(string=html_content)
            pdf_bytes = html.write_pdf()

            logger.info(f"Generated cover letter PDF using {template_id} template")
            return pdf_bytes

        except ImportError as e:
            logger.error(f"WeasyPrint not installed: {e}")
            raise RuntimeError(
                "PDF generation requires WeasyPrint. "
                "Install it with: pip install weasyprint"
            )
        except Exception as e:
            logger.error(f"Cover letter PDF generation failed: {e}")
            raise

    def _format_cover_letter_content(self, text: str) -> str:
        """
        Format cover letter text into HTML paragraphs.

        Args:
            text: Raw cover letter text

        Returns:
            HTML-formatted content with paragraph tags
        """
        if not text:
            return ""

        # Split by double newlines (paragraph breaks)
        paragraphs = text.strip().split('\n\n')

        # Wrap each paragraph in <p> tags
        formatted = []
        for para in paragraphs:
            # Clean up single newlines within paragraphs
            para = para.replace('\n', ' ').strip()
            if para:
                formatted.append(f'<p>{para}</p>')

        return '\n'.join(formatted)

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


# Singleton instance
pdf_generator = PDFGenerator()
