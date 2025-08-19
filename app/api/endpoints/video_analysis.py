import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks, Form
from sqlalchemy.orm import Session
from pathlib import Path
import shutil
import uuid
from datetime import datetime

from app import crud, models, schemas
from app.api import deps
from app.core.config import settings
from app.services.ai.gemini_service import GeminiService
from app.utils import save_upload_file

router = APIRouter()
UPLOAD_DIR = Path(settings.UPLOAD_DIR) / "videos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

@router.post("/upload", response_model=schemas.VideoUploadResponse)
async def upload_video(
    title: str = Form(...),
    description: str = Form(None),
    language: str = Form("uz"),
    file: UploadFile = File(...),
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    background_tasks: BackgroundTasks = None
):
    # File validation
    allowed_extensions = {".mp4", ".mov", ".avi", ".mkv"}
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(400, detail=f"Faqat {', '.join(allowed_extensions)} formatlari qo'llab-quvvatlanadi")
    
    # Create video record
    video_data = schemas.VideoAnalysisCreate(
        title=title,
        description=description,
        language=language,
        video_url="",
        metadata={"original_filename": file.filename}
    )
    
    db_video = crud.video_analysis.create_with_owner(db, obj_in=video_data, owner_id=current_user.id)
    
    try:
        # Save file
        filename = f"{db_video.id}_{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / filename
        save_upload_file(file, file_path)
        
        # Update with file URL
        video_url = f"{settings.SERVER_HOST}/uploads/videos/{filename}"
        db_video = crud.video_analysis.update(
            db, db_obj=db_video,
            obj_in={"video_url": video_url, "is_processed": False}
        )
        
        # Start analysis in background
        if background_tasks:
            background_tasks.add_task(analyze_video_task, db_video.id, str(file_path), language, db)
        
        return {"id": db_video.id, "status": "processing", "message": "Video yuklandi"}
        
    except Exception as e:
        db.delete(db_video)
        db.commit()
        raise HTTPException(500, detail=f"Xatolik: {str(e)}")

async def analyze_video_task(video_id: int, video_path: str, language: str, db: Session):
    try:
        db_video = crud.video_analysis.get(db, video_id)
        if not db_video:
            return
            
        # Update status
        db_video = crud.video_analysis.update(
            db, db_obj=db_video,
            obj_in={"processing_status": "processing"}
        )
        
        # Analyze with Gemini
        gemini = GeminiService()
        analysis = await gemini.analyze_video(video_path)
        
        if analysis["status"] != "completed":
            raise Exception(analysis.get("error", "Analysis failed"))
        
        # Save results
        crud.video_analysis.update(
            db, db_obj=db_video,
            obj_in={
                "is_processed": True,
                "processing_status": "completed",
                "metadata": {
                    **db_video.metadata,
                    "analysis": analysis,
                    "processed_at": str(datetime.utcnow())
                }
            }
        )
        
    except Exception as e:
        if db_video:
            crud.video_analysis.update(
                db, db_obj=db_video,
                obj_in={
                    "processing_status": "failed",
                    "metadata": {
                        **db_video.metadata,
                        "error": str(e)
                    }
                }
            )

@router.get("/{video_id}", response_model=schemas.VideoAnalysis)
def get_video_analysis(
    video_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    db_video = crud.video_analysis.get(db, video_id)
    if not db_video:
        raise HTTPException(404, detail="Video topilmadi")
    
    if db_video.owner_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(403, detail="Ruxsat yo'q")
    
    return db_video
