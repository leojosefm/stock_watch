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

@router.get("/pegy/{ticker}")
def get_pegy_by_ticker(ticker: str, db: Session = Depends(get_db)):
    result = crud.get_latest_pegy_by_ticker(db, ticker)
    if not result:
        raise HTTPException(status_code=404, detail=f"No data found for ticker {ticker}")
    return result


@router.get("/history/{ticker}")
def get_price_history(ticker: str, db: Session = Depends(get_db)):
    result = db.query(models.Pricehistory)\
        .filter(models.Pricehistory.ticker == ticker)\
        .order_by(models.Pricehistory.date.asc())\
        .all()
    return [{"date": r.date, "close": float(r.close)} for r in result]