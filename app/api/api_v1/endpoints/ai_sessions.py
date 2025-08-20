from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any, List
from uuid import uuid4
from pathlib import Path
from datetime import datetime
import json
import logging

from app import models, schemas
from app.api import deps
from app.core.config import settings
from app.core.cache import redis_client
from app.services import ai_service
from app.crud import crud_user_ai_usage
from gtts import gTTS
from gtts.lang import tts_langs

router = APIRouter()
logger = logging.getLogger(__name__)

# Helpers
SESSION_PREFIX = "ai_session"
MEMORY_SESSIONS: Dict[str, Dict[str, Any]] = {}


def _session_key(session_id: str) -> str:
    return f"{SESSION_PREFIX}:{session_id}"


def _now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def _ensure_owner(session: Dict[str, Any], user_id: int):
    if not session or session.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Session not found")


def _load_session(session_id: str) -> Optional[Dict[str, Any]]:
    try:
        data = redis_client.get(_session_key(session_id))
        if not data:
            # try memory fallback
            return MEMORY_SESSIONS.get(session_id)
        try:
            return json.loads(data)
        except Exception:
            return None
    except Exception:
        # Redis unavailable -> memory fallback
        return MEMORY_SESSIONS.get(session_id)


def _save_session(session_id: str, session: Dict[str, Any], ttl_seconds: int = 60 * 60 * 24 * 7):
    # default TTL 7 days
    try:
        redis_client.setex(_session_key(session_id), ttl_seconds, json.dumps(session, default=str))
    except Exception:
        # Redis unavailable -> save to memory
        MEMORY_SESSIONS[session_id] = session


def _list_user_sessions(user_id: int) -> List[Dict[str, Any]]:
    """Return all sessions for a given user from Redis."""
    sessions: List[Dict[str, Any]] = []
    try:
        keys = redis_client.keys(f"{SESSION_PREFIX}:*")
        for k in keys:
            try:
                raw = redis_client.get(k)
                if not raw:
                    continue
                sess = json.loads(raw)
                if sess.get("user_id") == user_id:
                    sessions.append(sess)
            except Exception:
                # skip malformed entries
                continue
    except Exception:
        # Redis unavailable -> use in-memory sessions
        for sess in MEMORY_SESSIONS.values():
            try:
                if sess.get("user_id") == user_id:
                    sessions.append(sess)
            except Exception:
                continue
    # Order by created_at desc if present
    def _created_at(s: Dict[str, Any]):
        return s.get("created_at") or ""
    sessions.sort(key=_created_at, reverse=True)
    return sessions


@router.post("/sessions", summary="Create AI multi-turn session")
async def create_session(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    title: Optional[str] = Query(default=None, description="Optional session title")
):
    session_id = uuid4().hex
    session = {
        "id": session_id,
        "user_id": current_user.id,
        "title": title or "AI Session",
        "status": "idle",
        "created_at": _now_iso(),
        "messages": []  # list of {role, text, audio_url, analysis, created_at}
    }
    _save_session(session_id, session)
    return session


