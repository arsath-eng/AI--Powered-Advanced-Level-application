# backend/app/routers/past_papers.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from app import crud, models, schemas
from app.core.security import get_current_user, get_db

router = APIRouter(
    prefix="/admin/past-papers",
    tags=["Admin - Past Papers"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=schemas.PastPaperQuestion, status_code=status.HTTP_201_CREATED)
def create_past_paper_question(item: schemas.PastPaperQuestionCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, model=models.PastPaperQuestion, schema=item)

@router.get("/", response_model=list[schemas.PastPaperQuestion])
def read_past_paper_questions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_items(db=db, model=models.PastPaperQuestion, skip=skip, limit=limit)

@router.get("/{item_id}", response_model=schemas.PastPaperQuestion)
def read_past_paper_question(item_id: uuid.UUID, db: Session = Depends(get_db)):
    db_item = crud.get_item(db=db, model=models.PastPaperQuestion, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_item

@router.patch("/{item_id}", response_model=schemas.PastPaperQuestion)
def update_past_paper_question(item_id: uuid.UUID, item: schemas.PastPaperQuestionUpdate, db: Session = Depends(get_db)):
    return crud.update_item(db=db, model=models.PastPaperQuestion, item_id=item_id, schema=item)

@router.delete("/{item_id}", response_model=schemas.PastPaperQuestion)
def delete_past_paper_question(item_id: uuid.UUID, db: Session = Depends(get_db)):
    db_item = crud.delete_item(db=db, model=models.PastPaperQuestion, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return db_item

# Add this new function to backend/app/routers/past_papers.py

@router.post("/bulk", response_model=list[schemas.PastPaperQuestion], status_code=status.HTTP_201_CREATED)
def create_bulk_past_paper_questions(questions: list[schemas.PastPaperQuestionCreate], db: Session = Depends(get_db)):
    created_questions = []
    for question_schema in questions:
        # We use the generic create_item function for each question in the list
        created_question = crud.create_item(db=db, model=models.PastPaperQuestion, schema=question_schema)
        created_questions.append(created_question)
    return created_questions