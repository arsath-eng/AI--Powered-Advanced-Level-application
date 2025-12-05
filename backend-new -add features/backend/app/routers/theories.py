# backend/app/routers/theories.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import uuid
from app import crud, models, schemas
from app.core.security import get_current_user, get_db

router = APIRouter(
    prefix="/admin/theories",
    tags=["Admin - Theories"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=schemas.Theory, status_code=status.HTTP_201_CREATED)
def create_theory(item: schemas.TheoryCreate, db: Session = Depends(get_db)):
    return crud.create_item(db=db, model=models.Theory, schema=item)

@router.get("/", response_model=list[schemas.Theory])
def read_theories(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_items(db=db, model=models.Theory, skip=skip, limit=limit)

@router.get("/{item_id}", response_model=schemas.Theory)
def read_theory(item_id: uuid.UUID, db: Session = Depends(get_db)):
    db_item = crud.get_item(db=db, model=models.Theory, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Theory not found")
    return db_item

@router.patch("/{item_id}", response_model=schemas.Theory)
def update_theory(item_id: uuid.UUID, item: schemas.TheoryUpdate, db: Session = Depends(get_db)):
    return crud.update_item(db=db, model=models.Theory, item_id=item_id, schema=item)

@router.delete("/{item_id}", response_model=schemas.Theory)
def delete_theory(item_id: uuid.UUID, db: Session = Depends(get_db)):
    db_item = crud.delete_item(db=db, model=models.Theory, item_id=item_id)
    if db_item is None:
        raise HTTPException(status_code=404, detail="Theory not found")
    return db_item