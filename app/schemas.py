from pydantic import BaseModel
from datetime import datetime,date
from typing import Optional


# Base - shared fields
# Create - incoming requests
# model_name as it is - Outgoing response, ORM Mode - allows Pydantic to read the response - Validates type is correct before it goes
## out of the API


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    pass

class User(UserBase):
    id: int

    class Config:
        orm_mode = True

class CompanyBase(BaseModel):
    name: str
    ticker_symbol: str

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int

    class Config:
        orm_mode = True

class WatchlistBase(BaseModel):
    user_id: int
    company_name: str
    ticker_symbol: str
    rsi_threshold: int
    triggered: bool = False
    added_datetime: datetime = datetime.now()
    triggered_datetime: datetime = datetime(9999, 12, 31)
    rsi_triggered: Optional[float] = None
    pegy_ratio: Optional[float] = None


class WatchlistCreate(WatchlistBase):
    pass

class Watchlist(WatchlistBase):
    id: int

    class Config:
        orm_mode = True

class PricehistoryBase(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    adj_close: float
    volume: int
    ticker: str
    pegy_ratio: float


class PricehistoryBase(PricehistoryBase):
    pass

class Pricehistory(PricehistoryBase):
    id: int

    class Config:
        orm_mode = True

class PegyRatioLatestView(BaseModel):  ## only response no need to expose all the price columns since that's all Streamlit needs to display
    ticker: str
    date: date
    RSI: Optional[float] = None
    pegy_ratio: Optional[float] = None

    class Config:
        orm_mode = True

        