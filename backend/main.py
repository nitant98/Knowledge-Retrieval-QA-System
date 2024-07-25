from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
# Make sure to import your actual utility modules correctly
from utils.report_of_questions import main_workflow
# from utils.question_generation import generate_questions_set, load_filtered_data, save_questions_to_file, ques
from utils.question_generation import run_question_generation
# Assuming you have a module for Pinecone storage, make sure it's imported correctly
from utils.store_in_pinecone import final
from utils.summary_generation import main
from utils.snowflake_connector import fetch_data_from_snowflake
from typing import List

app = FastAPI()

class QuestionSet(BaseModel):
    questions: list

class GenerateQuestionsInput(BaseModel):
    file_name: str  # Ensure this path or key is accessible by your API server
    topic: str
    num_questions: int

class StoreInPineconeRequest(BaseModel):
    file_paths: List[str]

# # Endpoint for generating questions
# @app.post("/generate_questions")
# async def generate_questions(input: GenerateQuestionsInput):
#     df = load_filtered_data(input.file_name)
#     if df.empty:
#         raise HTTPException(status_code=404, detail="Data file is empty or not found.")
    
#     existing_questions = set()  # Consider how to persist or manage this state
#     questions = generate_questions_set(df, input.topic, input.num_questions, existing_questions)
    
#     return {"questions": questions}

# # Endpoint for saving questions
# @app.post("/save_questions")
# async def save_questions(topic: str, set_name: str, questions: list):
#     filename = save_questions_to_file(questions, topic, set_name)
#     if not filename:
#         raise HTTPException(status_code=500, detail="Failed to save questions.")
    
#     return {"message": f"Questions saved successfully in {filename}."}

@app.get("/summary_gen")
async def summary_gen():
    main()
    return {"message": "summary_generation.py has been executed."}

@app.get("/gen_ques")
async def gen_ques():
    run_question_generation()
    return {"message": "question_generation.py has been executed."}

@app.get("/run_store_in_pinecone")
async def run_store_in_pinecone():
    final()
    return {"message": "store_in_pinecone.py has been executed."}
    
@app.get("/topics")
async def topics():
    data = fetch_data_from_snowflake()
    return data

# Endpoint for processing questions through Pinecone and generating a report
@app.post("/process_questions")
async def process_questions_endpoint(question_set: QuestionSet):
    results, errors = main_workflow(question_set.questions)
    if errors:
        raise HTTPException(status_code=400, detail=errors)
    return {"results": results}
