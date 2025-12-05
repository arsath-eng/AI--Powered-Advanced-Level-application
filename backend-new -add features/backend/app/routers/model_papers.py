# backend/app/routers/model_papers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from app import crud, models, schemas
from app.core.security import get_current_user, get_db

router = APIRouter(
    prefix="/admin/model-papers",
    tags=["Admin - Model Papers"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=schemas.ModelPaperQuestion, status_code=status.HTTP_201_CREATED)
def create_model_paper_question(item: schemas.ModelPaperQuestionCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, model=models.ModelPaperQuestion, schema=item)

@router.get("/", response_model=list[schemas.ModelPaperQuestion])
def read_model_paper_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_items(db=db, model=models.ModelPaperQuestion, skip=skip, limit=limit)

@router.get("/{item_id}", response_model=schemas.ModelPaperQuestion)
def read_model_paper_question(item_id: uuid.UUID, db: Session = Depends(get_db)):
    db_item = crud.get_item(db=db, model=models.ModelPaperQuestion, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_item

@router.patch("/{item_id}", response_model=schemas.ModelPaperQuestion)
def update_model_paper_question(item_id: uuid.UUID, item: schemas.ModelPaperQuestionUpdate, db: Session = Depends(get_db)):
    return crud.update_item(db=db, model=models.ModelPaperQuestion, item_id=item_id, schema=item)

@router.delete("/{item_id}", response_model=schemas.ModelPaperQuestion)
def delete_model_paper_question(item_id: uuid.UUID, db: Session = Depends(get_db)):
    db_item = crud.delete_item(db=db, model=models.ModelPaperQuestion, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_item