# streamlit_frontend.py
'''
import streamlit as st
import subprocess

# Title for your Streamlit app
st.title("Question Proccesing with LOS")

# When the button is clicked, execute the backend script and capture its output
if st.button("Generate Report"):
    # Calling the backend script from Streamlit
    result = subprocess.run(['python', 'los_answers.py'], capture_output=True, text=True)

    # Display the output of the backend script in the Streamlit app
    if result.stdout:
        st.success("Processing complete!")
        st.text(result.stdout)
    if result.stderr:
        st.error("An error occurred during processing.")
        st.text(result.stderr)
        '''

# streamlit_frontend.py


import streamlit as st
import subprocess
import matplotlib.pyplot as plt
import ast  
# Title for your Streamlit app
st.title("Question Processing LOS")

# Function to parse the output string and return data suitable for plotting
def parse_backend_output(output):
    output_list = ast.literal_eval(output)
    results = []
    for line in output_list:
        # Extract the relevant data using string methods
        parts = line.split(' ')
        correct_answers = int(parts[2])
        total_questions = int(parts[5])
        topic = ' '.join(parts[7:])
        results.append((topic, correct_answers, total_questions))
    return results

# Function to plot a pie chart for a single topic
def plot_pie_chart(topic, correct_answers, total_questions):
    incorrect_answers = total_questions - correct_answers
    labels = 'Correct Answers', 'Incorrect Answers'
    sizes = [correct_answers, incorrect_answers]
    colors = ['#ff9999','#66b3ff']
    fig1, ax1 = plt.subplots()
    ax1.pie(sizes, colors=colors, labels=labels, autopct='%1.1f%%', startangle=90)
    # Draw circle to make it look like a donut chart
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    # Equal aspect ratio ensures that pie is drawn as a circle.
    ax1.axis('equal')  
    plt.tight_layout()
    plt.title(topic)
    return fig


if st.button("Generate Report"):
    
    result = subprocess.run(['python', 'utils/los_answers.py'], capture_output=True, text=True)
    # Display the output of the backend script in the Streamlit app
    if result.stdout:
        st.success("Processing complete!")
        
        parsed_results = parse_backend_output(result.stdout)
        
        # Generate and display pie charts for each topic
        for topic, correct_answers, total_questions in parsed_results:
            fig = plot_pie_chart(topic, correct_answers, total_questions)
            st.pyplot(fig)
    else:
        st.error("An error occurred during processing.")
        if result.stderr:
            st.text(result.stderr)
