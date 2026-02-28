from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import crud, schemas, models
from ..database import get_db

router = APIRouter(
    prefix="/companies",
    tags=["companies"]
)

@router.get("/")
def get_companies(db: Session = Depends(get_db)):
    db_companies = crud.get_companies(db)
    if db_companies:
        #raise HTTPException(status_code=400, detail="Email already registered")
        return db_companies
    


@router.post("/")
def create_company(company_name: str, ticker_symbol: str, db: Session = Depends(get_db)):
    return crud.create_company(db, company_name, ticker_symbol)  # 👈 cleaner