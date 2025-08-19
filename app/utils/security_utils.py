from datetime import datetime, timedelta, timezone
from typing import Optional, Any, Union

from jose import jwt, JWTError
from sqlalchemy.orm import Session
import httpx

from app.core.config import settings
from app.core.security import create_access_token
from app.schemas import User


def generate_password_reset_token(email: str) -> str:
    delta = timedelta(hours=settings.EMAIL_RESET_TOKEN_EXPIRE_HOURS)
    now = datetime.now(timezone.utc)
    expires = now + delta
    exp = expires.timestamp()
    encoded_jwt = jwt.encode(
        {"exp": exp, "nbf": now, "sub": email},
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM,
    )
    return encoded_jwt

def verify_password_reset_token(token: str) -> Optional[str]:
    try:
        decoded_token = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        return decoded_token["sub"]
    except JWTError:
        return None

async def send_reset_password_email(email_to: str, token: str) -> None:
    """
    In a real application, this would send an email.
    For now, we'll just print the link to the console for development purposes.
    """
    reset_link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    print(f"Password reset link for {email_to}: {reset_link}")
    # In production, you would use a service like SendGrid, Amazon SES, etc.
    # For example:
    # import sendgrid
    # from sendgrid.helpers.mail import Mail
    # message = Mail(
    #     from_email='no-reply@yourapp.com',
    #     to_emails=email_to,
    #     subject='Password Reset Request',
    #     html_content=f'<strong>Please click here to reset your password:</strong> <a href="{reset_link}">Reset Password</a>'
    # )
    # try:
    #     sg = sendgrid.SendGridAPIClient(settings.SENDGRID_API_KEY)
    #     response = await sg.send(message)
    # except Exception as e:
    #     print(e.message)


async def verify_recaptcha(token: str, client_ip: Optional[str] = None) -> bool:
    """
    Verifies a reCAPTCHA v3 token with Google's siteverify API.

    :param token: The reCAPTCHA token received from the frontend.
    :param client_ip: The user's IP address (optional but recommended).
    :return: True if the token is valid and the score is above the threshold, False otherwise.
    """
    if not settings.RECAPTCHA_SECRET_KEY:
        # If secret key is not set, bypass for development
        return True 

    params = {
        'secret': settings.RECAPTCHA_SECRET_KEY,
        'response': token,
    }
    if client_ip:
        params['remoteip'] = client_ip

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post("https://www.google.com/recaptcha/api/siteverify", data=params)
            response.raise_for_status()
            result = response.json()

            if result.get("success") and result.get("score", 0.0) >= settings.RECAPTCHA_SCORE_THRESHOLD:
                return True
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            # Log the error in a real application
            print(f"reCAPTCHA verification request failed: {e}")
            return False
    return False


def refresh_user_tokens(db: Session, user: User) -> tuple[str, str]:
    """
    Generates new access and refresh tokens for a user.
    """
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        subject=str(user.id), expires_delta=access_token_expires
    )

    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_access_token(
        subject=str(user.id), expires_delta=refresh_token_expires  # Note: The original 'type' claim is not supported by the current create_access_token function.
    )

    # Here you might want to store or invalidate old refresh tokens

    return access_token, refresh_token
