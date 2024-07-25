import json
from pinecone import Pinecone
import openai
from sentence_transformers import SentenceTransformer
import numpy as np
import re
from dotenv import load_dotenv
import os

load_dotenv()

pinecone_api_key = os.getenv("pinecone_api_key_1")
pinecone_host_url = os.getenv("pinecone_host")
########################## Other Pinecone API ########################
# Initialize Pinecone
pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index(host = pinecone_host_url)

# Initialize the sentence transformer model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Initialize OpenAI
openai.api_key = os.getenv("openai_api_key")



def sanitize_namespace(name):
    """Sanitize a namespace name to meet specific requirements."""
    sanitized = ''.join(c if c.isalnum() else '_' for c in name).strip('_')
    sanitized = '_'.join(filter(None, sanitized.split('_')))
    sanitized = sanitized.replace("_","")
    return sanitized

## Vector Embeddings ##
def get_vector_embedding(question_text):
    return model.encode([question_text])[0]

## Retrieve Similar Questions ##
def retrieve_similar_Los(question_text, field_identifier):
    index = pc.Index(host = pinecone_host_url)
    
    vector = get_vector_embedding(question_text)
    # Convert NumPy array to list if necessary
    if isinstance(vector, np.ndarray):
        vector = vector.tolist()
    
    # Correctly use the namespace parameter in the query
    query_result = index.query(vector=vector, top_k=2, include_metadata=True, namespace=field_identifier)
    return query_result["matches"]

def query_gpt(question, options, similar_questions_info):

    prompt = f"Question: {question}\n\n"
    prompt += "Based on the following information:\n"
    for info in similar_questions_info:
        learning_outcome_text, technical_notes = info['learning_outcome_text'], info['technical_notes']
        prompt += f"\n Learning Outcome = {learning_outcome_text} \n Technical Note = {technical_notes}\n"
    prompt += "\nWhich of the following options is correct?\n" + ', '.join(options) + "\n Give the correct answer  only ,without including any option prefixes or justification just the text part of the option"
    
    #print('*************************')
    #print(prompt)
    #print('*******************************')
    
    
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",
        prompt=prompt,
        max_tokens=900,
        temperature=0.7
        #stop=None,
        #n=1
    )
    
    return response.choices[0].text.strip()

def process_questions():

    # Load Set B questions from the JSON file
    with open('../backend/JSON/parsed_questions_set_B.json', 'r') as file:
        questions_set_b = json.load(file)

    # Load Set A questions from the JSON file
    with open('../backend/JSON/parsed_questions.json', 'r') as file:
        questions_set_a = json.load(file)

    combined_questions = questions_set_a + questions_set_b

    for question in combined_questions:
            question['file_identifier'] = sanitize_namespace(question['file_identifier'])

    correct_answers_count = 0

    # Assuming questions_set_b is a list of dictionaries with field_identifier included
    correct_answers_count_by_identifier = {identifier: 0 for identifier in ['EquityValuationConceptsandBasicTools', 'IntroductiontoIndustryandCompanyAnalysis', 'MarketEfficiency']}


    for question in combined_questions:
        field_identifier = question["file_identifier"]  # Ensure this matches your JSON structure
        #similar_questions = retrieve_similar_questions(question["question_text"], field_identifier)
        similar_questions = retrieve_similar_Los(question.get('question_text', "Unknown"), field_identifier)
        similar_questions_info = [{
            "learning_outcome_text": match["metadata"].get("learning_outcome_text", "N/A"),  # 'N/A' as a fallback if 'question_text' does not exist
            "technical_notes": match["metadata"]["technical_notes"]
        } for match in similar_questions]
        
        
        #options = question['options']

        try:
            options = question.get('options','UnKnown')
        except KeyError:
            print("KeyError encountered. 'options' key is missing in the question.")
            print("Question content:", question)

        #if options != 'UnKnown':
            #formatted_options = [ re.split(r'\. |\) ', opt, maxsplit=1)[1] for opt in options]

        try:
            correct_answer = re.split(r'\. |\) |(?<=^[A-Z]) ', question['correct_answer'], maxsplit=1)[-1]
        except:
            print(question)

        
        gpt_answer = query_gpt(question.get('question_text', "Unknown"), options, similar_questions_info)


        if correct_answer.strip().lower() in re.sub(r'^[A-Z][). ]\s*', '', gpt_answer.strip(), flags=re.IGNORECASE).lower() :
            correct_answers_count_by_identifier[field_identifier] += 1
        
    output=[]  
    # Print results by field identifier
    for identifier, count in correct_answers_count_by_identifier.items():
        output.append(f"Correctly answered {count} out of {sum(1 for q in combined_questions if q['file_identifier'] == identifier)} questions for {identifier}.")
    
    return output

if __name__ == "__main__":
    result = process_questions()
    print(result)