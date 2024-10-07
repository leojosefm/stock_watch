from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    email: str
    name: str

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
    company_id: int
    rsi_threshold: int

class WatchlistCreate(WatchlistBase):
    pass

class Watchlist(WatchlistBase):
    id: int

    class Config:
        orm_mode = True

