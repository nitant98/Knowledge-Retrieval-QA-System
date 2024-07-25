import streamlit as st
import requests
from dotenv import load_dotenv
import os 

load_dotenv()

FASTAPI_SERVER = os.getenv("fastapi_url")    # Update to your FastAPI server address

st.title('Question Bank Management System')

# Header for generating questions
st.header("Generate Questions")
topic = st.selectbox("Select Topic", ["Market Efficiency", "Introduction to Industry and Company Analysis", "Equity Valuation: Concepts and Basic Tools"])
num_questions = st.number_input("Number of Questions to Generate", min_value=1, value=50)

# Button to generate questions
if st.button('Generate Questions'):
    # Since you're using a GET endpoint without body for generation, we call the endpoint directly
    response = requests.get(f"{FASTAPI_SERVER}/gen_ques")
    if response.status_code == 200:
        st.success("Questions generated successfully.")
        # If your endpoint returns the generated questions, uncomment the line below to display them
        # st.write(response.json()["questions"])
    else:
        st.error(f"Failed to generate questions: {response.text}")

# Button to store questions in Pinecone
st.header("Store Questions in Pinecone")
if st.button('Store in Pinecone'):
    response = requests.get(f"{FASTAPI_SERVER}/run_store_in_pinecone")
    if response.status_code == 200:
        st.success("Questions stored successfully in Pinecone.")
    else:
        st.error(f"Failed to store questions in Pinecone: {response.text}")
