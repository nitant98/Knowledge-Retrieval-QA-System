import pandas as pd
import openai
import random
import os
from dotenv import load_dotenv

load_dotenv()

# Assuming you have your OpenAI API key set as an environment variable for security reasons
# Otherwise, you can set it directly as you have in your code.
openai.api_key = os.getenv("openai_api_key")

def load_filtered_data(file_name):
    df = pd.read_csv(file_name)
    return df

def generate_question(context, existing_questions):
    prompt = f"Generate a unique multiple-choice question with 4 options and remember it considering all the topics from the context, with correct option and it's text value and its 1 line justification with format Question:, Options:, Correct Answer:, Justification:  considering the context: {context}. Ensure the question is distinct from the previously generated ones."
    
    while True:
        response = openai.Completion.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=300,
            temperature=0.7
        )
        new_question = response.choices[0].text.strip()
        if new_question not in existing_questions:
            return new_question

def generate_questions_set(df, topic, num_questions, existing_questions):
    questions = []
    while len(questions) < num_questions:
        df_slice = df[df['topicName'] == topic].sample(n=1)
        context = f"{df_slice['summary'].iloc[0]} {df_slice['learningOutcome'].iloc[0]}"
        question = generate_question(context, existing_questions)
        if question not in existing_questions:
            existing_questions.add(question)
            questions.append(question)
    return questions

def save_questions_to_file(questions, topic, set_name):
    filename = f'{topic}_{set_name}_Questions.txt'.replace(" ", "_")
    filename = filename.replace(":", "")
    filename = os.path.join("Questions", filename)
    with open(filename, 'w') as file:
        file.write(f"Topic: {topic}\n\n")
        for idx, question in enumerate(questions, start=1):
            file.write(f"{idx}. {question}\n\n")

def run_question_generation():
    file_path = 'new_extracted_updated.csv'
    topics = ["Market Efficiency", "Introduction to Industry and Company Analysis", "Equity Valuation: Concepts and Basic Tools"]
    df = load_filtered_data(file_path)

    if not df.empty:
        for set_name in ["Set A", "Set B"]:
            for topic in topics:
                existing_questions = set()  # Assuming existing questions are managed elsewhere
                questions = generate_questions_set(df, topic, 50, existing_questions)
                save_questions_to_file(questions, topic, set_name)
                print(f"{set_name} questions for {topic} have been generated and saved successfully.")
    else:
        print("No data found for selected topics or file not found.")

if __name__ == "__main__":
    run_question_generation()
