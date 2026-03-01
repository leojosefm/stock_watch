import streamlit as st
import streamlit_authenticator as stauth
from google.oauth2 import id_token
from google.auth.transport import requests as  google_requests
from streamlit_url_fragment import get_fragment
from urllib.parse import urlparse, parse_qs
import random
import string
import requests 
import json
import logging
import pandas as pd
from dotenv import load_dotenv
import os
# import yfinance as yf


# API URL for creating a user
API_URL_BASE = "http://fastapi_app:8000/"

# Load environment variables
load_dotenv()

# Configure Google OAuth 2.0
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')


    
# Function to call FastAPI to create a user
def create_user(email: str):

    payload = json.dumps({
            "email": email
            })
    
    headers = {
    'Content-Type': 'application/json'
    }
    print (payload)

    response = requests.request("POST", API_URL_BASE+"users/", headers=headers, data=payload)
    if response.status_code == '200':
        st.write("User created successfully")



#Function to display triggered & pending alerts
def display_alerts(type,triggered_flag,watchlist_data,col_list):    
    st.subheader(f"{type.capitalize()}")
    #alerts = watchlist_data[watchlist_data['triggered'] == triggered_flag]
    #['company_name', 'ticker_symbol', 'rsi_threshold']
    # Guard: check if dataframe is empty or column missing
    if watchlist_data.empty:
        st.write(f"No {type}")
        return
    
    if 'triggered' not in watchlist_data.columns:
        st.error(f"Unexpected data format: {watchlist_data.columns.tolist()}")
        return
    

    alerts = watchlist_data[watchlist_data['triggered'] == triggered_flag]
    if not alerts.empty:
        # Create dataframe for pending alerts
        alerts = alerts.reset_index(drop=True)
        alerts.index += 1 
        alerts['Serial No.'] = alerts.index

        df = alerts[col_list]
        df.columns = df.columns.str.replace('_', ' ').str.title()
        st.dataframe(df)
    else:
        st.write(f"No {type}") 
                 
def get_user_id(email: str):
    payload = json.dumps({
            "email": email
            })
    
    headers = {
    'Content-Type': 'application/json'
    }
    print (payload)

    response = requests.request("GET", API_URL_BASE+f"users/{email}/id", headers=headers, data=payload)
    return response.json()

def fetch_watchlist(id: int):
    payload = json.dumps({
            "id": id
            })
    
    headers = {
    'Content-Type': 'application/json'
    }
    print (payload)

    try:
        response = requests.request(
            "GET", 
            API_URL_BASE+f"users/watchlist/{id}",
            timeout=5
        )
        if response.status_code == 200 and response.text:
            return response.json()
        return []       # 👈 return empty list if no content
    except Exception as e:
        st.error(f"Error fetching watchlist: {e}")
        return []

# Function to fetch companies
def fetch_companies():
    try:
        response = requests.get(f"{API_URL_BASE}companies/")
        if response.status_code == 200:
            return response.json()
        else:
            st.error("Failed to fetch companies.")
            return []
    except Exception as e:
        st.error(f"Error connecting to API: {e}")
        return []       

