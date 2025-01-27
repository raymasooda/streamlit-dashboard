import os
import json
import gspread
import pandas as pd
import streamlit as st
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Define the required scopes for Google Sheets API
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Path to your OAuth credentials.json file
CREDENTIALS_FILE = "client_secret_481874012972-k9bl8dojpo95mmpgr1v160njgc6jq6t2.apps.googleusercontent.com.json"


# Function to authenticate interactively via OAuth
def authenticate_user():
    # Check if token.json exists (to reuse previous authentication)
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        if creds and creds.valid:
            return creds
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            return creds

    # Perform interactive login via OAuth flow
    flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, SCOPES)
    creds = flow.run_local_server(port=0)

    # Save the credentials for future use
    with open("token.json", "w") as token_file:
        token_file.write(creds.to_json())

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
