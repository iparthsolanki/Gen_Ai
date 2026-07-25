from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
import streamlit as st

# Load API Key
load_dotenv()

# Gemini Model
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0
)

# Prompt
prompt = ChatPromptTemplate.from_template("""
You are an expert teacher.

Topic: {topic}

Difficulty Level: {difficulty}

Generate the following study material:

##  Explanation
Explain the topic according to the selected difficulty.

##  Simple Example
Give one simple example.

##  Real-Life Example
Give one real-life example.

##  5 MCQs
Generate exactly 5 MCQs with:
- Question
- A, B, C, D options
- Correct Answer

##  5 Interview Questions
Generate 5 interview questions.

##  Summary
Summarize the topic in bullet points.

Return everything in proper Markdown.
""")

# Chain
chain = prompt | llm

# ---------------- Streamlit UI ----------------

st.set_page_config(page_title="Smart Study Buddy", page_icon="")

st.title(" Smart Study Buddy")

st.write("Generate complete study material using Google Gemini.")

topic = st.text_input(
    "Enter Topic",
    placeholder="Example: Machine Learning"
)

difficulty = st.selectbox(
    "Select Difficulty",
    ["Easy", "Medium", "Hard"]
)

generate = st.button("Generate Study Material")

# ---------------- Generate ----------------

if generate:

    if not topic.strip():
        st.warning(" Please enter a topic.")

    else:

        with st.spinner("Generating Study Material..."):

            response = chain.invoke(
                {
                    "topic": topic,
                    "difficulty": difficulty
                }
            )

        st.success(" Study Material Generated Successfully!")

        st.markdown("---")

        st.markdown(response.content)