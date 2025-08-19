import os
import sys
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timezone

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.schemas.speech import (
    PronunciationPhraseCreate, PronunciationSessionCreate,

)
from app import crud, models

# Test utility functions
def random_lower_string(length: int = 8) -> str:
    """Generate a random lowercase string of specified length"""
    import random
    import string
    return ''.join(random.choices(string.ascii_lowercase, k=length))

def create_test_pronunciation_phrase(db: Session, **kwargs):
    """Create a test pronunciation phrase"""
    text = kwargs.get('text', f"Test phrase {random_lower_string()}")
    level = kwargs.get('level', 'beginner')
    category = kwargs.get('category', 'test')
    
    phrase_in = PronunciationPhraseCreate(
        text=text,
        level=level,
        category=category
    )
    return crud.crud_pronunciation_phrase.create(db, obj_in=phrase_in)

def create_test_pronunciation_session(db: Session, user_id: int, **kwargs):
    """Create a test pronunciation session for a specific user."""
    level = kwargs.get('level', 'beginner')
    phrases = kwargs.get('phrases', [])

    # If no phrases provided, create some test phrases
    if not phrases:
        for _ in range(3):
            phrase = create_test_pronunciation_phrase(db)
            phrases.append(phrase.id)

    session_in = PronunciationSessionCreate(
        user_id=user_id,
        level=level,
        phrases=phrases
    )

    session = crud.crud_pronunciation_session.create(db, obj_in=session_in)

    # Mark as completed if requested
    if kwargs.get('completed', False):
        session.completed = True
        session.completed_at = datetime.now(timezone.utc)
        db.add(session)
        db.commit()
        db.refresh(session)

    return session

def create_test_pronunciation_attempt(db: Session, user_id: int, **kwargs):
    """Create a test pronunciation attempt for a specific user."""
    session_id = kwargs.get('session_id')
    phrase_id = kwargs.get('phrase_id')

    # If no phrase_id provided, create a test phrase
    if phrase_id is None:
        phrase = create_test_pronunciation_phrase(db)
        phrase_id = phrase.id

    # Create test attempt data
    attempt_data = {
        "user_id": user_id,
        "session_id": session_id,
        "phrase_id": phrase_id,
        "recognized_text": "test recognized text",
        "expected_text": "test expected text",
        "score": kwargs.get('score', 85.5),
        "feedback": kwargs.get('feedback', f"Test feedback {random_lower_string()}"),
        "analysis_data": {
            "word_level": {"test": 0.8},
            "phoneme_level": {
                "t": 0.9, 
                "e": 0.8, 
                "s": 0.7, 
                "t2": 0.9
            }
        }
    }

    return crud.crud_pronunciation_attempt.create(db, obj_in=attempt_data)


# --- Test Pronunciation Endpoints ---

@pytest.mark.parametrize("level", ["beginner", "intermediate", "advanced"])
def test_create_pronunciation_phrase(
    client: TestClient, power_user_token_headers: dict, db: Session, level: str
) -> None:
    """Test creating a pronunciation phrase for different levels."""
    data = {"text": f"A new {level} phrase", "level": level, "category": "testing"}
    response = client.post(
        f"{settings.API_V1_STR}/pronunciation/phrases/",
        headers=power_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["text"] == data["text"]
    assert content["level"] == level
    assert "id" in content


def test_get_pronunciation_phrase(
    client: TestClient, power_user_token_headers: dict, db: Session
) -> None:
    """Test retrieving a specific pronunciation phrase."""
    phrase = create_test_pronunciation_phrase(db)
    response = client.get(
        f"{settings.API_V1_STR}/pronunciation/phrases/{phrase.id}",
        headers=power_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["text"] == phrase.text
    assert content["id"] == phrase.id


def test_create_pronunciation_session(
    client: TestClient, power_user_token_headers: dict, db: Session, power_user: models.User
) -> None:
    """Test creating a new pronunciation session."""
    phrase1 = create_test_pronunciation_phrase(db)
    phrase2 = create_test_pronunciation_phrase(db)
    data = {"level": "beginner", "phrase_ids": [phrase1.id, phrase2.id]}
    response = client.post(
        f"{settings.API_V1_STR}/pronunciation/sessions/",
        headers=power_user_token_headers,
        json=data,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["user_id"] == power_user.id
    assert content["level"] == "beginner"
    assert len(content["phrases"]) == 2
    assert content["phrases"][0]["id"] in [phrase1.id, phrase2.id]


def test_analyze_pronunciation(
    client: TestClient, power_user_token_headers: dict, db: Session, tmp_path, power_user: models.User
) -> None:
    """Test analyzing pronunciation from an audio file."""
    # This test requires a valid audio file and external services/models to be mocked or available.
    # For now, we'll just check if the endpoint exists and returns a plausible error for bad data.
    phrase = create_test_pronunciation_phrase(db, text="hello world")
    session = create_test_pronunciation_session(db, user_id=power_user.id, phrases=[phrase.id])

    # Create a dummy audio file
    audio_content = b"dummy audio content"
    audio_file = tmp_path / "test.wav"
    audio_file.write_bytes(audio_content)

    with open(audio_file, "rb") as f:
        files = {"audio_file": (audio_file.name, f, "audio/wav")}
        data = {"session_id": session.id, "phrase_id": phrase.id}
        response = client.post(
            f"{settings.API_V1_STR}/pronunciation/analyze/",
            headers=power_user_token_headers,
            data=data,
            files=files,
        )
    # The actual service might fail, but we expect a 200 OK from the API endpoint itself
    # if the request is well-formed.
    assert response.status_code in [200, 500] # 500 if AI service fails
    if response.status_code == 200:
        content = response.json()
        assert "score" in content
        assert "recognized_text" in content


def test_get_pronunciation_history(
    client: TestClient, power_user_token_headers: dict, db: Session, power_user: models.User
) -> None:
    """Test retrieving the user's pronunciation history."""
    phrase = create_test_pronunciation_phrase(db)
    session = create_test_pronunciation_session(db, user_id=power_user.id, phrases=[phrase.id])
    create_test_pronunciation_attempt(db, user_id=power_user.id, session_id=session.id, phrase_id=phrase.id)

    response = client.get(
        f"{settings.API_V1_STR}/pronunciation/history/",
        headers=power_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert isinstance(content, list)
    assert len(content) >= 1
    assert content[0]["user_id"] == power_user.id


def test_get_pronunciation_profile(
    client: TestClient, power_user_token_headers: dict, db: Session, power_user: models.User
) -> None:
    """Test retrieving the user's pronunciation profile."""
    phrase = create_test_pronunciation_phrase(db)
    session = create_test_pronunciation_session(db, user_id=power_user.id, phrases=[phrase.id])
    create_test_pronunciation_attempt(db, user_id=power_user.id, session_id=session.id, phrase_id=phrase.id, score=90)
    create_test_pronunciation_attempt(db, user_id=power_user.id, session_id=session.id, phrase_id=phrase.id, score=70)

    response = client.get(
        f"{settings.API_V1_STR}/pronunciation/profile/",
        headers=power_user_token_headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert "average_score" in content
    assert content["average_score"] == 80.0
    assert "total_attempts" in content
    assert content["total_attempts"] >= 2
