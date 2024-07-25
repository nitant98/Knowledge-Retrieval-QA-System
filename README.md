
## Assignment 5

## Problem Statement:
Development of a Structured Database and Text Extraction System for Finance Professional Development Resources

## Project Goals
Utilize Pinecone and OpenAI APIs to create knowledge summaries, generate a contextual knowledge base, utilize vector databases for question answering, and employ GPT-based summaries to provide accurate answers.

## Project Tasks
  
### Step1 Generating Technical Notes from LOS:
        
    1. The script Step1_Summary_LOS.py utilizes OpenAI's GPT to generate technical notes summarizing key Learning Outcome Statements (LOS).
    2. Furthermore, the script integrates with Pinecone for efficient data storage by chunking each LOS and its corresponding technical note and uploading it to Pinecone for retrieval.

 ### Step 2: Question Bank Creation and Data Organization

    1. Question Bank Creation: Generate question banks for each assigned topic. Save these questions as separate TXT files for each topic.
    2. Parsing TXT Files to Generate JSON Schema: Develop a parser to extract questions from TXT files. Create a JSON schema for all questions within each set (Set A and Set B). Include metadata such as the topic to identify the source of the questions.
    3. Data Organization and Storage: Save parsed data in JSON format. Utilize Pinecone for data storage with topics as namespaces.


### Step 3: Using a Vector Database to Find and Answer Questions
    
    1. Utilizing RAG for Question Similarity Search: The system employs RAG (Retrieval-Augmented Generation) to search for similar questions based on information stored in Pinecone. It retrieves relevant question-answer pairs from Set A to assess the accuracy of answers from Set B.
    2. GPT-4 Question Answering Process: Question-answer pairs from Set A are passed to GPT-4 along with a question from Set B and answer choices. GPT-4 processes the input and generates responses, simulating human-like comprehension and reasoning.
    3. Evaluation of Answer Correctness: The system evaluates the correctness of answers provided by GPT-4 and compares them to the actual answers. Results are presented to the user, allowing for further analysis and refinement of the question answering process.

    
### Step 4: Use Knowledge Summaries to Answer Questions
    
    1. Utilizing RAG in Pinecone Vector Database: The system employs RAG (Retrieval-Augmented Generation) within the Pinecone vector database to search for similar embeddings and Learning Outcome Statements (LOS) containing answers to questions from both Set A and Set B.
    2. Tabulating Answer Accuracy: The accuracy of answers to the 100 questions/topics is tabulated and presented to the user.
    3. Evaluation and Discussion: The effectiveness of this approach is discussed in comparison to Task 3, highlighting its strengths and areas for improvement.
    Alternative designs for enhanced question answering are proposed, considering factors such as accuracy, efficiency, and user experience.

## Conclusion

By completing these tasks, we aim to evaluate different approaches for knowledge retrieval and question answering using MaaS APIs, contributing valuable insights for enterprise applications.

## Codelab

