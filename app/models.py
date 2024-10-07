from sqlalchemy import Column, Integer, String
from .database import Base



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=False)
    email = Column(String, unique=True, index=False)
    name = Column(String)

class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True, index=False)
    name = Column(String, index=False)
    ticker_symbol = Column(String, unique=True, index=False)

class Watchlist(Base):
    __tablename__ = 'watchlists'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    company_id = Column(Integer)
    rsi_threshold = Column(Integer)
