from typing import List, Optional
from sqlalchemy.orm import Session
import uuid

from app.crud.base import CRUDBase
from app.models import Certificate, User
from app.schemas import CertificateCreate, CertificateUpdate
from app.utils.pdf_generator import create_certificate_pdf

class CRUDCertificate(CRUDBase[Certificate, CertificateCreate, CertificateUpdate]):
    def get_multi_by_user(
        self, db: Session, *, user_id: int, skip: int = 0, limit: int = 100
    ) -> List[Certificate]:
        return (
            db.query(self.model)
            .filter(Certificate.user_id == user_id)
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_by_user_and_course(self, db: Session, *, user_id: int, course_id: int) -> Optional[Certificate]:
        return db.query(self.model).filter(self.model.user_id == user_id, self.model.course_id == course_id).first()

    def create_with_pdf(self, db: Session, *, obj_in: CertificateCreate, user: User) -> Certificate:
        """
        Create a certificate record and generate the PDF file.
        """
        # 1. Create the certificate record to get an ID
        verification_code = str(uuid.uuid4())
        db_cert = self.model(**obj_in.model_dump(), verification_code=verification_code)
        db.add(db_cert)
        db.commit()
        db.refresh(db_cert)

        # 2. Generate PDF
        pdf_path = create_certificate_pdf(
            user_name=user.full_name or user.username,
            course_name=obj_in.course_name,
            level_completed=obj_in.level_completed,
            certificate_id=db_cert.id,
            issue_date=db_cert.issue_date.strftime("%Y-%m-%d"),
            verification_code=verification_code
        )

        # 3. Update the certificate record with the PDF path
        update_data = CertificateUpdate(file_path=pdf_path)
        db_cert = self.update(db=db, db_obj=db_cert, obj_in=update_data)

        return db_cert

certificate = CRUDCertificate(Certificate)
