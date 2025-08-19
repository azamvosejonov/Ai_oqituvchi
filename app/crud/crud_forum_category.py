from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.forum import ForumCategory
from app.schemas.forum import ForumCategoryCreate, ForumCategoryUpdate

class CRUDForumCategory(CRUDBase[ForumCategory, ForumCategoryCreate, ForumCategoryUpdate]):
    def get_by_name(self, db: Session, *, name: str) -> ForumCategory | None:
        return db.query(ForumCategory).filter(ForumCategory.name == name).first()

forum_category = CRUDForumCategory(ForumCategory)
