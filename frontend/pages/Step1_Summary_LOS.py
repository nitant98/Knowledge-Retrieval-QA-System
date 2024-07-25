import streamlit as st
import csv
import re
import pandas as pd
from pinecone import Pinecone
import os
from dotenv import load_dotenv
import openai
import requests
from utils import pinecone_upload

load_dotenv()
# client = OpenAI(api_key=os.getenv("openai_api_key"))
openai.api_key = os.getenv("openai_api_key")
# FastAPI service URL
FASTAPI_SERVICE_URL = os.getenv("fastapi_url")  


def generate_note(topic, summary, learning_outcomes):
    
    technical_notes = []
    learning_outcomes = learning_outcomes.strip().replace("The member should be able to: ", "").replace("The candidate should be able to: ","")
    outcome_bullets = learning_outcomes.split(';')
    
    for bullet in outcome_bullets:
        prompt = f"As a financial analyst with an MBA seeking to deepen your understanding of the {topic}, generate a concise technical note summarizing key concepts and principles from {bullet} in the CFA curriculum. Craft an intro (3 sentences), material/method (3 sentences), results/discussion (3 sentences), and conclusion (2 sentences), adhering strictly to the specified sentence count per heading. Your goal is to effectively convey {bullet}'s essence to financial analysts. Adjust section lengths for a complete conclusion without truncation."
        if bullet.strip():
            # Assuming 'prompt' and 'client' are defined somewhere in your code
            response = openai.Completion.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=350
            )
            generated_text = response.choices[0].text.strip()  # Accessing the generated text
        #generated_text = f"dummy tech note:  {bullet}"
        technical_notes.append((topic, bullet, generated_text))  # Store the bullet and its corresponding generated text
            
    return technical_notes


def display_table_data():
    response = requests.get(f"{FASTAPI_SERVICE_URL}/topics")

    if response.status_code == 200:
        try:
            data = response.json()
            df = pd.DataFrame(data['rows'], columns=data['columns'])
            return df  
        except ValueError: 
            return "Failed to decode the response as JSON."
    elif response.status_code == 500:
        return "Server error occurred."
    else:
        return f"Failed to fetch table data. Status code: {response.status_code}"

def main():
    print("Test")
    data = display_table_data()
    if isinstance(data, pd.DataFrame):
        st.title("Select Topics")
        desired_topics = ["Market Efficiency", "Equity Valuation: Concepts and Basic Tools", "Introduction to Industry and Company Analysis"]
        selected_topic = st.selectbox("Select a topic:", [""] + desired_topics)
        
        if len(selected_topic) < 1:
            st.warning("Please select at least 1 topic.")
        else:
            # Filter data based on selected topic and display
            filtered_data = data[data['TOPICNAME'] == selected_topic]
           
            st.dataframe(filtered_data)

             # # Create DataFrame from selected rows
            df = pd.DataFrame(filtered_data, columns=["TOPICNAME", "INTRODUCTION", "LEARNINGOUTCOME", "SUMMARY"])
           
            # Generate summaries for Learning Outcome Statements
            st.write("Learning Outcome Summaries:")
            
            for learningOutcome, topic_name, summary in zip(df["LEARNINGOUTCOME"], df["TOPICNAME"], df["SUMMARY"]):
                tech_notes = generate_note(topic_name, summary, learningOutcome)
                #tech_notes = "dummy"
                tech_df = pd.DataFrame(tech_notes, columns=["Topic" ,"LOS", "Technical Note"])
        
            st.write(tech_df)
              
            # save in csv
            csv_directory = 'data/csv_files/'
            if not os.path.exists(csv_directory):
                os.makedirs(csv_directory)
            tech_df.to_csv(os.path.join(csv_directory, f"{topic_name}.csv"), index=False)
            
            #Define the file path for the Markdown file
            directory = 'data/readme_files/'
            if not os.path.exists(directory):
                os.makedirs(directory)
            
            if st.button('Save in local'):

                # Define the file path for each Markdown file
                for topic_name in df["TOPICNAME"].unique():
                    md_file_path = os.path.join(directory, f'readme_{topic_name}_1.md')

                # Open the Markdown file in write mode
                with open(md_file_path, 'w') as md_file:
                    # Iterate through each row in the DataFrame
                    for index, row in tech_df.iterrows():
                        # Extract LOS (Learning Outcome) and Technical Note
                        los = row['LOS']
                        tech_note = row['Technical Note']
                        
                        # Write the Markdown formatted text to the file
                        md_file.write(f"### Learning Outcome: {los}\n\n")
                        md_file.write(f"{tech_note}\n\n")
                st.success(f"Generated notes have been saved to 'readme_{topic_name}_1.md'")
                st.write("Readme file content:")
                # Display the content of the Markdown file
                st.write("Markdown file content:")
                with open(md_file_path, 'r') as md_file:
                    md_content = md_file.read()
                    st.markdown(md_content)
                try:
                    pinecone_upload.main()
                    st.write("Data saved in Pinecone")
                except Exception as e:
                    st.error(f"Error uploading data to Pinecone: {str(e)}")


   
    
if __name__ == "__main__":
    main()