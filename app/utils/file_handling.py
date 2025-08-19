import shutil
from pathlib import Path
from fastapi import UploadFile

def save_upload_file(upload_file: UploadFile, destination: Path) -> str:
    """Saves an uploaded file to a destination and returns the absolute path."""
    try:
        with destination.open("wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
        return str(destination.absolute())
    finally:
        upload_file.file.close()