# Function to fetch latest PEGY ratio by ticker
def fetch_pegy_by_ticker(ticker: str):
    try:
        response = requests.get(f"{API_URL_BASE}companies/pegy/{ticker}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        st.error(f"Error fetching PEGY: {e}")
        return None

# Function to generate a random nonce
def generate_nonce(length=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def verify_google_sign_in(token):
    # Simulate token verification (replace this with your actual token verification)
    # For now, we assume the email is extracted from the token successfully
    return {"email": "user@example.com"}  # Replace with actual token logic


# Create a function to verify the token received from Google
def verify_token(token):
    try:
        idinfo = id_token.verify_oauth2_token(token, google_requests.Request(), CLIENT_ID)
        print (idinfo)
        return idinfo
    except ValueError:
        return None
    
# def get_pegy_ratio(ticker_symbol: str):
#     try:
#         stock = yf.Ticker(ticker_symbol)
#         info = stock.info

#         pe_ratio = info.get('trailingPE')
#         growth_rate = info.get('earningsGrowth')       # as decimal e.g. 0.15 = 15%
#         dividend_yield = info.get('dividendYield', 0)  # as decimal e.g. 0.02 = 2%

#         if not pe_ratio or not growth_rate:
#             return None

#         # Convert decimals to percentages
#         growth_rate_pct = growth_rate * 100
#         dividend_yield_pct = (dividend_yield or 0) * 100

#         pegy = pe_ratio / (growth_rate_pct + dividend_yield_pct)
#         return round(pegy, 2)

#     except Exception as e:
#         print(f"Error fetching PEGY for {ticker_symbol}: {e}")
#         return None

# Function to display the login page
def show_login_page():
    st.set_page_config(page_title="Stock Monitor - Login", layout="wide")
    st.title("📊 Stock Monitor")
    st.markdown("### Sign in to monitor your favorite stocks.")
    st.markdown("#### Login using Gmail")
    st.markdown(f'<a href="https://accounts.google.com/o/oauth2/v2/auth?client_id={CLIENT_ID}&redirect_uri=http://localhost:8501/&response_type=id_token&scope=email profile&nonce={st.session_state.nonce}" target="_self">Sign in with Gmail</a>', unsafe_allow_html=True)

    current_value = get_fragment()
    if current_value:
            # Remove the leading '#' character
            parsed_string = current_value.lstrip('#')
            # Parse the query string
            parsed_query = parse_qs(parsed_string)

            # Extract the access token
            access_token = parsed_query.get('id_token', [None])[0]


            if access_token:
                user_info = verify_token(access_token)

                if user_info:
                    st.session_state['logged_in'] = True
                    st.session_state['user_email'] = user_info['email']
                    
                    # Logic to check if the user exists in your database
                    email = user_info['email']
                    # Call the FastAPI endpoint to check/add the user
                    if email:
                        create_user(email)
                    st.rerun()

# Function to display the main page after login
def show_main_page():
    st.set_page_config(page_title="Stock Monitor - Dashboard", layout="wide")
    st.title("📊 Stock Monitor")
    st.markdown("### Welcome to Your Watchlist")
    st.write(f"Hello, **{st.session_state['user_email']}**!")

    st.markdown("---")

    st.markdown(
        """
        <style>
        .top-right-button {
            position: absolute;
            top: 10px;
            right: 10px;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.write(f'''
<div class="top-right-button">
<a target="_self" href="http://localhost:8501">
    <button>Log out</button>
</a>
</div>
''', unsafe_allow_html=True)
    
    watchlist_data = fetch_watchlist(get_user_id(st.session_state['user_email'])['id'])

    if not watchlist_data:
        watchlist_data = pd.DataFrame()
    elif isinstance(watchlist_data, list):
        watchlist_data = pd.DataFrame(watchlist_data)

    st.markdown("---")

    # ✅ Add New Company Section
    st.subheader("Add New Company")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        new_company_name = st.text_input("Company Name")
    with col2:
        new_ticker = st.text_input("Ticker Symbol")
    with col3:
        st.write("")
        st.write("")
        add_company_btn = st.button("Add Company")

    if add_company_btn:
        if new_company_name and new_ticker:
            response = requests.post(
                f"{API_URL_BASE}companies/",
                params={
                    "company_name": new_company_name,
                    "ticker_symbol": new_ticker.upper()
                }
            )
            if response.status_code == 200:
                st.success(f"{new_company_name} ({new_ticker.upper()}) added!")
                st.rerun()
            else:
                st.error(f"Failed to add company: {response.text}")
        else:
            st.warning("Please fill in both fields.")

    st.markdown("---")

    # ✅ Add to Watchlist Section
    st.subheader("Add to Watchlist")
    companies_data = fetch_companies()

    if not companies_data:
        st.warning("No companies yet. Please add a company above first.")
    else:
        company_ticker_mapping = {company['company_name']: company['ticker_symbol'] for company in companies_data}

        col1, col2 = st.columns([2, 1])
        with col1:
            company_name = st.selectbox("Company", options=company_ticker_mapping.keys(), key="watchlist_company")
        with col2:
            ticker_symbol = st.selectbox("Ticker Symbol", options=company_ticker_mapping[company_name], key="watchlist_ticker")

        rsi_threshold = st.number_input("RSI Threshold", min_value=0, max_value=100)
        

        pegy_data = fetch_pegy_by_ticker(ticker_symbol)
        if pegy_data:
            col1, col2 = st.columns(2)
            with col1:
                rsi_value = pegy_data.get('RSI')
                if rsi_value is not None:
                    if rsi_value < 30:
                        rsi_color = '#22c55e'
                    elif rsi_value > 70:
                        rsi_color = '#ef4444'
                    else:
                        rsi_color = '#94a3b8'
                    st.caption("Latest RSI")
                    st.markdown(f"<p style='font-size:28px; font-weight:700; color:{rsi_color}; margin:0'>{round(rsi_value, 2)}</p>", unsafe_allow_html=True)
                else:
                    st.caption("Latest RSI")
                    st.markdown("N/A")
                st.markdown("""
                    <small>
                    <span style='color:#22c55e'>● Below 30</span> — oversold, potential buy<br>
                    <span style='color:#94a3b8'>● 30 to 50</span> — recovering, worth watching<br>
                    <span style='color:#ef4444'>● Above 70</span> — overbought, avoid buying
                    </small>
                """, unsafe_allow_html=True)
            with col2:
                pegy_value = pegy_data.get('pegy_ratio')
                if pegy_value is not None:
                    if pegy_value < 0:
                        pegy_color = '#ef4444'
                    elif pegy_value < 1.0:
                        pegy_color = '#22c55e'
                    elif pegy_value > 2.0:
                        pegy_color = '#ef4444'
                    else:
                        pegy_color = '#94a3b8'
                    st.caption("Latest PEGY Ratio")
                    st.markdown(f"<p style='font-size:28px; font-weight:700; color:{pegy_color}; margin:0'>{round(pegy_value, 2)}</p>", unsafe_allow_html=True)
                else:
                    st.caption("Latest PEGY Ratio")
                    st.markdown("N/A")
                st.markdown("""
                    <small>
                    <span style='color:#22c55e'>● Below 1.0</span> — undervalued, strong buy<br>
                    <span style='color:#94a3b8'>● 1.0 to 2.0</span> — fairly valued, acceptable<br>
                    <span style='color:#ef4444'>● Above 2.0</span> — overvalued, be cautious
                    </small>
                """, unsafe_allow_html=True)
        else:
            st.info("No price data available for this ticker yet.")


        if st.button("Add to Watchlist"):
            user_id = get_user_id(st.session_state['user_email'])['id']
            payload = {
                "user_id": user_id,
                "company_name": company_name,
                "ticker_symbol": ticker_symbol,
                "rsi_threshold": rsi_threshold
            }
            response = requests.post(
                f"{API_URL_BASE}users/watchlist/",
                headers={'Content-Type': 'application/json'},
                data=json.dumps(payload)
            )
            if response.status_code == 200:
                st.success(f"{company_name}, RSI {rsi_threshold} added to watchlist!")
                st.rerun()
            elif response.status_code == 400:
                st.error(response.json().get('detail'))
            else:
                st.error("Error adding to watchlist.")

    # Then in display_alerts, add pegy_ratio to col_list:
    display_alerts("pending alerts", False, watchlist_data, 
        ['Serial No.','company_name', 'ticker_symbol', 'rsi_threshold', 'pegy_ratio', 'added_datetime'])
    display_alerts("triggered alerts", True, watchlist_data, 
    ['Serial No.','company_name', 'ticker_symbol', 'rsi_threshold', 'pegy_ratio', 'triggered_datetime'])

def main():
    # Create a simple Streamlit app with authentication,
# Initialize session state
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
    if 'nonce' not in st.session_state:
        st.session_state.nonce = generate_nonce()

    # Display the appropriate page based on login status
    if st.session_state['logged_in']:
        show_main_page()  # Show the second page after login
    else:
        show_login_page()  # Show the login page if not logged in

    # Create a login button
    # if not st.session_state['logged_in']:
    #     st.markdown(f'<a href="https://accounts.google.com/o/oauth2/v2/auth?client_id={CLIENT_ID}&redirect_uri=http://localhost:8501/&response_type=id_token&scope=email profile&nonce={st.session_state.nonce}" target="_self">Sign in with Gmail</a>', unsafe_allow_html=True)



if __name__ == "__main__":
    main()
        
