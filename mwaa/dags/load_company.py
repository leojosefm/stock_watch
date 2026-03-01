import sys
import os
from airflow.models import DAG,Variable
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import logging
import psycopg2  
import requests


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 10, 11),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
     'catchup':False
}

dag = DAG(
    'load_companies',
    default_args=default_args,
    description='A DAG to load S&P 500 companies into the database',
    schedule_interval=None
)

# Function to get S&P 500 tickers and company names
def get_sp500_companies():
    url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'   ## User agent header to mimic a browser request, some websites block requests without it
        }

    response = requests.get(url, headers=headers)

    # Fetch the tables from the URL
    tables = pd.read_html(response.text)  

    # Extract the first table, which contains S&P 500 data
    sp500_table = tables[0]
    
    # Extract the relevant columns: 'Symbol' and 'Security'
    sp500_companies = sp500_table[['Symbol', 'Security']].values.tolist()
    logging.info(sp500_companies)
    return sp500_companies


# Function to insert companies into the database
def insert_sp500_companies():
    conn = psycopg2.connect(
        host=Variable.get('stock_db_host'),
        database=Variable.get('stock_db_name'),
        user=Variable.get('stock_db_user'),
        password=Variable.get('stock_db_password'),
        port="5432"
    )

    cur = conn.cursor()

    sp500_companies = get_sp500_companies()
    for ticker_symbol, company_name in sp500_companies:
        cur.execute("SELECT 1 FROM company WHERE ticker_symbol = %s", (ticker_symbol,))
        exists = cur.fetchone()
        #logging.info(exists)
        if not exists:
            cur.execute(
                "INSERT INTO company (name, ticker_symbol) VALUES (%s, %s)",
                (company_name, ticker_symbol)
            )
    conn.commit()
    cur.close()
    conn.close()

with dag:
    load_companies_task = PythonOperator(
        task_id='load_companies',
        python_callable=insert_sp500_companies,
        provide_context=True,
    )
