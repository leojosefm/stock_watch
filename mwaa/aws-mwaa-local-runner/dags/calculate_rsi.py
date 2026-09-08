import sys
import os
from airflow.models import DAG,Variable
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import logging
import psycopg2  
import yfinance as yf
from sqlalchemy import create_engine


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
    'calculate_rsi',
    default_args=default_args,
    description='A DAG to load S&P 500 companies into the database',
    schedule_interval=None,  # Runs daily
)


def get_pegy_ratio(ticker_symbol: str):
    try:
        stock = yf.Ticker(ticker_symbol)
        info = stock.info
        pe_ratio = info.get('trailingPE')
        growth_rate = info.get('earningsGrowth')
        dividend_yield = info.get('dividendYield', 0)
        if not pe_ratio or not growth_rate:
            return None
        pegy = pe_ratio / ((growth_rate * 100) + ((dividend_yield or 0) * 100))
        return round(pegy, 2)
    except Exception as e:
        logging.error(f"Error fetching PEGY for {ticker_symbol}: {e}")
        return None

def rsi_pegy_calculator(ticker):
    # Download the data for AAPL for the last 1 month, 1 day interval
    data = yf.download(ticker, period="1mo", interval="1d",auto_adjust=False)
    data.columns = data.columns.get_level_values(0)
    # Step 1: Calculate the difference in 'Close' price
    delta = data['Close'].diff()

    # Step 2: Separate the positive and negative changes
    gain = delta.where(delta > 0, 0)  # Keep only positive gains
    loss = -delta.where(delta < 0, 0)  # Keep only negative losses and make them positive

    # Step 3: Calculate the average gain and average loss (using a 14-period window)
    window_length = 14
    average_gain = gain.rolling(window=window_length, min_periods=1).mean()
    average_loss = loss.rolling(window=window_length, min_periods=1).mean()

    # Step 4: Calculate the Relative Strength (RS)
    rs = average_gain / average_loss

    # Step 5: Calculate the RSI using the formula
    rsi = 100 - (100 / (1 + rs))
    data['RSI'] = rsi
    data['ticker'] = ticker
    pegy = get_pegy_ratio(ticker)
    data['pegy_ratio'] = pegy

    if data.index.name == 'Date' or isinstance(data.index, pd.DatetimeIndex):
            data = data.reset_index()

    
    # Display the RSI values
    logging.info("sample historical data with RSI calculated")
    logging.info(data.tail(1))
    return data


def read_company(**kwargs):
    conn = psycopg2.connect(
        host=Variable.get('stock_db_host'),
        database=Variable.get('stock_db_name'),
        user=Variable.get('stock_db_user'),
        password=Variable.get('stock_db_password'),
        port="5432"
    )

    cur = conn.cursor()
    cur.execute("select max(c.id) as company_id from price_history ph join company c on ph.ticker = c.ticker_symbol")
    company_id = cur.fetchone()[0]
    logging.info(f"max company id in price history is {company_id}")
    logging.info(f" executing SQL: SELECT ticker_symbol FROM company where id >{company_id}")  
    cur.execute(f"SELECT ticker_symbol FROM company where id >{company_id}")
    result = cur.fetchall()
    ticker_list = [item[0] for item in result]
    kwargs['ti'].xcom_push(key="company_list", value=ticker_list)
    cur.close()

def load_historical_data(**kwargs):
    conn = psycopg2.connect(
        host=Variable.get('stock_db_host'),
        database=Variable.get('stock_db_name'),
        user=Variable.get('stock_db_user'),
        password=Variable.get('stock_db_password'),
        port="5432"
    )

    cur = conn.cursor()
    engine = create_engine(f"postgresql://{Variable.get('stock_db_user')}:{Variable.get('stock_db_password')}@{Variable.get('stock_db_host')}:5432/{Variable.get('stock_db_name')}")
    company_list = kwargs['ti'].xcom_pull(key='company_list', task_ids='read_company')
    for item in company_list:
        delete_query = f"DELETE FROM price_history where ticker='{item}'"
        logging.info(delete_query)
        cur.execute(delete_query)
        df = rsi_pegy_calculator(item)
        df.columns = ['date', 'open', 'high', 'low', 'close', 'adj_close', 'volume', 'RSI', 'ticker','pegy_ratio']  
        logging.info(f"inserting price history for {item}")
        df.to_sql('price_history', con=engine, if_exists='append', index=False)


with dag:
    t_read_company = PythonOperator(
        task_id='read_company',
        python_callable=read_company,
        provide_context=True,
    )

    t_load_history =  PythonOperator(
        task_id='load_historical_data',
        python_callable=load_historical_data,
        provide_context=True,
    )

    t_read_company >> t_load_history



