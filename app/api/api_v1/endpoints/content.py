from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from typing import Any, List, Dict, Optional
from pathlib import Path
import json
from app import models
from app.api import deps

router = APIRouter()

# Simple content management endpoints
CONTENT_DIR = Path("uploads/content")
CONTENT_DIR.mkdir(parents=True, exist_ok=True)
LESSONS_JSON = CONTENT_DIR / "lessons.json"

def ensure_lessons_json() -> None:
    if not LESSONS_JSON.exists():
        default_payload = {"lessons": [], "version": 1}
        LESSONS_JSON.write_text(json.dumps(default_payload, ensure_ascii=False, indent=2), encoding="utf-8")

def _load_lessons() -> Dict[str, Any]:
    ensure_lessons_json()
    try:
        return json.loads(LESSONS_JSON.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid lessons.json: {e}")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def _save_lessons(data: Dict[str, Any]) -> None:
    try:
        # atomic write
        tmp = LESSONS_JSON.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(LESSONS_JSON)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

def _next_id(items: List[Dict[str, Any]]) -> int:
    ids = [int(it.get("id", 0)) for it in items if isinstance(it.get("id"), (int, str)) and str(it.get("id")).isdigit()]
    return (max(ids) + 1) if ids else 1

def _find_index_by_id(items: List[Dict[str, Any]], lesson_id: int) -> int:
    for idx, it in enumerate(items):
        if str(it.get("id")) == str(lesson_id):
            return idx
    return -1

@router.get("/lessons/export")
async def export_lessons(
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    return _load_lessons()

@router.get("/lessons/validate")
async def validate_lessons_json(
    current_user: models.User = Depends(deps.get_current_active_superuser),
):
    """
    Validate lessons.json structure and referenced media files under uploads/content.
    Returns a summary with a list of validation errors (empty if valid).
    """
    data = _load_lessons()
    errors: List[str] = []

    # Basic structure
    if not isinstance(data, dict):
        errors.append("Root must be an object")
        return {"valid": False, "errors": errors}

    lessons = data.get("lessons")
    if lessons is None:
        errors.append("Missing 'lessons' array")
        return {"valid": False, "errors": errors}
    if not isinstance(lessons, list):
        errors.append("'lessons' must be an array")
        return {"valid": False, "errors": errors}

    # Per-lesson checks
    seen_ids = set()
    for i, lesson in enumerate(lessons):
        if not isinstance(lesson, dict):
            errors.append(f"lessons[{i}] must be an object")
            continue
        lid = lesson.get("id")
        title = lesson.get("title")
        if lid is None:
            errors.append(f"lessons[{i}] is missing 'id'")
        else:
            if str(lid) in seen_ids:
                errors.append(f"Duplicate lesson id: {lid}")
            seen_ids.add(str(lid))
        if not title:
            errors.append(f"lessons[{i}] is missing 'title'")

        # Media fields to check if given
        for field in ["video", "audio", "image", "exercise", "attachment"]:
            val = lesson.get(field)
            if isinstance(val, str) and val:
                # Consider relative paths under uploads/content
                if val.startswith("http://") or val.startswith("https://"):
                    continue
                candidate = CONTENT_DIR / val
                if not candidate.exists():
                    # try basename lookup in content dir
                    candidate2 = CONTENT_DIR / Path(val).name
                    if not candidate2.exists():
                        errors.append(f"lessons[{i}].{field}: file not found '{val}'")

    return {"valid": len(errors) == 0, "errors": errors, "count": len(lessons)}

@router.get("/lessons-json")
async def get_lessons_json(
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Return lessons JSON content for admin content management."""
    return _load_lessons()

@router.put("/lessons-json")
async def update_lessons_json(
    *,
    payload: Any,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Overwrite lessons.json with provided JSON payload."""
    try:
        # Validate that payload is JSON-serializable
        data = json.loads(json.dumps(payload))
        _save_lessons(data)
        return {"status": "ok", "size": len(json.dumps(data))}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid JSON: {str(e)}")

# ---- Lessons CRUD (admin) ----

@router.get("/lessons", response_model=List[Dict[str, Any]])
async def list_lessons(
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> List[Dict[str, Any]]:
    data = _load_lessons()
    return data.get("lessons", [])

@router.get("/lessons/{lesson_id}", response_model=Dict[str, Any])
async def get_lesson(
    lesson_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Dict[str, Any]:
    data = _load_lessons()
    lessons = data.get("lessons", [])
    idx = _find_index_by_id(lessons, lesson_id)
    if idx == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lesson not found")
    return lessons[idx]

@router.post("/lessons", status_code=status.HTTP_201_CREATED, response_model=Dict[str, Any])
async def create_lesson(
    payload: Dict[str, Any],
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Dict[str, Any]:
    data = _load_lessons()
    lessons = data.setdefault("lessons", [])
    # minimal validation
    if not payload.get("title"):
        raise HTTPException(status_code=400, detail="'title' is required")
    new_item = dict(payload)
    new_item["id"] = _next_id(lessons)
    lessons.append(new_item)
    _save_lessons(data)
    return new_item

@router.put("/lessons/{lesson_id}", response_model=Dict[str, Any])
async def update_lesson(
    lesson_id: int,
    payload: Dict[str, Any],
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Dict[str, Any]:
    data = _load_lessons()
    lessons = data.setdefault("lessons", [])
    idx = _find_index_by_id(lessons, lesson_id)
    if idx == -1:
        raise HTTPException(status_code=404, detail="Lesson not found")
    # require title on full update
    if not payload.get("title"):
        raise HTTPException(status_code=400, detail="'title' is required")
    updated = dict(payload)
    updated["id"] = lesson_id
    lessons[idx] = updated
    _save_lessons(data)
    return updated

@router.patch("/lessons/{lesson_id}", response_model=Dict[str, Any])
async def patch_lesson(
    lesson_id: int,
    payload: Dict[str, Any],
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Dict[str, Any]:
    data = _load_lessons()
    lessons = data.setdefault("lessons", [])
    idx = _find_index_by_id(lessons, lesson_id)
    if idx == -1:
        raise HTTPException(status_code=404, detail="Lesson not found")
    merged = {**lessons[idx], **payload, "id": lesson_id}
    lessons[idx] = merged
    _save_lessons(data)
    return merged

@router.delete("/lessons/{lesson_id}")
async def delete_lesson(
    lesson_id: int,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Dict[str, Any]:
    data = _load_lessons()
    lessons = data.setdefault("lessons", [])
    idx = _find_index_by_id(lessons, lesson_id)
    if idx == -1:
        raise HTTPException(status_code=404, detail="Lesson not found")
    removed = lessons.pop(idx)
    _save_lessons(data)
    return {"status": "deleted", "id": lesson_id, "title": removed.get("title")}

@router.post("/lessons/bulk-import")
async def bulk_import_lessons(
    payload: Dict[str, Any],
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Dict[str, Any]:
    """
    Accepts payload in shape {"lessons": [...], "version": <int>?}
    If items have no id, they will be assigned.
    """
    if not isinstance(payload, dict) or "lessons" not in payload or not isinstance(payload["lessons"], list):
        raise HTTPException(status_code=400, detail="Payload must contain 'lessons' array")
    data = _load_lessons()
    incoming = payload["lessons"]
    # assign ids if missing
    next_id = _next_id(data.get("lessons", []))
    for it in incoming:
        if "id" not in it:
            it["id"] = next_id
            next_id += 1
    data["lessons"] = incoming
    if "version" in payload:
        data["version"] = payload["version"]
    _save_lessons(data)
    return {"status": "ok", "count": len(incoming)}

@router.get("/media", response_model=List[str])
async def list_media(
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """List uploaded media filenames."""
    try:
        return [p.name for p in CONTENT_DIR.iterdir() if p.is_file()]
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.post("/media/upload")
async def upload_media(
    *,
    file: UploadFile = File(...),
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Upload a media file for AI content management and return a local URL."""
    try:
        dest = CONTENT_DIR / file.filename
        with dest.open("wb") as f:
            f.write(await file.read())
        return {"filename": file.filename, "url": f"/uploads/content/{file.filename}"}
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

@router.delete("/media/{filename}")
async def delete_media(
    filename: str,
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> Any:
    """Delete a media file by filename."""
    try:
        target = CONTENT_DIR / filename
        if not target.exists() or not target.is_file():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        target.unlink()
        return {"status": "deleted", "filename": filename}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
