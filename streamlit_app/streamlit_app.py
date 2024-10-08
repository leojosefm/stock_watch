import streamlit as st
import streamlit_authenticator as stauth
from google.oauth2 import id_token
from google.auth.transport import requests

# Configure Google OAuth 2.0
CLIENT_ID = '1012644879713-sj9mtjginh6oqmcm3a2ju3vv5fah94cl.apps.googleusercontent.com'
CLIENT_SECRET = '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'

# Create a function to verify the token received from Google
def verify_token(token):
    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        return idinfo
    except ValueError:
        return None

# Create a simple Streamlit app with authentication
st.title("Login using Gmail")

# Create a login button

st.markdown(f'<a href="https://accounts.google.com/o/oauth2/v2/auth?client_id={CLIENT_ID}&redirect_uri=http://localhost:8501/&response_type=token&scope=email profile" target="_self">Sign in with Gmail</a>', unsafe_allow_html=True)

# Redirect to Google sign-in
# stauth.Authenticate(
#     cookie_name="cookie_name",
#     key="some_random_key",
#     password="password",
#     username="username",
#     google_client_id=CLIENT_ID,
#     google_client_secret=CLIENT_SECRET,
#     callback_url="http://localhost:8501/"
# )

# Check if the token is in the URL
# Check if the token is in the URL
if 'token' in st.query_params:
    token = st.query_params['token'][0]
    user_info = verify_token(token)

    if user_info:
        st.success(f"Welcome, {user_info['name']}!")
        # Logic to check if the user exists in your database
    else:
        st.error("Invalid token, please try again.")