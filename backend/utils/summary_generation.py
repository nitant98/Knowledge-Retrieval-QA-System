import csv
import os
import pandas as pd
# from dotenv import load_dotenv
import openai
import json
from dotenv import load_dotenv

load_dotenv()

# Load environment variables
# load_dotenv()
openai.api_key = os.getenv("openai_api_key")

def generate_note(topic, summary, learning_outcomes):
    technical_notes = []
    learning_outcomes = learning_outcomes.strip().replace("The member should be able to: ", "").replace("The candidate should be able to: ", "")
    outcome_bullets = learning_outcomes.split(';')

    for bullet in outcome_bullets:
        prompt = f"As a financial analyst with an MBA seeking to deepen your understanding of {topic}, generate a concise technical note summarizing key concepts and principles from {bullet} in the CFA curriculum. Craft an intro (3 sentences), material/method (3 sentences), results/discussion (3 sentences), and conclusion (2 sentences), adhering strictly to the specified sentence count per heading. Your goal is to effectively convey {bullet}'s essence to financial analysts. Adjust section lengths for a complete conclusion without truncation."
        if bullet.strip():
            response = openai.completions.create(
                model="gpt-3.5-turbo-instruct",
                prompt=prompt,
                max_tokens=350
            )
            generated_text = response.choices[0].text.strip()
            technical_notes.append((topic, bullet, generated_text))

    return technical_notes

def main():
    data_file = 'data/topics.csv'  # Update to your data file path
    data = pd.read_csv(data_file)
    print("Select Topics")
    desired_topics = ["Market Efficiency", "Equity Valuation: Concepts and Basic Tools", "Introduction to Industry and Company Analysis"]
    print("\n".join(f"{i}. {topic}" for i, topic in enumerate(desired_topics, 1)))
    topic_index = int(input("Enter the number for your topic choice: ")) - 1
    selected_topic = desired_topics[topic_index]

    filtered_data = data[data['TOPICNAME'] == selected_topic]
    print("\nFiltered Data:")
    print(filtered_data.to_string(index=False))

    # Generate summaries for Learning Outcome Statements
    print("\nLearning Outcome Summaries:")
    tech_notes = []
    for _, row in filtered_data.iterrows():
        notes = generate_note(row['TOPICNAME'], row['SUMMARY'], row['LEARNINGOUTCOME'])
        tech_notes.extend(notes)

    tech_df = pd.DataFrame(tech_notes, columns=["Topic", "LOS", "Technical Note"])
    print(tech_df.to_string())

    # Save in CSV
    csv_directory = 'data/csv_files/'
    if not os.path.exists(csv_directory):
        os.makedirs(csv_directory)
    csv_file_path = os.path.join(csv_directory, f"{selected_topic}.csv")
    tech_df.to_csv(csv_file_path, index=False)
    print(f"\nGenerated notes have been saved to '{csv_file_path}'")

    # Save in Markdown
    markdown_directory = 'data/readme_files/'
    if not os.path.exists(markdown_directory):
        os.makedirs(markdown_directory)
    markdown_file_path = os.path.join(markdown_directory, f'readme_{selected_topic}_1.md')
    with open(markdown_file_path, 'w') as md_file:
        for _, note in tech_df.iterrows():
            md_file.write(f"### Learning Outcome: {note['LOS']}\n\n")
            md_file.write(f"{note['Technical Note']}\n\n")
    print(f"Markdown file 'readme_{selected_topic}_1.md' has been generated.")

if __name__ == "__main__":
    main()
