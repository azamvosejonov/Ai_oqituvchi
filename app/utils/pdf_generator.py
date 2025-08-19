import os
from datetime import datetime
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch

CERTIFICATE_DIR = "static/certificates"


def create_certificate_pdf(user_name: str, level_completed: str, course_name: str, certificate_id: int) -> str:
    """
    Generates a PDF certificate for a user.

    Args:
        user_name: The full name of the user.
        level_completed: The level the user has completed (e.g., 'B1').
        course_name: The name of the course.
        certificate_id: The unique ID of the certificate record.

    Returns:
        The path to the generated PDF file.
    """
    # Ensure the directory exists
    os.makedirs(CERTIFICATE_DIR, exist_ok=True)

    # Define file path
    file_path = os.path.join(CERTIFICATE_DIR, f"certificate_{certificate_id}_{user_name.replace(' ', '_')}.pdf")

    # Create PDF
    c = canvas.Canvas(file_path, pagesize=letter)
    width, height = letter

    # Set up fonts and text
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(width / 2.0, height - 2 * inch, "Certificate of Achievement")

    c.setFont("Helvetica", 24)
    c.drawCentredString(width / 2.0, height - 3 * inch, "This is to certify that")

    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2.0, height - 4 * inch, user_name)

    c.setFont("Helvetica", 24)
    c.drawCentredString(width / 2.0, height - 5 * inch, f"has successfully completed the course")

    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2.0, height - 6 * inch, course_name)

    c.setFont("Helvetica", 18)
    c.drawCentredString(width / 2.0, height - 7 * inch, f"(Level: {level_completed})")

    c.setFont("Helvetica", 18)
    c.drawCentredString(width / 2.0, height - 8 * inch, f"Issued on: {datetime.utcnow().strftime('%Y-%m-%d')}")

    c.save()

    return file_path
