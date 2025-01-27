import json
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import gspread
import pandas as pd

# Define the required scopes for Google Sheets API
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# Function to authenticate interactively via OAuth
def authenticate_user():
    # Load OAuth client configuration from Streamlit Secrets
    credentials_json = st.secrets["credentials_json"]

    # Check if credentials are already stored in session_state
    if "token" in st.session_state:
        creds = Credentials.from_authorized_user_info(
            json.loads(st.session_state["token"]), SCOPES
        )
        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            return creds

    # Attempt to use the local server for authentication
    try:
        flow = InstalledAppFlow.from_client_config(json.loads(credentials_json), SCOPES)
        creds = flow.run_local_server(port=0)
    except Exception:
        # If the local server fails (e.g., no browser), use manual console authentication
        st.warning("No browser available. Falling back to manual authentication.")
        flow = InstalledAppFlow.from_client_config(json.loads(credentials_json), SCOPES)
        auth_url, _ = flow.authorization_url(prompt="consent")

        # Show the authorization URL to the user
        st.write("Visit the following URL to authenticate:")
        st.code(auth_url, language="markdown")

        # Prompt the user to enter the authorization code
        auth_code = st.text_input("Enter the authorization code:")
        if not auth_code:
            st.stop()  # Stop execution until the user enters the code
        creds = flow.fetch_token(code=auth_code)

    # Store credentials in session_state for reuse in the current session
    st.session_state["token"] = creds.to_json()

    return creds


# Function to fetch data from Google Sheets using the sheet ID
def fetch_data_from_sheet_by_id(sheet_id, worksheet_index=0):
    # Authenticate the user interactively
    credentials = authenticate_user()
    client = gspread.authorize(credentials)

    # Open the Google Sheet by ID
    sheet = client.open_by_key(sheet_id)
    # Get the specified worksheet (default is the first worksheet)
    worksheet = sheet.get_worksheet(worksheet_index)

    # Fetch all data from the worksheet and convert it to a Pandas DataFrame
    data = pd.DataFrame(worksheet.get_all_records())
    return data


# Streamlit app
st.title("Google Sheets Dashboard by ID")
st.write(
    "This app dynamically fetches data from a Google Sheet using an interactive sign-in!"
)

# Input field for Google Sheet ID
sheet_id = st.text_input("Enter your Google Sheet ID:", value="")

# Fetch and display data when the user provides a sheet ID
if sheet_id:
    try:
        data = fetch_data_from_sheet_by_id(sheet_id)
        st.success(f"Data successfully fetched from the sheet with ID: {sheet_id}")

        # Display the data
        st.write("Latest Data:")
        st.dataframe(data)

        # Example visualization
        if not data.empty:
            numeric_columns = data.select_dtypes(include="number").columns
            if len(numeric_columns) > 0:
                st.write("Example Visualization (Line Chart):")
                st.line_chart(data[numeric_columns[0]])
            else:
                st.warning("No numeric columns found for visualization.")
        else:
            st.warning("The sheet is empty or has no valid data.")
    except Exception as e:
        st.error(f"An error occurred: {e}")
