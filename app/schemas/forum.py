from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List, Optional

from .user import User

# ===================================================================
# Forum Category Schemas
# ===================================================================

class ForumCategoryBase(BaseModel):
    name: str
    description: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class ForumCategoryCreate(ForumCategoryBase):
    pass

class ForumCategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class ForumCategoryInDBBase(ForumCategoryBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True,
    )

class ForumCategory(ForumCategoryInDBBase):
    pass

# ===================================================================
# Forum Post Schemas
# ===================================================================

class ForumPostBase(BaseModel):
    content: str

    model_config = ConfigDict(
        from_attributes=True,
    )

class ForumPostCreate(ForumPostBase):
    topic_id: int
    parent_id: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class ForumPostUpdate(BaseModel):
    content: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class ForumPostInDBBase(ForumPostBase):
    id: int
    topic_id: int
    author_id: int
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_edited: bool
    author: User

    model_config = ConfigDict(
        from_attributes=True,
    )

class ForumPost(ForumPostInDBBase):
    replies: List['ForumPost'] = []

    model_config = ConfigDict(
        from_attributes=True,
    )

# ===================================================================
# Forum Topic Schemas
# ===================================================================

class ForumTopicBase(BaseModel):
    title: str
    description: Optional[str] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class ForumTopicCreate(ForumTopicBase):
    category_id: int
    content: str  # For the first post in the topic

    model_config = ConfigDict(
        from_attributes=True,
    )

class ForumTopicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_closed: Optional[bool] = None
    category_id: Optional[int] = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class ForumTopicInDBBase(ForumTopicBase):
    id: int
    author_id: int
    category_id: int
    created_at: datetime
    is_pinned: bool
    is_closed: bool
    author: User
    category: ForumCategory

    model_config = ConfigDict(
        from_attributes=True,
    )

class ForumTopic(ForumTopicInDBBase):
    posts: List[ForumPost] = []

    model_config = ConfigDict(
        from_attributes=True,
    )

class ForumTopicWithStats(ForumTopic):
    posts_count: int
    last_post: Optional[ForumPost] = None

    model_config = ConfigDict(
        from_attributes=True,
    )
