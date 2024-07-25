import json
import numpy as np
import re
import openai
from pinecone import Pinecone
from sentence_transformers import SentenceTransformer
import os
from dotenv import load_dotenv

load_dotenv()

pinecone_api_key = os.getenv("pinecone_api_key")
# Initialize Pinecone, models, etc., outside of the endpoint
# Your initialization and function definitions here...
pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index(host="https://combined-index-4wzfa7a.svc.gcp-starter.pinecone.io")

# Initialize the sentence transformer model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize OpenAI
openai.api_key = os.getenv("openai_api_key")

## Vector Embeddings ##
def get_vector_embedding(question_text):
    return model.encode([question_text])[0]

## Retrieve Similar Questions ##
def retrieve_similar_questions(question_text, field_identifier):
    vector = get_vector_embedding(question_text)
    # Convert NumPy array to list if necessary
    if isinstance(vector, np.ndarray):
        vector = vector.tolist()
    
    # Correctly use the namespace parameter in the query
    query_result = index.query(vector=vector, top_k=3, include_metadata=True, namespace=field_identifier)
    return query_result["matches"]

## Query GPT ##
def query_gpt(question, options, similar_questions_info):
    prompt = f"Question: {question}\n\n"
    prompt += "Based on the following information:\n"
    for info in similar_questions_info:
        question, answer, justification = info['question_text'], info['correct_answer'], info['justification']
        prompt += f"\n Question = {question} \n Answer = {answer}: \n Justification = {justification}\n"
    prompt += "\nWhich of the following options is correct?\n" + ', '.join(options) + "\n Give the correct answer only, without including any option prefixes or justification just the text part of the option"
    
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=300,
        temperature=0.7
    )
    
    return response.choices[0].text.strip()

##### Check Answers #####

def sanitize_namespace(name):
    """Sanitize a namespace name to meet specific requirements."""
    sanitized = ''.join(c if c.isalnum() else '_' for c in name).strip('_')
    sanitized = '_'.join(filter(None, sanitized.split('_')))
    return sanitized

# Main workflow function encapsulating your logic
def main_workflow(questions_set_b):
    correct_answers_count_by_identifier = {
        'Equity_Valuation_Concepts_and_Basic_Tools': 0,
        'Introduction_to_Industry_and_Company_Analysis': 0,
        'Market_Efficiency': 0
    }

    errors = []  # Initialize an empty list to collect errors
    for question in questions_set_b:
        # Check if 'question' is a dictionary
        if not isinstance(question, dict):
            errors.append(f"Expected a dictionary for question, but got: {type(question)}")
            continue  # Skip this iteration if it's not a dictionary

        # Proceed with the assumption that 'question' is a dictionary
        try:
            question['file_identifier'] = sanitize_namespace(question['file_identifier'])
            field_identifier = question["file_identifier"]
            similar_questions = retrieve_similar_questions(question.get('question_text', "Unknown"), field_identifier)
            similar_questions_info = [{
                "question_text": match["metadata"].get("question_text", "N/A"),  # 'N/A' as a fallback if 'question_text' does not exist
                "correct_answer": match["metadata"]["correct_answer"],
                "justification": match["metadata"]["justification"]
            } for match in similar_questions]

            options = question.get('options', 'Unknown')
            if not isinstance(options, list):
                errors.append(f"Options for question {question['file_identifier']} are not in list format.")
                continue

            # Ensure 'correct_answer' is a string to prevent TypeErrors when calling .strip() and .lower()
            correct_answer = question.get('correct_answer', '')
            if not isinstance(correct_answer, str):
                errors.append(f"Correct answer for question {question['file_identifier']} is not a string.")
                continue

            correct_answer = re.split(r'\. |\) |(?<=^[A-Z]) ', correct_answer, maxsplit=1)[-1].strip().lower()
            gpt_answer = query_gpt(question.get('question_text', "Unknown"), options, similar_questions_info).strip().lower()

            # Use 'in' to check for the correct answer within the GPT answer after stripping and lowercasing both
            if correct_answer in re.sub(r'^[A-Z][). ]\s*', '', gpt_answer, flags=re.IGNORECASE):
                correct_answers_count_by_identifier[field_identifier] += 1
        except Exception as e:
            errors.append(f"An error occurred while processing the question: {e}")

    results = []
    for identifier, count in correct_answers_count_by_identifier.items():
        results.append(f"Correctly answered {count} out of {sum(1 for q in questions_set_b if isinstance(q, dict) and q.get('file_identifier', '') == identifier)} questions for {identifier}.")

    return results, errors

