from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base


class ForumCategory(Base):
    __tablename__ = "forum_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Relationships
    topics = relationship("ForumTopic", back_populates="category", cascade="all, delete-orphan")


class ForumTopic(Base):
    __tablename__ = "forum_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_pinned = Column(Boolean, default=False)
    is_closed = Column(Boolean, default=False)
    author_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("forum_categories.id"), nullable=False)
    
    # Relationships
    author = relationship("User", back_populates="forum_topics")
    category = relationship("ForumCategory", back_populates="topics")
    posts = relationship("ForumPost", back_populates="topic", cascade="all, delete-orphan")


class ForumPost(Base):
    __tablename__ = "forum_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_edited = Column(Boolean, default=False)
    topic_id = Column(Integer, ForeignKey("forum_topics.id", ondelete="CASCADE"))
    author_id = Column(Integer, ForeignKey("users.id"))
    parent_id = Column(Integer, ForeignKey("forum_posts.id"), nullable=True)
    
    # Relationships
    author = relationship("User", back_populates="forum_posts")
    topic = relationship("ForumTopic", back_populates="posts")
    parent = relationship("ForumPost", remote_side=[id], backref="replies")
