from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.word import Word
from app.schemas.word import WordCreate, WordUpdate


class CRUDWord(CRUDBase[Word, WordCreate, WordUpdate]):
    pass


word = CRUDWord(Word)
