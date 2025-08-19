import os
from datetime import datetime
from uuid import uuid4

from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.lib.colors import black, darkblue
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from app.core.config import settings

CERTIFICATES_DIR = os.path.join(settings.MEDIA_ROOT, "certificates")
os.makedirs(CERTIFICATES_DIR, exist_ok=True)

# Register fonts if they exist
FONT_DIR = os.path.join(settings.STATIC_FILES_DIR, "fonts")

try:
    pdfmetrics.registerFont(TTFont('DejaVu-Bold', os.path.join(FONT_DIR, 'DejaVuSans-Bold.ttf')))
    pdfmetrics.registerFont(TTFont('DejaVu', os.path.join(FONT_DIR, 'DejaVuSans.ttf')))
    FONT_FAMILY_BOLD = 'DejaVu-Bold'
    FONT_FAMILY = 'DejaVu'
except Exception:
    FONT_FAMILY_BOLD = 'Helvetica-Bold'
    FONT_FAMILY = 'Helvetica'

def create_certificate_pdf(
    user_name: str, 
    course_name: str, 
    issue_date: str, 
    verification_code: str, 
    level_completed: str = None,
    certificate_id: int = None
) -> str:
    """Generates a PDF certificate and returns the file path."""
    file_name = f"{uuid4()}.pdf"
    file_path = os.path.join(CERTIFICATES_DIR, file_name)

    c = canvas.Canvas(file_path, pagesize=landscape(letter))
    width, height = landscape(letter)

    # Draw border
    c.setStrokeColor(darkblue)
    c.setLineWidth(3)
    c.rect(0.2 * inch, 0.2 * inch, width - 0.4 * inch, height - 0.4 * inch)

    # Title
    c.setFont(FONT_FAMILY_BOLD, 36)
    c.drawCentredString(width / 2, height - 1.5 * inch, "Certificate of Completion")

    # "This certifies that"
    c.setFont(FONT_FAMILY, 18)
    c.drawCentredString(width / 2, height - 2.5 * inch, "This certifies that")

    # User Name
    c.setFont(FONT_FAMILY_BOLD, 32)
    c.setFillColor(darkblue)
    c.drawCentredString(width / 2, height - 3.5 * inch, user_name)

    # "has successfully completed the course"
    c.setFont(FONT_FAMILY, 18)
    c.setFillColor(black)
    c.drawCentredString(width / 2, height - 4.5 * inch, "has successfully completed the course")

    # Course Name
    c.setFont(FONT_FAMILY_BOLD, 24)
    c.drawCentredString(width / 2, height - 5.2 * inch, course_name)
    
    # Level Completed
    if level_completed:
        c.setFont(FONT_FAMILY, 16)
        c.drawCentredString(width / 2, height - 5.8 * inch, f"Level: {level_completed}")

    # Issue Date
    c.setFont(FONT_FAMILY, 12)
    c.drawString(0.5 * inch, 0.5 * inch, f"Issue Date: {issue_date}")

    # Verification Code
    c.drawRightString(width - 0.5 * inch, 0.5 * inch, f"Verification Code: {verification_code}")

    c.save()
    return file_path
