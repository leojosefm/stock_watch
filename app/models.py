from sqlalchemy import Column, Integer, String, Boolean, DateTime , Date, Numeric, func
from .database import Base
from datetime import datetime



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
    triggered = Column(Boolean, default = False)
    added_datetime  =  Column(DateTime, default=func.now())
    triggered_datetime = Column(DateTime, default=datetime(9999, 12, 31))

Class Pricehistory(Base):
    __tablename__ = 'price_history'

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date)
    open = Column(Numeric)
    high = Column(Numeric)
    low = Column(Numeric)
    close = Column(Numeric)
    adj_close = Column(Numeric)
    volume = Column(Integer)
    RSI = Column(Numeric)
    ticker = Column(String)