@router.get("/sessions", summary="List user's AI sessions")
async def list_sessions(
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    sessions = _list_user_sessions(current_user.id)
    return {"sessions": sessions, "count": len(sessions)}


@router.get("/sessions/{session_id}", summary="Get session with history")
async def get_session(
    session_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    session = _load_session(session_id)
    _ensure_owner(session, current_user.id)
    return session


@router.patch("/sessions/{session_id}", summary="Update session metadata (e.g., title)")
async def update_session(
    session_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    title: Optional[str] = Form(default=None),
    status: Optional[str] = Form(default=None),
):
    session = _load_session(session_id)
    _ensure_owner(session, current_user.id)
    if title is not None:
        session["title"] = title
    if status is not None:
        session["status"] = status
    session["updated_at"] = _now_iso()
    _save_session(session_id, session)
    return session


@router.delete("/sessions/{session_id}", summary="Delete a session")
async def delete_session(
    session_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    session = _load_session(session_id)
    _ensure_owner(session, current_user.id)
    try:
        redis_client.delete(_session_key(session_id))
    except Exception:
        # Redis unavailable -> remove from memory
        MEMORY_SESSIONS.pop(session_id, None)
    return {"status": "deleted", "id": session_id}


@router.post("/sessions/{session_id}/reset", summary="Clear all messages in a session")
async def reset_session(
    session_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
):
    session = _load_session(session_id)
    _ensure_owner(session, current_user.id)
    session["messages"] = []
    session["status"] = "idle"
    session["updated_at"] = _now_iso()
    _save_session(session_id, session)
    return session


@router.post("/sessions/{session_id}/messages", summary="Post user message (text or audio) and get assistant reply")
async def post_message(
    session_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.AIQuotaChecker('gpt4o_requests_left', 1)),
    text: Optional[str] = Form(default=None),
    audio_file: Optional[UploadFile] = File(default=None),
    speak: bool = Form(default=False),
    language: str = Form(default="uz"),
    reference_text: Optional[str] = Form(default=None),
):
    session = _load_session(session_id)
    _ensure_owner(session, current_user.id)

    # 1) Ingest user input (text or audio -> STT)
    if not text and not audio_file:
        raise HTTPException(status_code=400, detail="Provide either text or audio_file")

    user_text = text
    audio_url = None

    if audio_file is not None:
        if not audio_file.content_type.startswith("audio/"):
            raise HTTPException(status_code=400, detail="Invalid file type. Please upload an audio file.")
        content = await audio_file.read()
        try:
            # STT quota: check and decrement 1 request
            if not crud_user_ai_usage.user_ai_usage.has_enough_quota(
                db, user_id=current_user.id, field="stt_requests_left", amount=1
            ):
                raise HTTPException(status_code=403, detail="Not enough STT requests left.")
            crud_user_ai_usage.user_ai_usage.decrement(
                db, user_id=current_user.id, field="stt_requests_left", amount=1
            )
            crud_user_ai_usage.user_ai_usage.increment(
                db, user_id=current_user.id, field="stt_requests", amount=1
            )
            user_text = await ai_service.transcribe_audio_file(content)
        except Exception as e:
            logger.error(f"STT failed in session {session_id}: {e}")
            raise HTTPException(status_code=500, detail="STT failed")

    if not user_text:
        raise HTTPException(status_code=400, detail="Empty message")

    # Append user message
    user_msg = {
        "role": "user",
        "text": user_text,
        "audio_url": audio_url,
        "analysis": None,
        "created_at": _now_iso(),
    }
    session["messages"].append(user_msg)

    # 2) Analyze user's message (heuristic, structured)
    analysis = await ai_service.analyze_answer(
        user_response=user_text,
        reference_text=reference_text,
        language=language,
    )
    user_msg["analysis"] = analysis

    # 3) Build chat history for completion (last 6 messages)
    history: List[Dict[str, Any]] = []
    for m in session["messages"][-6:]:
        history.append({
            "role": "user" if m["role"] == "user" else "model",
            "parts": [{"text": m.get("text", "") or ""}]
        })

    # Ensure there is at least one message for the current turn
    if not history:
        history = [{"role": "user", "parts": [{"text": user_text}]}]

    # 3.1) Inject adaptive instruction based on user's level (safe, local-only)
    # This only affects the current endpoint's prompt and does not change other APIs.
    try:
        level_value = None
        progress = getattr(current_user, "progress", None)
        if progress is not None and getattr(progress, "level", None) is not None:
            # SQLAlchemy Enum -> use .value if available, otherwise str(enum)
            enum_level = progress.level
            level_value = getattr(enum_level, "value", str(enum_level))
        level_value = level_value or "beginner"

        instruction_text = (
            f"Ko'rsatma: foydalanuvchi darajasi '{level_value}'. "
            f"Javobni '{language}' tilida qisqa, sodda va tushunarli qiling. "
            "Maslahat, kichik topshiriq va 1-2 savol kiriting. "
            "Kerak bo'lsa qisqa misol keltiring."
        )

        # Prepend instruction as context; last item remains the current user turn
        history.insert(0, {"role": "user", "parts": [{"text": instruction_text}]})
    except Exception:
        # Fail-safe: if anything goes wrong, continue without instruction
        pass

    # 4) Get assistant response via LLM (Gemini or disabled fallback)
    assistant_text_chunks: List[str] = []
    try:
        async for chunk in ai_service.get_chat_completion(history):
            if chunk:
                assistant_text_chunks.append(chunk)
    except Exception as e:
        logger.error(f"LLM chat failed: {e}")

    assistant_text = "".join(assistant_text_chunks).strip()
    if not assistant_text:
        # Fallback deterministic
        assistant_text = f"Qabul qilindi. Siz: '{user_text[:200]}' dedingiz. Mana tahlil natijasi: {json.dumps(analysis)}"

    # Increment LLM usage counter (quota already decremented by dependency)
    crud_user_ai_usage.user_ai_usage.increment(
        db, user_id=current_user.id, field="gemini_requests", amount=1
    )

    # 5) Optionally synthesize TTS for assistant reply
    assistant_audio_url = None
    if speak and assistant_text:
        try:
            uploads_root = Path(settings.UPLOAD_DIR)
            tts_dir = uploads_root / "tts"
            tts_dir.mkdir(parents=True, exist_ok=True)
            filename = f"sess_{session_id}_{int(datetime.utcnow().timestamp())}.mp3"
            filepath = tts_dir / filename
            requested = language.split('-')[0]
            supported = tts_langs()
            fallback_order = [requested, "uz", "tr", "ru", "en"]
            chosen = next((lc for lc in fallback_order if lc in supported), None) or next(iter(supported.keys()))
            # TTS quota: based on character length of assistant_text
            tts_chars = len(assistant_text)
            if not crud_user_ai_usage.user_ai_usage.has_enough_quota(
                db, user_id=current_user.id, field="tts_chars_left", amount=tts_chars
            ):
                raise HTTPException(status_code=403, detail="Not enough TTS characters left.")
            crud_user_ai_usage.user_ai_usage.decrement(
                db, user_id=current_user.id, field="tts_chars_left", amount=tts_chars
            )
            crud_user_ai_usage.user_ai_usage.increment(
                db, user_id=current_user.id, field="tts_characters", amount=tts_chars
            )
            tts = gTTS(text=assistant_text, lang=chosen, slow=False)
            tts.save(str(filepath))
            assistant_audio_url = f"/uploads/tts/{filename}"
        except Exception as e:
            logger.error(f"TTS failed for session {session_id}: {e}")

    # Append assistant message
    assistant_msg = {
        "role": "assistant",
        "text": assistant_text,
        "audio_url": assistant_audio_url,
        "analysis": None,
        "created_at": _now_iso(),
    }
    session["messages"].append(assistant_msg)
    session["status"] = "idle"

    # Persist session
    _save_session(session_id, session)

    return {
        "session": session,
        "assistant": {
            "text": assistant_text,
            "audio_url": assistant_audio_url,
        },
        "user_analysis": analysis,
    }


@router.get("/sessions/{session_id}/messages", summary="Get messages in a session")
async def get_messages(
    session_id: str,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Depends(deps.get_current_active_user),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    session = _load_session(session_id)
    _ensure_owner(session, current_user.id)
    messages = session.get("messages", [])
    return {
        "total": len(messages),
        "items": messages[offset: offset + limit],
    }
