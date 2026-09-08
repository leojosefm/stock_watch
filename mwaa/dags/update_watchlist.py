import sys
import os
from airflow.models import DAG,Variable
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
import pandas as pd
import logging
import psycopg2  
from airflow.operators.email import EmailOperator


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
    'update_watchlist',
    default_args=default_args,
    description='A DAG to load S&P 500 companies into the database',
    schedule_interval=None,  # Runs daily
)

def find_rsi_threshold_reached(**kwargs):
    conn = psycopg2.connect(
        host=Variable.get('stock_db_host'),
        database=Variable.get('stock_db_name'),
        user=Variable.get('stock_db_user'),
        password=Variable.get('stock_db_password'),
        port="5432"
    )
    sql_query = """
            select 
            id as user_id,ticker_symbol,rsi_threshold,"RSI",date
            from 
            (
            select u.email , u.id,w.company_name ,w.ticker_symbol , w.rsi_threshold ,ph."RSI", w.added_datetime 
            ,ph.date
            ,row_number() over(partition by u.id,w.ticker_symbol,w.rsi_threshold order by ph.date asc) rn
            from watchlist w 
            join public.user u 
            on
            w.user_id = u.id 
            left join price_history ph 
            on w.ticker_symbol = ph.ticker 
            where date_trunc('day',w.added_datetime)  <= ph."date" 
            and w.rsi_threshold >= ph."RSI" 
            and w.triggered = False
            ) where rn =1
            """
    cur = conn.cursor()
    cur.execute(sql_query)
    tmp_watchlist = cur.fetchall()
    kwargs['ti'].xcom_push(key="rsi_threshold_reached", value=tmp_watchlist)
    cur.close()

        
def update_watchlist(**kwargs):
    conn = psycopg2.connect(
        host=Variable.get('stock_db_host'),
        database=Variable.get('stock_db_name'),
        user=Variable.get('stock_db_user'),
        password=Variable.get('stock_db_password'),
        port="5432"
    )
    tmp_watchlist = kwargs['ti'].xcom_pull(key='rsi_threshold_reached', task_ids='find_rsi')
    if not tmp_watchlist:
        logging.info("No alerts")
        return True
    cur = conn.cursor()
    for i in range(0,len(tmp_watchlist)):
        upd_query = f"""
        update watchlist
        set rsi_triggered = {tmp_watchlist[i][3]}, triggered_datetime = '{tmp_watchlist[i][4]}' , triggered = True
        where user_id = {tmp_watchlist[i][0]}
        and ticker_symbol = '{tmp_watchlist[i][1]}'
        and rsi_threshold = {tmp_watchlist[i][2]}
        """
        logging.info(upd_query)
        cur.execute(upd_query)
    conn.commit()
    cur.close()
    conn.close()


with dag:
    t_find_rsi_threshold_reached = PythonOperator(
        task_id='find_rsi',
        python_callable=find_rsi_threshold_reached,
        provide_context=True,
    )

    t_update_watchlist = PythonOperator(
        task_id='update_watchlist',
        python_callable=update_watchlist,
        provide_context=True,
    )



t_find_rsi_threshold_reached >>t_update_watchlist





