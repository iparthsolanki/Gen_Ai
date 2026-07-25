
# import tempfile
# from dotenv import load_dotenv
# import streamlit as st

# from langchain_community.document_loaders import PyPDFLoader
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_chroma import Chroma
# from langchain_core.prompts import PromptTemplate
# from langchain_groq import ChatGroq

# load_dotenv()

# st.set_page_config(page_title="RAG Chatbot", page_icon="📄")
# st.title("📄 AI Learning Coach - RAG Chatbot")

# uploaded_files = st.file_uploader(
#     "Upload PDF Files",
#     type=["pdf"],
#     accept_multiple_files=True
# )

# if uploaded_files:

#     documents = []

#     with st.spinner("Loading PDFs..."):
#         for pdf in uploaded_files:
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#                 tmp.write(pdf.read())
#                 loader = PyPDFLoader(tmp.name)
#                 documents.extend(loader.load())

#     splitter = RecursiveCharacterTextSplitter(
#         chunk_size=1000,
#         chunk_overlap=200
#     )

#     chunks = splitter.split_documents(documents)

   
#     embedding = HuggingFaceEmbeddings(
#     model_name="sentence-transformers/all-MiniLM-L6-v2"
# )

#     vectorstore = Chroma.from_documents(
#         documents=chunks,
#         embedding=embedding
#     )

#     retriever = vectorstore.as_retriever(
#         search_kwargs={"k":3}
#     )

#     prompt = PromptTemplate(
#         template="""
# You are an AI Learning Coach.

# Answer ONLY from the provided context.

# If the answer is not available in the context, reply:
# "I couldn't find this information in the uploaded documents."

# Context:
# {context}

# Question:
# {question}

# Answer:
# """,
#         input_variables=["context","question"]
#     )

#     llm = ChatGroq(
#     model="openai/gpt-oss-20b",
#     temperature=0
#     )

#     query = st.chat_input("Ask a question about your PDFs")

#     if query:
#         docs = retriever.invoke(query)
#         context = "\n\n".join(doc.page_content for doc in docs)

#         final_prompt = prompt.invoke({
#             "context": context,
#             "question": query
#         })

#         with st.spinner("Generating answer..."):
#             response = llm.invoke(final_prompt)

#         st.subheader("Answer")
#         st.write(response.content)

#         with st.expander("Retrieved Context"):
#             for i, d in enumerate(docs,1):
#                 st.markdown(f"### Chunk {i}")
#                 st.write(d.page_content)
# else:
#     st.info("Upload one or more PDF files to begin.")

import tempfile
from dotenv import load_dotenv
import streamlit as st
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

load_dotenv()

st.set_page_config(page_title="AI Learning Coach", page_icon="📄")
st.title("📄 AI Learning Coach - RAG Chatbot")

if "messages" not in st.session_state:
    st.session_state.messages=[]
if "retriever" not in st.session_state:
    st.session_state.retriever=None

files=st.file_uploader("Upload PDFs",type="pdf",accept_multiple_files=True)

if files and st.session_state.retriever is None:
    docs=[]
    with st.spinner("Processing PDFs..."):
        for pdf in files:
            with tempfile.NamedTemporaryFile(delete=False,suffix=".pdf") as tmp:
                tmp.write(pdf.read())
                docs.extend(PyPDFLoader(tmp.name).load())
        chunks=RecursiveCharacterTextSplitter(chunk_size=1000,chunk_overlap=200).split_documents(docs)
        emb=HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        vs=Chroma.from_documents(chunks,emb)
        st.session_state.retriever=vs.as_retriever(search_kwargs={"k":3})
    st.success("PDFs processed.")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if st.session_state.retriever:
    q=st.chat_input("Ask a question...")
    if q:
        st.session_state.messages.append({"role":"user","content":q})
        with st.chat_message("user"):
            st.markdown(q)
        docs=st.session_state.retriever.invoke(q)
        context="\n\n".join(d.page_content for d in docs)
        prompt=PromptTemplate(
            input_variables=["context","question"],
            template="""You are a helpful AI assistant.
Answer only from the context.
If answer is unavailable, say: I couldn't find this information in the uploaded documents.

Context:
{context}

Question:
{question}

Answer:""")
        llm=ChatGroq(model="openai/gpt-oss-20b",temperature=0)
        ans=llm.invoke(prompt.invoke({"context":context,"question":q})).content
        with st.chat_message("assistant"):
            st.markdown(ans)
        st.session_state.messages.append({"role":"assistant","content":ans})
else:
    st.info("Upload one or more PDF files.")