[codelabs](https://codelabs-preview.appspot.com/?file_id=1fgubqz6h9BDCbEH1wdWYCjpfK3Iof7RCu2W_Kd6uOAY#3)

[Demo Part1](https://www.youtube.com/watch?v=5RZNkLJtoBE)
 
[Demo Part2](https://www.youtube.com/watch?v=0n0S1EA3dPc)

## Technologies Used

[![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)](https://www.python.org/)
[![Snowflake](https://img.shields.io/badge/Snowflake-387BC3?style=for-the-badge&logo=snowflake&logoColor=light)](https://www.snowflake.com/)
[![Google Cloud Platform](https://img.shields.io/badge/Google%20Cloud%20Platform-4285F4?style=for-the-badge&logo=google-cloud&logoColor=white)](https://cloud.google.com/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://www.streamlit.io/)
[![Pinecone](https://img.shields.io/badge/Pinecone-7B0099?style=for-the-badge&logo=pinecone&logoColor=white)](https://www.pinecone.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI-000000?style=for-the-badge&logo=openai&logoColor=white)](https://openai.com/)



## Project Structure
```
├── .gitignore
├── docker-compose.yml
├── Makefile
├── README.md
├── requirements.txt
├── backend
│   ├── Dockerfile
│   ├── main.py
│   ├── new_extracted_updated.csv
│   ├── JSON
│   │   ├── parsed_questions.json
│   │   └── parsed_questions_set_B.json
│   ├── Questions
│   │   ├── Equity_Valuation_Concepts_and_Basic_Tools_Set_A_Questions.txt
│   │   ├── Equity_Valuation_Concepts_and_Basic_Tools_Set_B_Questions.txt
│   │   ├── Introduction_to_Industry_and_Company_Analysis_Set_A_Questions.txt
│   │   ├── Introduction_to_Industry_and_Company_Analysis_Set_B_Questions.txt
│   │   ├── Market_Efficiency_Set_A_Questions.txt
│   │   └── Market_Efficiency_Set_B_Questions.txt
│   └── utils
│       ├── los_pinecone.py
│       ├── new_extracted_updated.csv
│       ├── question_generation.py
│       ├── report_of_questions.py
│       ├── snowflake_connector.py
│       ├── store_in_pinecone.py
│       ├── summary_generation.py
│       └── __init__.py
└── frontend
    ├── app.py
    ├── Dockerfile
    ├── data
    │   ├── csv_files
    │   │   ├── Equity Valuation_ Concepts and Basic Tools.csv
    │   │   ├── EquityValuationConceptsandBasicTools.csv
    │   │   ├── Introduction to Industry and Company Analysis.csv
    │   │   ├── Market Efficiency.csv
    │   ├── json_files
    │   │   ├── Equity Valuation_ Concepts and Basic Tools.json
    │   │   ├── Introduction to Industry and Company Analysis.json
    │   │   ├── Market Efficiency.json
    │   └── readme_files
    │       ├── readme_Equity Valuation_ Concepts and Basic Tools.md
    │       ├── readme_Introduction to Industry and Company Analysis.md
    │       ├── readme_Market Efficiency.md
    ├── pages
    │   ├── Step1_Summary_LOS.py
    │   ├── Step2_Question_Generation_Page.py
    │   ├── Step3_Question_Answers_Report.py
    │   └── Step4_LOS_Answers.py
    └── utils
        ├── los_answers.py
        └── pinecone_upload.py
```
## Architectural Diagram
![diagram](https://github.com/BigDataIA-Spring2024-Sec1-Team4/Assignment5/blob/Anirudha/diagrams/system_architecture_for_assignment5.png)

## To run the application locally, follow these steps:

1. **Clone the Repository**: Clone the repository onto your local machine.

   ```bash
   git clone https://github.com/BigDataIA-Spring2024-Sec1-Team4/Assignment5
   ```

2. **Create a Virtual Environment**: Set up a virtual environment to isolate project dependencies.

   ```bash
   python -m venv venv
   ```

3. **Activate the Virtual Environment**: Activate the virtual environment.

   - **Windows**:

     ```bash
     venv\Scripts\activate
     ```

   - **Unix or MacOS**:

     ```bash
     source venv/bin/activate
     ```

4. **Run MakeFile to start Docker Compose**: Start the Docker containers using Docker Compose.

   ```bash
   cd Assignment5
   make build-up
   ```

5. **Access Streamlit Interface**: Open your web browser and go to `34.75.0.13:8000` to access the Streamlit interface.

6. **Step1**: On the Streamlit homepage,Users can select a topic from the available topics. generate summaery and save it in pinecone.

7. **Step2 Question_Generation_Page.**:Users can select topics from a dropdown menu and specify the number of questions to generate. Upon clicking the "Generate Questions" button, save data in pinecone
8. **Step3 Question Answers Report** :Upon clicking the "Run QA Workflow" button, the script loads questions from a JSON file and displayes results
9. **Step4 LOS Answers** :  Upon clicking the "Generate Report" button, Generates a pie chart for each topic depicting the distribution of correct and incorrect answers.
    
By following these steps, you should be able to run the application locally and interact with it using the provided Streamlit interface to upload PDF files, trigger data processing pipelines, and query Snowflake for results.



## Team Information and Contribution 

Name           | NUID          |
---------------|---------------|
Anirudh Joshi  | 002991365     |      
Nitant Jatale  | 002776669     |      
Rutuja More    | 00272782      |      
