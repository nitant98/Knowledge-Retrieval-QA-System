import json
import re
from pinecone import Pinecone, PodSpec
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import os

load_dotenv()

def final():
    def parse_file(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='cp1252') as file:
                content = file.read()

        topic_name_match = re.search(r'^Topic:\s*(.+)$', content, re.MULTILINE)
        if topic_name_match:
            topic_name = topic_name_match.group(1).strip()
        else:
            topic_name = "Unknown Topic"

        question_blocks = re.split(r'\n\d+\.\sQuestion:\s', content)[1:]

        questions_list = []
        for block in question_blocks:
            question = {}
            question_text_match = re.search(r'^(.*?)Options:', block, re.DOTALL)
            if question_text_match:
                question['question_text'] = question_text_match.group(1).strip()

            options_match = re.search(r'Options:\s(.*?)Correct Answer:', block, re.DOTALL)
            if options_match:
                options_text = options_match.group(1).strip()
                question['options'] = [opt.strip() for opt in re.split(r'\n', options_text)]

            correct_answer_match = re.search(r'Correct Answer:\s(.*?)\n', block)
            if correct_answer_match:
                question['correct_answer'] = correct_answer_match.group(1).strip()

            justification_match = re.search(r'Justification:\s(.*)', block, re.DOTALL)
            if justification_match:
                question['justification'] = justification_match.group(1).strip()

            questions_list.append(question)

        return topic_name, questions_list

    # Set A files
    file_paths_set_a = ["Questions/Market_Efficiency_Set_A_Questions.txt","Questions/Introduction_to_Industry_and_Company_Analysis_Set_A_Questions.txt","Questions/Equity_Valuation_Concepts_and_Basic_Tools_Set_A_Questions.txt"]

    # Set B files
    file_paths_set_b = ["Questions/Market_Efficiency_Set_B_Questions.txt","Questions/Introduction_to_Industry_and_Company_Analysis_Set_B_Questions.txt","Questions/Equity_Valuation_Concepts_and_Basic_Tools_Set_B_Questions.txt"]

    def process_files(file_paths, output_filename):
        all_questions = []
        for file_path in file_paths:
            try:
                topic_name, questions = parse_file(file_path)
                for question in questions:
                    question['file_identifier'] = topic_name
                    question['question_id'] = questions.index(question) + 1
                all_questions.extend(questions)
                print(f"Processed {len(questions)} questions from {topic_name}")
            except FileNotFoundError:
                print(f"Error: The file was not found: {file_path}")
            except Exception as e:
                print(f"An unexpected error occurred while processing {file_path}: {str(e)}")

        with open(f'JSON/{output_filename}.json', 'w', encoding='utf-8') as json_file:
            json.dump(all_questions, json_file, indent=4)

        print(f"Total questions parsed and saved in {output_filename}: {len(all_questions)}")

    # Process and save for Set A and Set B
    process_files(file_paths_set_a, 'parsed_questions')
    process_files(file_paths_set_b, 'parsed_questions_set_B')



    ################ Embeddings ###################

    def load_questions_data(file_path):
        """Load questions data from a JSON file."""
        with open(file_path, 'r') as file:
            questions_data = json.load(file)
        return questions_data

    def generate_embeddings(model, questions_data):
        """Generate embeddings for each question text in the dataset."""
        for question in questions_data:
            text_to_encode = question.get('question_text', "Unknown")
            question['embedding'] = model.encode(text_to_encode, convert_to_tensor=True).cpu().numpy().tolist()
        return questions_data

    def sanitize_namespace(name):
        """Sanitize a namespace name to meet specific requirements."""
        sanitized = ''.join(c if c.isalnum() else '_' for c in name).strip('_')
        sanitized = '_'.join(filter(None, sanitized.split('_')))
        return sanitized

    def insert_data_into_pinecone(index, questions_data):
        """Insert questions data into Pinecone."""
        for question in questions_data:
            vector = question.pop('embedding')
            metadata = question
            namespace = sanitize_namespace(question['file_identifier'])
            index.upsert(vectors=[(str(question['question_id']), vector, metadata)], namespace=namespace)
        print("Data insertion complete.")


    # Initialize Pinecone without changing the method you're using
    def initialize_and_insert(api_key, host_name, questions_data):
        pc = Pinecone(api_key=api_key)
        index = pc.Index(host = host_name)
        # Insert data
        insert_data_into_pinecone(index, questions_data)

    pinecone_api_key = os.getenv("pinecone_api_key")
    # Configuration
    model_name = 'all-MiniLM-L6-v2'
    api_key = pinecone_api_key
    pinecone_environment = "gcp-starter"
    host_name = "https://combined-index-4wzfa7a.svc.gcp-starter.pinecone.io"

    # Load questions data
    questions_data = load_questions_data('JSON/parsed_questions.json')

    # Initialize the Sentence Transformer model
    model = SentenceTransformer(model_name)

    # Generate embeddings
    questions_data = generate_embeddings(model, questions_data)

    # Initialize Pinecone and insert data
    initialize_and_insert(api_key, host_name, questions_data)

    print("Function from store_in_pinecone.py has run.")




#### Old Parse File #####

'''
def parse_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
    except UnicodeDecodeError:
        with open(file_path, 'r', encoding='cp1252') as file:
            content = file.read()

    # Extract the topic name as the first line or another pattern if it's consistent
    topic_name_match = re.search(r'^Topic:\s*(.+)$', content, re.MULTILINE)
    if topic_name_match:
        topic_name = topic_name_match.group(1).strip()
    else:
        # Fallback if no topic is found; consider adjusting or ensuring consistency
        topic_name = "Unknown Topic"

    question_blocks = re.split(r'\n\d+\.\sQuestion:\s', content)[1:]  # Skipping the first split which is empty

    questions_list = []
    for block in question_blocks:
        question = {}
        question_text_match = re.search(r'^(.*?)Options:', block, re.DOTALL)
        if question_text_match:
            question['question_text'] = question_text_match.group(1).strip()

        options_match = re.search(r'Options:\s(.*?)Correct Answer:', block, re.DOTALL)
        if options_match:
            options_text = options_match.group(1).strip()
            question['options'] = [opt.strip() for opt in re.split(r'\n', options_text)]

        correct_answer_match = re.search(r'Correct Answer:\s(.*?)\n', block)
        if correct_answer_match:
            question['correct_answer'] = correct_answer_match.group(1).strip()

        justification_match = re.search(r'Justification:\s(.*)', block, re.DOTALL)
        if justification_match:
            question['justification'] = justification_match.group(1).strip()

        questions_list.append(question)

    return topic_name, questions_list

file_paths = ["Questions/Market_Efficiency_Set_A_Questions.txt","Questions/Introduction_to_Industry_and_Company_Analysis_Set_A_Questions.txt","Questions/Equity_Valuation_Concepts_and_Basic_Tools_Set_A_Questions.txt"]

all_questions = []

for file_path in file_paths:
    try:
        topic_name, questions = parse_file(file_path)
        # Use topic name as file_identifier
        for question in questions:
            question['file_identifier'] = topic_name
            question['question_id'] = questions.index(question) + 1
        all_questions.extend(questions)
        print(f"Processed {len(questions)} questions from {topic_name}")
    except FileNotFoundError:
        print(f"Error: The file was not found: {file_path}")
    except Exception as e:
        print(f"An unexpected error occurred while processing {file_path}: {str(e)}")

# Optionally, save the structured data to a JSON file
with open('JSON/parsed_questions.json', 'w', encoding='utf-8') as json_file:
    json.dump(all_questions, json_file, indent=4)
'''