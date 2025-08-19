import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core.config import settings
from tests.utils.utils import random_lower_string


# --- Test Word CRUD operations ---

def test_create_word(session: Session, power_user: models.User) -> None:
    """Test creating a word."""
    # Create a course first to satisfy the foreign key constraint, using the power_user as instructor
    course_in = schemas.CourseCreate(
        title="Test Course for Words", 
        description="Description",
        difficulty_level=schemas.DifficultyLevel.BEGINNER,
        instructor_id=power_user.id
    )
    course = crud.course.create_with_instructor(db=session, obj_in=course_in)

    # Create a lesson for the course
    lesson_in = schemas.LessonCreate(
        title="Test Lesson for Words",
        content="Test lesson content",
        course_id=course.id,
        order=1,
        avatar_id=1  # Use default avatar
    )
    lesson = crud.lesson.create(db=session, obj_in=lesson_in)

    word_in = schemas.WordCreate(word="test_word", translation="test_translation", course_id=course.id, lesson_id=lesson.id)
    word = crud.word.create(db=session, obj_in=word_in)
    assert word
    assert word.word == word_in.word
    assert word.translation == word_in.translation
    assert word.lesson_id == lesson.id


def test_read_words(session: Session, power_user: models.User):
    """Test reading words (both a single word and a list of all words)."""
    # Create a course and a word using the power_user as instructor
    course_in = schemas.CourseCreate(
        title="Test Course for Reading Words", 
        description="Description",
        difficulty_level=schemas.DifficultyLevel.INTERMEDIATE,
        instructor_id=power_user.id
    )
    course = crud.course.create_with_instructor(db=session, obj_in=course_in)

    # Create a lesson for the course
    lesson_in = schemas.LessonCreate(
        title="Test Lesson for Reading Words",
        content="Test lesson content",
        course_id=course.id,
        order=1,
        avatar_id=1  # Use default avatar
    )
    lesson = crud.lesson.create(db=session, obj_in=lesson_in)

    word_in = schemas.WordCreate(word="read_word", translation="read_translation", course_id=course.id, lesson_id=lesson.id)
    word = crud.word.create(db=session, obj_in=word_in)

    # Test reading the single word by ID
    retrieved_word = crud.word.get(db=session, id=word.id)
    assert retrieved_word
    assert retrieved_word.id == word.id
    assert retrieved_word.word == word_in.word

    # Test reading the list of all words
    words_list = crud.word.get_multi(db=session)
    assert isinstance(words_list, list)
    assert len(words_list) >= 1
    assert any(w.id == word.id for w in words_list)


def test_full_word_crud_cycle(session: Session, power_user: models.User):
    """Test the full lifecycle of a word: Create, Read, Update, Delete."""
    # Create a course using the power_user as instructor
    course_in = schemas.CourseCreate(
        title="Test Course for Word CRUD", 
        description="Description",
        difficulty_level=schemas.DifficultyLevel.ADVANCED,
        instructor_id=power_user.id
    )
    course = crud.course.create_with_instructor(db=session, obj_in=course_in)

    # Create a lesson for the course
    lesson_in = schemas.LessonCreate(
        title="Test Lesson for Word CRUD",
        content="Test lesson content",
        course_id=course.id,
        order=1,
        avatar_id=1  # Use default avatar
    )
    lesson = crud.lesson.create(db=session, obj_in=lesson_in)

    # Create
    word_in = schemas.WordCreate(word="crud_word", translation="crud_translation", course_id=course.id, lesson_id=lesson.id)
    created_word = crud.word.create(db=session, obj_in=word_in)
    assert created_word.word == word_in.word

    # Read
    read_word = crud.word.get(db=session, id=created_word.id)
    assert read_word
    assert read_word.word == word_in.word

    # Update
    word_update_in = schemas.WordUpdate(translation="updated_translation")
    updated_word = crud.word.update(db=session, db_obj=read_word, obj_in=word_update_in)
    assert updated_word.translation == word_update_in.translation

    # Delete
    deleted_word = crud.word.remove(db=session, id=created_word.id)
    assert deleted_word.id == created_word.id
    assert not crud.word.get(db=session, id=created_word.id)
