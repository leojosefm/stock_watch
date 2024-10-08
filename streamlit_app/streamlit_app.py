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
    st.title("Login using Gmail")
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
    st.title("Welcome to Your Watchlist")
    # Display user info
    st.write(f"Hello, **{st.session_state['user_email']}**!")


    st.markdown("---")

    # You can add more content here (e.g., user-specific data, features, etc.)
    st.write("Here’s your personalized content.")

    # Logout button
    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.rerun()

def main():
    # Create a simple Streamlit app with authentication
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
        
