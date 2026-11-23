import os
import hashlib
import tempfile

import streamlit as st
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Campus Knowledge Assistant",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

load_dotenv()

DEFAULT_PDF = "information.pdf"
MODEL_NAME = "openai/gpt-oss-20b"
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ---------------------------------------------------------------------------
# Custom CSS (professional dark theme)
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
    #MainMenu, footer {visibility: hidden;}
    .block-container {padding-top: 1.5rem; max-width: 1000px;}

    .hero {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 55%, #06b6d4 100%);
        padding: 1.6rem 1.8rem;
        border-radius: 18px;
        margin-bottom: 1.2rem;
        box-shadow: 0 10px 30px rgba(79, 70, 229, 0.35);
    }
    .hero h1 {color: #fff; margin: 0; font-size: 1.9rem; font-weight: 700;}
    .hero p {color: rgba(255,255,255,0.88); margin: 0.35rem 0 0 0; font-size: 0.98rem;}

    [data-testid="stChatMessage"] {
        background: #161b2e;
        border: 1px solid #252b45;
        border-radius: 14px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.7rem;
    }
    [data-testid="stSidebar"] {
        background: #0b0f1e;
        border-right: 1px solid #1f2540;
    }
    .src-chip {
        display: inline-block;
        background: #1e2547;
        color: #a5b4fc;
        border: 1px solid #2f3a6e;
        border-radius: 999px;
        padding: 2px 10px;
        font-size: 0.75rem;
        margin: 2px 4px 2px 0;
    }
    .stButton > button {
        border-radius: 10px;
        border: 1px solid #2f3a6e;
        width: 100%;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Prompt
# ---------------------------------------------------------------------------
PROMPT = PromptTemplate(
    input_variables=["context", "history", "question"],
    template="""
You are a Campus Knowledge Assistant.

Answer the question using only the information provided in the context.

Instructions:
1. Give clear, well-structured and simple answers (use bullet points when helpful).
2. Answer only from the provided context.
3. Do not make up information.
4. If the answer is not available, say that it was not found in the documents.
5. Do not mention unnecessary technical details.
6. Use the chat history only to understand follow-up questions.
7. Several candidate passages are given, ranked by relevance. Base your answer on
   the MOST relevant passage (Passage 1). Use the other passages only if
   Passage 1 does not contain the answer.
8. Give one single, final answer. Do not list or compare the passages.

Chat History:
{history}

Candidate passages (ranked by relevance, Passage 1 = most relevant):
{context}

Question:
{question}

Answer:
""",
)


# ---------------------------------------------------------------------------
# Cached resources
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def load_embeddings():
    return HuggingFaceEmbeddings(model_name=EMBED_MODEL)


@st.cache_resource(show_spinner=False)
def build_vector_store(file_bytes: bytes, file_hash: str):
    """Load PDF -> split -> embed -> store in Chroma (in-memory, cached per file)."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(file_bytes)
        tmp_path = tmp.name

    try:
        documents = PyPDFLoader(tmp_path).load()
    finally:
        os.remove(tmp_path)

    splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = splitter.split_documents(documents)

    store = Chroma.from_documents(
        documents=chunks,
        embedding=load_embeddings(),
        collection_name=f"docs_{file_hash[:16]}",
    )
    return store, len(documents), len(chunks)


def get_llm(api_key: str, temperature: float):
    return ChatGroq(model=MODEL_NAME, temperature=temperature, groq_api_key=api_key)


def format_history(messages, limit=6):
    recent = messages[-limit:]
    return "\n".join(
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
        for m in recent
    ) or "None"


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 🎓 Campus Assistant")
    st.caption("RAG chatbot • LangChain • ChromaDB • Groq")
    st.divider()

    st.markdown("### 🔑 API Key")
    env_key = os.getenv("GROQ_API_KEY")
    if not env_key:
        try:
            env_key = st.secrets["GROQ_API_KEY"]
        except Exception:
            env_key = None
    key_input = st.text_input(
        "Groq API Key",
        type="password",
        value="",
        placeholder="Loaded from .env" if env_key else "gsk_...",
        label_visibility="collapsed",
    )
    groq_api_key = key_input or env_key

    st.markdown("### 📄 Document")
    uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

    st.markdown("### ⚙️ Settings")
    top_k = 3  # 3 candidate answers retrieved, best one is used
    temperature = st.slider("Temperature", 0.0, 1.0, 0.0, 0.1)
    show_sources = st.toggle("Show sources", value=True)

    st.divider()
    if st.button("🗑️ Clear chat"):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>🎓 Campus Knowledge Assistant</h1>
        <p>Ask questions directly from your documents. Answers are based only on the PDF content.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Guards
# ---------------------------------------------------------------------------
if not groq_api_key:
    st.error("Groq API key not found. Add `GROQ_API_KEY` to your `.env` file or paste it in the sidebar.")
    st.stop()

if uploaded is not None:
    pdf_bytes = uploaded.getvalue()
    pdf_name = uploaded.name
elif os.path.exists(DEFAULT_PDF):
    with open(DEFAULT_PDF, "rb") as f:
        pdf_bytes = f.read()
    pdf_name = DEFAULT_PDF
else:
    st.warning("Upload a PDF from the sidebar or place `information.pdf` in the project folder.")
    st.stop()

file_hash = hashlib.md5(pdf_bytes).hexdigest()

# Reset chat if the document changes
if st.session_state.get("active_doc") != file_hash:
    st.session_state.active_doc = file_hash
    st.session_state.messages = []

with st.spinner("Processing document..."):
    vector_store, n_pages, n_chunks = build_vector_store(pdf_bytes, file_hash)

llm = get_llm(groq_api_key, temperature)

st.caption(f"📎 Active document: **{pdf_name}**")
st.write("")

# ---------------------------------------------------------------------------
# Chat history
# ---------------------------------------------------------------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar="🧑‍🎓" if msg["role"] == "user" else "🎓"):
        st.markdown(msg["content"])
        if show_sources and msg.get("sources"):
            st.markdown(
                "".join(f'<span class="src-chip">📄 Page {p}</span>' for p in msg["sources"]),
                unsafe_allow_html=True,
            )

if not st.session_state.messages:
    st.info("Try: *“What is the admission process?”*, *“What is the fee structure?”*, *“What hostel facilities are available?”*")

# ---------------------------------------------------------------------------
# Chat input
# ---------------------------------------------------------------------------
question = st.chat_input("Ask your question here...")

if question:
    question = question.strip()
    history_text = format_history(st.session_state.messages)

    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user", avatar="🧑‍🎓"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🎓"):
        try:
            with st.spinner("Searching documents..."):
                results = vector_store.similarity_search_with_score(question, k=top_k)
            # lower distance = more relevant -> best passage first
            results = sorted(results, key=lambda r: r[1])
            docs = [d for d, _ in results]
            scores = [round(100 / (1 + s), 1) for _, s in results]
            context = "\n\n".join(
                f"[Passage {i} | Page {(d.metadata.get('page', 0) or 0) + 1}]\n{d.page_content}"
                for i, d in enumerate(docs, 1)
            )
            prompt = PROMPT.format(context=context, history=history_text, question=question)

            def token_stream():
                for chunk in llm.stream(prompt):
                    if chunk.content:
                        yield chunk.content

            answer = st.write_stream(token_stream())

            # only the most relevant source is shown as the main source
            pages = [(docs[0].metadata.get("page", 0) or 0) + 1] if docs else []
            if show_sources and pages:
                st.markdown(
                    f'<span class="src-chip">🏆 Best match • Page {pages[0]} • {scores[0]}%</span>',
                    unsafe_allow_html=True,
                )
                with st.expander("🔍 Top 3 retrieved passages (ranked)"):
                    for i, (d, sc) in enumerate(zip(docs, scores), 1):
                        page_no = (d.metadata.get("page", 0) or 0) + 1
                        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
                        st.markdown(f"**{medal} Passage {i} • Page {page_no} • Match {sc}%**")
                        st.caption(d.page_content)

            st.session_state.messages.append(
                {"role": "assistant", "content": answer, "sources": pages}
            )
        except Exception as e:
            st.error(f"Error: {e}")   
# import os
# from dotenv import load_dotenv

# from langchain_groq import ChatGroq
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_chroma import Chroma
# from langchain_core.prompts import PromptTemplate
# import shutil

# if os.path.exists("./chroma_db"):
#     shutil.rmtree("./chroma_db")

# print("Old ChromaDB Deleted!")

# load_dotenv()

# groq_api_key = os.getenv("GROQ_API_KEY")

# if not groq_api_key:
#     raise ValueError("Groq API Key Not Found!")

# print("Groq API Key Loaded Successfully!")

# print("\nLoading PDF...")

# loader = PyPDFLoader("information.pdf")
# documents = loader.load()

# print("PDF Loaded Successfully!")
# print("Total Pages:", len(documents))

# text_splitter = RecursiveCharacterTextSplitter(
#     chunk_size=1000,
#     chunk_overlap=200
# )

# chunks = text_splitter.split_documents(documents)

# print("\nText Splitting Completed!")
# print("Total Chunks:", len(chunks))

# embeddings = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )

# print("\nEmbedding Model Loaded Successfully!")

# vector_store = Chroma.from_documents(
#     documents=chunks,
#     embedding=embeddings,
#     persist_directory="./chroma_db"
# )

# print("\nDocuments Stored Successfully in ChromaDB!")

# retriever = vector_store.as_retriever(
#     search_type="similarity",
#     search_kwargs={"k": 1}
# )

# print("\nRetriever Created Successfully!")

# llm = ChatGroq(
#     model="openai/gpt-oss-20b",
#     temperature=0,
#     groq_api_key=groq_api_key
# )

# print("\nGroq LLM Connected Successfully!")

# prompt_template = PromptTemplate(
#     input_variables=["context", "question"],
#     template="""
# You are a Campus Knowledge Assistant.

# Answer the question using only the
# information provided in the context.

# Instructions:
# 1. Give clear and simple answers.
# 2. Answer only from the provided context.
# 3. Do not make up information.
# 4. If the answer is not available,
#    say that it was not found in the documents.
# 5. Do not mention unnecessary technical details.

# Context:
# {context}

# Question:
# {question}

# Answer:
# """
# )


# print("\n" + "=" * 50)
# print("WELCOME TO CAMPUS KNOWLEDGE ASSISTANT")
# print("=" * 50)

# print("\nAsk your questions below.")
# print("Type 'exit' to stop the chatbot.")



# while True:

#     question = input("\nYou: ").strip()

#     if question.lower() in ["exit", "quit", "bye"]:
#         print("\nThank you for using Campus Knowledge Assistant!")
#         break

#     if not question:
#         print("Please enter a valid question.")
#         continue

#     retrieved_docs = retriever.invoke(question)

#     context = "\n\n".join(
#         [doc.page_content for doc in retrieved_docs]
#     )

#     prompt = prompt_template.format(
#         context=context,
#         question=question
#     )

#     response = llm.invoke(prompt)

#     print("\nCampus Assistant:", response.content)
