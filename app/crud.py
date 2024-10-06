from sqlalchemy.orm import Session
from . import models, schemas

# Create a new user
def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(username=user.username, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# Get a user by email
def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

# Add company to watchlist
def add_to_watchlist(db: Session, user_id: int, company_id: int):
    db_watchlist = models.Watchlist(user_id=user_id, company_id=company_id)
    db.add(db_watchlist)
    db.commit()
    db.refresh(db_watchlist)
    return db_watchlist
