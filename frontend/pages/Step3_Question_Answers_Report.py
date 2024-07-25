import streamlit as st
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

FASTAPI_SERVER = os.getenv("fastapi_url") 

st.title("Question Answering System")

if st.button('Run QA Workflow'):
    # Load your questions
    with open('../backend/JSON/parsed_questions_set_B.json', 'r') as file:
        questions_set_b = json.load(file)
    
    # Call the FastAPI endpoint
    response = requests.post(f"{FASTAPI_SERVER}/process_questions", json={"questions": questions_set_b})
    
    # Check the status code before attempting to parse the response
    if response.status_code == 200:
        try:
            # Attempt to decode the JSON response
            results = response.json()["results"]
            for result in results:
                st.write(result)
        except json.JSONDecodeError:
            st.error(f"Invalid JSON response: {response.text}")
    else:
        # For non-200 responses, output the status code and response text
        st.error(f"Failed to get a valid response: {response.status_code}, {response.text}")

        # If possible, decode the error details
        try:
            errors = response.json().get("detail", [])
            for error in errors:
                st.error(error)
        except json.JSONDecodeError:
            st.error("An error occurred, but the response was not in JSON format.")
