from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.forum import ForumCategory, ForumTopic, ForumPost
from app.models.user import User
from app.schemas.forum import (
    ForumCategoryCreate, ForumCategoryUpdate,
    ForumTopicCreate, ForumTopicUpdate,
    ForumPostCreate, ForumPostUpdate
)


class CRUDForumCategory(CRUDBase[ForumCategory, ForumCategoryCreate, ForumCategoryUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> Optional[ForumCategory]:
        return db.query(self.model).filter(self.model.name == name).first()


class CRUDForumTopic(CRUDBase[ForumTopic, ForumTopicCreate, ForumTopicUpdate]):
    def create_with_initial_post(self, db: Session, *, obj_in: ForumTopicCreate, author: User) -> ForumTopic:
        """Creates a new topic and its initial post."""
        # Extract post content from the topic creation schema
        post_content = obj_in.content
        
        # Create the topic object without the 'content' field
        topic_data = obj_in.model_dump(exclude={'content'})
        db_topic = self.model(**topic_data, author_id=author.id)
        
        db.add(db_topic)
        db.commit()
        db.refresh(db_topic)

        # Create the initial post for the topic
        initial_post = ForumPost(
            content=post_content,
            topic_id=db_topic.id,
            author_id=author.id
        )
        db.add(initial_post)
        db.commit()
        db.refresh(db_topic) # Refresh topic to get the new post in the relationship

        return db_topic

    def get_multi_by_category(self, db: Session, *, category_id: int, skip: int = 0, limit: int = 100) -> List[ForumTopic]:
        return db.query(self.model).filter(self.model.category_id == category_id).offset(skip).limit(limit).all()


class CRUDForumPost(CRUDBase[ForumPost, ForumPostCreate, ForumPostUpdate]):
    def create_with_owner(self, db: Session, *, obj_in: ForumPostCreate, author_id: int) -> ForumPost:
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data, author_id=author_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_multi_by_topic(self, db: Session, *, topic_id: int, skip: int = 0, limit: int = 100) -> List[ForumPost]:
        return db.query(self.model).filter(self.model.topic_id == topic_id).order_by(self.model.created_at.asc()).offset(skip).limit(limit).all()


forum_category = CRUDForumCategory(ForumCategory)
forum_topic = CRUDForumTopic(ForumTopic)
forum_post = CRUDForumPost(ForumPost)
