from sqlalchemy.orm import Session
from . import models, schemas
import logging
from sqlalchemy.exc import IntegrityError
import yfinance as yf


def get_pegy_ratio(ticker_symbol: str):
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        pe_ratio = info.get('trailingPE')
        growth_rate = info.get('earningsGrowth')
        dividend_yield = info.get('dividendYield', 0)
        if not pe_ratio or not growth_rate:
            return None
        pegy = pe_ratio / ((growth_rate * 100) + ((dividend_yield or 0) * 100))
        return round(pegy, 2)
    except Exception as e:
        logging.error(f"Error fetching PEGY for {ticker_symbol}: {e}")
        return None
    
def update_pegy_ratio(db: Session, watchlist_id: int, ticker_symbol: str):
    pegy = get_pegy_ratio(ticker_symbol)
    if pegy is not None:
        db.query(models.Watchlist).filter(
            models.Watchlist.id == watchlist_id
        ).update({"pegy_ratio": pegy})
        db.commit()
    return pegy

def refresh_pegy_for_user(db: Session, user_id: int):
    watchlists = get_watchlist_by_user_id(db, user_id)
    for item in watchlists:
        if item.pegy_ratio is None:           # fetch if empty
            update_pegy_ratio(db, item.id, item.ticker_symbol)
    return get_watchlist_by_user_id(db, user_id)

# Create a new user
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(email=user.email)
    logging.info(db_user)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get a user by email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Get a user by email
def get_companies(db: Session):
    companies =  db.query(models.Company).all()
    return [{"company_name": company.name, "ticker_symbol": company.ticker_symbol} for company in companies]


# Function to retrieve a watchlist by user ID
def get_watchlist_by_user_id(db: Session, user_id: int):
    return db.query(models.Watchlist).filter(models.Watchlist.user_id == user_id).all()


# Add company to watchlist
def add_to_watchlist(db: Session, watchlist: schemas.WatchlistCreate):
    db_watchlist = models.Watchlist( user_id = watchlist.user_id,company_name=watchlist.company_name, ticker_symbol=watchlist.ticker_symbol, rsi_threshold = watchlist.rsi_threshold)
    db.add(db_watchlist)
    try:
        db.commit()
        db.refresh(db_watchlist)
        return db_watchlist
    except IntegrityError:
        db.rollback()
        return {"error": "A pending alert already exists for this threshold value for the user"}
    
def create_company(db: Session, company_name: str, ticker_symbol: str):
    company = models.Company(name=company_name, ticker_symbol=ticker_symbol)
    db.add(company)
    db.commit()
    db.refresh(company)
    return company