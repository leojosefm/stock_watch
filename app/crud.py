from sqlalchemy.orm import Session
from . import models, schemas
import logging
from sqlalchemy.exc import IntegrityError

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