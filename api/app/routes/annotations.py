from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session, sessionmaker
from db.mariadb_connector import engine as mariadb_engine
from typing import List
from models.annotation import Annotation
from schemas.publication_annotation import PublicationAnnotationCreate, PublicationAnnotationUpdate, \
    PublicationAnnotationSchema
from api.app.routes.authentication import verify_token

annotation_router = APIRouter(
    prefix="/annotations",
    tags=["annotations"],
    responses={
        404: {"description": "Not found"},
        403: {"description": "Forbidden"},
        401: {"description": "Unauthorized"},
    },
)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mariadb_engine)


# Dependency for getting DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@annotation_router.post("/", response_model=PublicationAnnotationSchema, status_code=status.HTTP_201_CREATED)
def create_annotation(
        annotation: PublicationAnnotationCreate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token),
):
    """
    Create a new publication annotation.
    """
    new_annotation = Annotation(**annotation.dict())
    db.add(new_annotation)
    db.commit()
    db.refresh(new_annotation)
    return new_annotation


@annotation_router.get("/{annotation_id}", response_model=PublicationAnnotationSchema)
def get_annotation(
        annotation_id: int,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token),
):
    """
    Retrieve a publication annotation by ID.
    """
    annotation = db.query(Annotation).filter(PublicationAnnotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Annotation not found")
    return annotation


@annotation_router.patch("/{annotation_id}", response_model=PublicationAnnotationSchema)
def update_annotation_patch(
        annotation_id: int,
        annotation_update: PublicationAnnotationUpdate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token),
):
    """
    Partially update a publication annotation using PATCH.
    """
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Annotation not found")

    update_data = annotation_update.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(annotation, key, value)

    db.commit()
    db.refresh(annotation)
    return annotation


@annotation_router.put("/{annotation_id}", response_model=PublicationAnnotationSchema)
def update_annotation_put(
        annotation_id: int,
        annotation_update: PublicationAnnotationCreate,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token),
):
    """
    Fully update a publication annotation using PUT.
    """
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Annotation not found")

    for key, value in annotation_update.dict().items():
        setattr(annotation, key, value)

    db.commit()
    db.refresh(annotation)
    return annotation


@annotation_router.delete("/{annotation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_annotation(
        annotation_id: int,
        db: Session = Depends(get_db),
        token: str = Depends(verify_token),
):
    """
    Delete a publication annotation by ID.
    """
    annotation = db.query(Annotation).filter(Annotation.id == annotation_id).first()
    if not annotation:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Annotation not found")

    db.delete(annotation)
    db.commit()
    return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"detail": "Annotation deleted"})
