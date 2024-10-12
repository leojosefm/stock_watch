from sqlalchemy import Column, Integer, String
from .database import Base



class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=False)
    
class Company(Base):
    __tablename__ = 'company'

    id = Column(Integer, primary_key=True, index=False)
    name = Column(String, index=False)
    ticker_symbol = Column(String, unique=True, index=False)

class Watchlist(Base):
    __tablename__ = 'watchlist'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    company_name = Column(String)
    ticker_symbol = Column(String)
    rsi_threshold = Column(Integer)
