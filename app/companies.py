from models import Company  # Import your Company model
import pandas as pd
import requests
from sqlalchemy.orm import Session
import models  # Assuming you have a Company model
from database import SessionLocal



# Function to get S&P 500 tickers and company names
def get_sp500_companies():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    
    # Fetch the tables from the URL
    tables = pd.read_html(url)  
    
    # Extract the first table, which contains S&P 500 data
    sp500_table = tables[0]
    
    # Extract the relevant columns: 'Symbol' and 'Security'
    sp500_companies = sp500_table[['Symbol', 'Security']].values.tolist()
    
    return sp500_companies


# Function to insert companies into the database
def insert_sp500_companies(db: Session):
    sp500_companies = get_sp500_companies()
    
    for ticker_symbol, company_name in sp500_companies:
        # Check if the company already exists in the table to avoid duplicates
        existing_company = db.query(Company).filter(Company.ticker_symbol == ticker_symbol).first()
        
        if not existing_company:
            new_company = Company(
                company_name=company_name,
                ticker_symbol=ticker_symbol
            )
            db.add(new_company)
    
    db.commit()


def run():
    db = SessionLocal()
    insert_sp500_companies(db)
    db.close()
    
if __name__ == "__main__":
    run()