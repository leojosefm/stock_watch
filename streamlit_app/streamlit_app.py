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


# API URL for creating a user
API_URL_BASE = "http://fastapi_app:8000/"

# Configure Google OAuth 2.0
CLIENT_ID = '1012644879713-sj9mtjginh6oqmcm3a2ju3vv5fah94cl.apps.googleusercontent.com'
CLIENT_SECRET = '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'




    
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
    alerts = watchlist_data[watchlist_data['triggered'] == triggered_flag]
    #['company_name', 'ticker_symbol', 'rsi_threshold']
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

    response = requests.request("GET", API_URL_BASE+f"users/watchlist/{id}", headers=headers, data=payload)
    return response.json()

# Function to fetch companies
def fetch_companies():
    response = requests.get(f"{API_URL_BASE}companies/")
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch companies.")
        return []



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
    # Display user info
    st.write(f"Hello, **{st.session_state['user_email']}**!")
    

    st.markdown("---")

    # Custom CSS to move the logout button to the top right corner
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
    <button>
        Log out
    </button>
</a>
</div>
''',
unsafe_allow_html=True
)
    
    watchlist_data = fetch_watchlist(get_user_id(st.session_state['user_email'])['id'])

    # Ensure watchlist_data is a DataFrame
    if isinstance(watchlist_data, list):
        watchlist_data = pd.DataFrame(watchlist_data)
    # Create two columns to display alert
    col1, col2 = st.columns(2)

    with col1:
        display_alerts("pending alerts",False,watchlist_data, ['Serial No.','company_name', 'ticker_symbol', 'rsi_threshold','added_datetime'])
    with col2:
        display_alerts("triggered alerts",True,watchlist_data,['Serial No.','company_name', 'ticker_symbol', 'rsi_threshold','triggered_datetime'])


    # Add to Watchlist Section
    st.subheader("Add to Watchlist")
    companies_data = fetch_companies()

# Extract company nmes and ticker symbols for the autocomplete feature
    # Extract company names and ticker symbols for the autocomplete feature
    company_names = [company['company_name'] for company in companies_data]
    ticker_symbols = [company['ticker_symbol'] for company in companies_data]
    company_ticker_mapping = {company['company_name']: company['ticker_symbol'] for company in companies_data}

    col1, col2 = st.columns([2, 1])
    with col1:
        company_name = st.selectbox("Company", options=company_ticker_mapping.keys(), key=1)
    with col2:
        ticker_symbol = st.selectbox("Ticker Symbol", options=company_ticker_mapping[company_name], key=2)

    rsi_threshold = st.number_input("RSI Threshold", min_value=0, max_value=100)

    submit_button = st.button(label='Add')

    if submit_button:
        user_id = get_user_id(st.session_state['user_email'])['id']
        payload = {
            "user_id": user_id,
            "company_name": company_name,
            "ticker_symbol": ticker_symbol,
            "rsi_threshold": rsi_threshold
        }

        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.post(f"{API_URL_BASE}users/watchlist/", headers=headers, data=json.dumps(payload))

        if response.status_code == 200:
            st.success(f"Company {company_name}, RSI {rsi_threshold} added to alerts.")
        elif response.status_code == 400:
            st.error(response.json().get('detail'))
        else:
            st.error("Error adding to alerts.")


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
        
