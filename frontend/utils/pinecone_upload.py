import pandas as pd
import numpy as np
import os
import csv
import json
from pinecone import Pinecone
from pinecone import PodSpec
from sentence_transformers import SentenceTransformer
import uuid
import unicodedata
from dotenv import load_dotenv

load_dotenv()

# Connect to Pinecone
pinecone_api_key = os.getenv("pinecone_api_key_1")
pinecone = Pinecone(api_key= pinecone_api_key)

# Load pre-trained model for vectorization (replace with your chosen model)
model = SentenceTransformer('all-MiniLM-L6-v2')

index_name = 'damg7245'


# Use the existing index
index = pinecone.Index(name=index_name)
print(f"Using existing index '{index_name}'")


# Now you can use the 'index' variable for your operations


def prepare_data(row):
    unique_id = str(uuid.uuid4()) 
    # Vectorize learning outcome
    learning_outcome_vector = model.encode(row['LOS'])
    # Convert the vector to a list of floats
    learning_outcome_vector = [float(val) for val in learning_outcome_vector]
    #print(learning_outcome_vector)

    # Create document with vector and technical notes as metadata
    return {
        "id": unique_id,  # Pinecone will generate the ID
        "values": learning_outcome_vector,
        "metadata": {
            "learning_outcome_text": row['LOS'],
            "technical_notes": row['Technical Note']
        }
    }

def main():
    # Read CSV files
    csv_files = ['EquityValuationConceptsandBasicTools.csv', 'Introduction to Industry and Company Analysis.csv', 'Market Efficiency.csv']

    # Directory containing CSV files
    csv_data_path = 'data/csv_files'

    data = {}

    # Loop through each CSV file
    for file in csv_files:
        with open(os.path.join(csv_data_path, file), 'r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.DictReader(csvfile)
            for row in csvreader:
                prepared_data = prepare_data(row)
                topic = row['Topic']
                # Remove non-ASCII characters from topic
                topic = ''.join(char for char in topic if unicodedata.category(char)[0] == 'L')
                if topic not in data:
                    data[topic] = [prepared_data]  # Store data as a list
                else:
                    data[topic].append(prepared_data) 

    # Save data dictionary to a JSON file
    json_data_path = 'data/csv_files'  # Directory for JSON files
    os.makedirs(json_data_path, exist_ok=True)  # Create directory if not exists

    for topic, info in data.items():
        with open(os.path.join(json_data_path, f'{topic}.json'), 'w', encoding='utf-8') as jsonfile:
            json.dump(info, jsonfile, indent=4)


    for topic, documents in data.items():
        index.upsert(documents, namespace=topic)
    print("Data uploaded successfully to Pinecone!")


if __name__ == "__main__":
    main()