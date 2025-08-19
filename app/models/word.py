from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship

from app.db.base_class import Base

class Word(Base):
    __tablename__ = "words"
    
    id = Column(Integer, primary_key=True, index=True)
    word = Column(String(100), nullable=False, index=True)
    translation = Column(String(255), nullable=True)
    language = Column(String(10), default="en")
    level = Column(String(20), nullable=True)  # A1, A2, B1, B2, C1, C2
    part_of_speech = Column(String(50), nullable=True)
    ipa_pronunciation = Column(String(100), nullable=True)  # International Phonetic Alphabet
    audio_url = Column(String(500), nullable=True)
    image_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    definitions = relationship("WordDefinition", back_populates="word", cascade="all, delete-orphan")
    examples = relationship("WordExample", back_populates="word", cascade="all, delete-orphan")
    synonyms = relationship("WordSynonym", back_populates="word", cascade="all, delete-orphan")
    antonyms = relationship("WordAntonym", back_populates="word", cascade="all, delete-orphan")
    
    # Relationship with Lesson
    lesson_id = Column(Integer, ForeignKey("interactive_lessons.id"), nullable=True)
    lesson = relationship("app.models.lesson.InteractiveLesson", back_populates="vocabulary")
    
    def __repr__(self):
        return f"<Word {self.word}>"


class WordDefinition(Base):
    __tablename__ = "word_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    definition = Column(Text, nullable=False)
    part_of_speech = Column(String(50), nullable=True)
    example = Column(Text, nullable=True)
    is_primary = Column(Boolean, default=False)
    
    # Relationships
    word = relationship("Word", back_populates="definitions")
    
    def __repr__(self):
        return f"<Definition {self.id} for Word {self.word_id}>"


class WordExample(Base):
    __tablename__ = "word_examples"
    
    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    example = Column(Text, nullable=False)
    translation = Column(Text, nullable=True)
    
    # Relationships
    word = relationship("Word", back_populates="examples")
    
    def __repr__(self):
        return f"<Example {self.id} for Word {self.word_id}>"


class WordSynonym(Base):
    __tablename__ = "word_synonyms"
    
    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    synonym = Column(String(100), nullable=False)
    
    # Relationships
    word = relationship("Word", back_populates="synonyms")
    
    def __repr__(self):
        return f"<Synonym {self.synonym} for Word {self.word_id}>"


class WordAntonym(Base):
    __tablename__ = "word_antonyms"
    
    id = Column(Integer, primary_key=True, index=True)
    word_id = Column(Integer, ForeignKey("words.id"), nullable=False)
    antonym = Column(String(100), nullable=False)
    
    # Relationships
    word = relationship("Word", back_populates="antonyms")
    
    def __repr__(self):
        return f"<Antonym {self.antonym} for Word {self.word_id}>"
