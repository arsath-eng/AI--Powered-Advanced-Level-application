# backend/app/routers/subjects.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from app import crud, models, schemas
from app.core.security import get_current_user, get_db

router = APIRouter(
    prefix="/admin/subjects",
    tags=["Admin - Subjects"],
    dependencies=[Depends(get_current_user)] 
)

@router.post("/", response_model=schemas.Subject, status_code=status.HTTP_201_CREATED)
def create_subject(subject: schemas.SubjectCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, model=models.Subject, schema=subject)

@router.get("/", response_model=list[schemas.Subject])
def read_subjects(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_items(db=db, model=models.Subject, skip=skip, limit=limit)

@router.get("/{item_id}", response_model=schemas.Subject)
def read_subject(item_id: uuid.UUID, db: Session = Depends(get_db)):
    db_item = crud.get_item(db=db, model=models.Subject, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return db_item

@router.patch("/{item_id}", response_model=schemas.Subject)
def update_subject(item_id: uuid.UUID, subject: schemas.SubjectBase, db: Session = Depends(get_db)):
    return crud.update_item(db=db, model=models.Subject, item_id=item_id, schema=subject)

@router.delete("/{item_id}", response_model=schemas.Subject)
def delete_subject(item_id: uuid.UUID, db: Session = Depends(get_db)):
    db_item = crud.delete_item(db=db, model=models.Subject, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Subject not found")
    return db_item