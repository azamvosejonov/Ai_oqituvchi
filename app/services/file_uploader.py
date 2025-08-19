import shutil
from pathlib import Path
import uuid
from fastapi import UploadFile

from app.core.config import settings

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(exist_ok=True)

async def save_upload_file(
    upload_file: UploadFile,
    destination: Path
) -> str:
    """
    Saves an uploaded file to a destination and returns the file path.
    """
    try:
        # Ensure the destination directory exists
        destination.parent.mkdir(exist_ok=True, parents=True)
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    finally:
        upload_file.file.close()
    
    # Return the relative path to be stored in the DB
    return str(destination.relative_to(UPLOAD_DIR.parent))

def get_unique_filename(filename: str) -> str:
    """
    Generates a unique filename to prevent overwrites.
    """
    file_extension = Path(filename).suffix
    unique_id = uuid.uuid4()
    return f"{unique_id}{file_extension}"

async def handle_file_upload(
    upload_file: UploadFile,
    sub_folder: str
) -> str:
    """
    Handles the file upload process: generates a unique name, saves the file,
    and returns the relative path.
    """
    if not upload_file:
        return None
        
    unique_filename = get_unique_filename(upload_file.filename)
    destination_path = UPLOAD_DIR / sub_folder / unique_filename
    
    file_path = await save_upload_file(upload_file, destination_path)
    return file_path
