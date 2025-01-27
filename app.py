import os
import json
from google.oauth2.service_account import Credentials
import gspread
import pandas as pd
import streamlit as st

# Define the required scopes for Google Sheets API
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


# Function to load credentials from the environment variable
def load_credentials():
    # Read the JSON content from the GOOGLE_APPLICATION_CREDENTIALS environment variable
    credentials_json = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials_json:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS environment variable not set")
    # Parse the JSON content into a dictionary
    credentials_dict = json.loads(credentials_json)
    # Create Credentials object from the dictionary
    return Credentials.from_authorized_user_info(credentials_dict, SCOPES)


# Function to fetch data from Google Sheets using the sheet ID
def fetch_data_from_sheet_by_id(sheet_id, worksheet_index=0):
    # Authenticate using the credentials
    credentials = load_credentials()
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
st.write("This app dynamically fetches data from a Google Sheet using its unique ID!")

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
