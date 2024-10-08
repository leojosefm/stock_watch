import streamlit as st
import streamlit_authenticator as stauth
from google.oauth2 import id_token
from google.auth.transport import requests
from streamlit_url_fragment import get_fragment
from urllib.parse import urlparse, parse_qs
import random
import string

# API URL for creating a user
API_URL = "http://localhost:8000/users/"

# Configure Google OAuth 2.0
CLIENT_ID = '1012644879713-sj9mtjginh6oqmcm3a2ju3vv5fah94cl.apps.googleusercontent.com'
CLIENT_SECRET = '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'


# Function to call FastAPI to create a user
def create_user(email: str):
    try:
        response = requests.post(
            API_URL,
            json={"email": email}  # Adjust this to include other fields if needed
        )
        if response.status_code == 201:
            st.success("User created successfully!")
        elif response.status_code == 409:  # Conflict (duplicate entry)
            st.info("User already exists.")
        else:
            st.error("Error creating user: " + response.text)
    except Exception as e:
        st.error(f"Failed to create user: {e}")


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
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        print (idinfo)
        return idinfo
    except ValueError:
        return None

# Create a simple Streamlit app with authentication
st.title("Login using Gmail")

# Check if nonce is already set in session state
if 'nonce' not in st.session_state:
    st.session_state.nonce = generate_nonce()

# Create a login button
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
            st.success(f"Welcome, {user_info['name']}!")
            # Logic to check if the user exists in your database
            email = user_info['email']


        else:
            st.error("Invalid token, please try again.")


        
