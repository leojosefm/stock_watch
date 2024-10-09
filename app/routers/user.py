from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, models
from ..database import get_db


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

@router.post("/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        #raise HTTPException(status_code=400, detail="Email already registered")
        return db_user
    else:
        return crud.create_user(db=db, user=user)

@router.post("/watchlist")
def add_to_watchlist(user_id: int, company_id: int, rsi_threshold: int, db: Session = Depends(get_db)):
    return crud.add_to_watchlist(db=db, user_id=user_id, company_id=company_id,rsi_threshold=rsi_threshold)


@router.get("/{email}/id",response_model=schemas.User)
def get_user_id(email:str, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email= email)
    if db_user:
        #raise HTTPException(status_code=400, detail="Email already registered")
        return db_user
    

@router.get("/watchlist/{user_id}")
def get_watchlists(user_id: int, db: Session = Depends(get_db)):
    watchlists = crud.get_watchlist_by_user_id(db, user_id= user_id)
    return watchlists