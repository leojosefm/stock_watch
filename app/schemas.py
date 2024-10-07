from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
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

class WatchlistCreate(BaseModel):
    user_id: int
    company_id: int

class Watchlist(BaseModel):
    id: int
    user_id: int
    company_id: int
    rsi_threshold: int


    class Config:
        orm_mode = True
