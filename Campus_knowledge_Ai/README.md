# Campus Knowledge Assistant – PDF Based RAG Chatbot

![Uploading image.png…]()


<p align="center">
  **Retrieval-Augmented Generation | LangChain | Groq | ChromaDB | Hugging Face | Streamlit**
</p>

<p align="center">
  An AI-powered document question-answering application that allows users to upload PDF documents and receive context-aware answers using semantic search and Large Language Models.
</p>

---

## 1. Project Overview

**Campus Knowledge Assistant** is an AI-powered Retrieval-Augmented Generation (RAG) application designed to make information retrieval from PDF documents faster, easier, and more interactive.

The application allows users to upload a PDF document and ask questions directly about its content. Instead of generating answers from general knowledge, the system retrieves relevant passages from the uploaded document and uses a Large Language Model to generate answers based on the retrieved information.

The project combines:

- LangChain for document processing and LLM integration.
- Hugging Face for text embeddings.
- ChromaDB for vector storage and semantic retrieval.
- Groq for fast LLM inference.
- Streamlit for the interactive chatbot interface.

The application also provides source-page references, ranked retrieved passages, conversation history, and configurable response temperature.

The main objective is to demonstrate how Retrieval-Augmented Generation can transform static PDF documents into an interactive knowledge assistant.

## 2. Problem Statement

Students and professionals frequently work with large PDF documents containing important information.

Finding a specific answer manually can be time-consuming, especially when information is distributed across multiple pages.

Traditional keyword searches may also fail to understand the meaning or context of a question.

This project addresses these challenges by developing a document-based AI assistant that:

- Accepts PDF documents as input.
- Extracts and processes document content.
- Converts text into numerical embeddings.
- Retrieves relevant passages using semantic similarity.
- Generates answers using an LLM.
- Provides page references for better traceability.

## 3. Project Objectives

- Build a PDF-based question-answering system.
- Implement a Retrieval-Augmented Generation pipeline.
- Extract text from uploaded PDF documents.
- Split extracted text into manageable chunks.
- Generate embeddings using Hugging Face.
- Store document embeddings in ChromaDB.
- Retrieve relevant passages using semantic search.
- Integrate Groq LLM for answer generation.
- Restrict answers to the provided document context.
- Maintain conversation history for follow-up questions.
- Display source-page references.
- Show the top three retrieved passages.
- Build an interactive Streamlit interface.

## 4. Key Features

### PDF Document Upload

Users can upload PDF documents directly through the Streamlit sidebar.

The application also supports a default PDF file named `information.pdf` placed in the project directory.

### Automatic Document Processing

After receiving a PDF, the application automatically:

- Loads the document.
- Extracts text from PDF pages.
- Splits text into smaller chunks.
- Generates vector embeddings.
- Stores the embeddings in ChromaDB.

### Semantic Search

The system retrieves relevant document passages based on the meaning of the user's question rather than relying only on exact keyword matching.

### AI-Powered Answer Generation

Groq LLM generates answers using the retrieved document passages.

The prompt instructs the model to:

- Answer only using the provided context.
- Avoid making up information.
- Use clear and simple language.
- State when information is not available in the document.
- Use chat history to understand follow-up questions.

### Source Page References

The application displays the page number associated with the most relevant retrieved passage.

This helps users identify where the information came from.

### Top 3 Retrieved Passages

Users can expand the retrieved-passage section to inspect:

- Passage ranking.
- Source page number.
- Relevance score.
- Extracted passage content.

### Conversation History

The application maintains conversation history during the current Streamlit session.

The latest six messages are included as context for follow-up questions.

### Dynamic Temperature Control

Users can adjust the LLM temperature from the sidebar.

A lower temperature generally produces more deterministic responses.

### Show Sources Option

Users can enable or disable source references using the sidebar toggle.

### Clear Chat

The Clear Chat button removes the current conversation history.

### Document Change Detection

The application generates an MD5 hash of the uploaded PDF.

When a different document is selected, the previous conversation is automatically reset.

### Professional Dark UI

The Streamlit interface includes:

- Custom dark theme.
- Gradient header.
- Chat-style message containers.
- Sidebar configuration.
- Source relevance indicators.
- Expandable retrieved passages.

---

## 5. System Architecture

The application follows a Retrieval-Augmented Generation architecture.

```text
                  User Uploads PDF
                         |
                         v
                   PDF Document
                         |
                         v
                   PyPDFLoader
                         |
                         v
                   Text Extraction
                         |
                         v
              Recursive Text Splitter
                         |
                         v
                  Text Chunks
                         |
                         v
              Hugging Face Embeddings
                         |
                         v
                    ChromaDB
                         |
                         |
              User Enters a Question
                         |
                         v
                 Semantic Search
                         |
                         v
               Retrieve Top 3 Chunks
                         |
                         v
                 Rank by Similarity
                         |
                         v
                Context Construction
                         |
                         v
                 Prompt Template
                         |
                         v
                    Groq LLM
                         |
                         v
                Generated Answer
                         |
                         v
             Answer + Source References
                         |
                         v
                  Streamlit UI
```

## 6. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| Streamlit | Interactive chatbot interface |
| LangChain | Document processing and LLM integration |
| Groq | Large Language Model inference |
| Hugging Face | Text embedding generation |
| Sentence Transformers | Semantic text embeddings |
| ChromaDB | Vector database |
| PyPDFLoader | PDF text extraction |
| RecursiveCharacterTextSplitter | Document chunking |
| PromptTemplate | Structured prompt construction |
| Python-dotenv | Environment variable management |
| NumPy | Numerical processing |

## 7. Detailed Technical Implementation

### 7.1 PDF Loading

The application uses LangChain's `PyPDFLoader` to extract text and metadata from PDF documents.

```python
documents = PyPDFLoader(tmp_path).load()
```

Each extracted document contains:

- Page content.
- Page metadata.
- Source information.

The PDF is temporarily written to a file before loading and is deleted after extraction.

### 7.2 Text Splitting

Large documents are divided into smaller text chunks using `RecursiveCharacterTextSplitter`.

```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200
)

chunks = splitter.split_documents(documents)
```

**Chunk Size: 1000**

Each chunk contains approximately 1000 characters.

**Chunk Overlap: 200**

Adjacent chunks share approximately 200 characters to preserve contextual continuity.

Why chunking is important:

- Large documents become easier to process.
- Relevant information can be retrieved more precisely.
- LLM context becomes more manageable.
- Smaller passages improve retrieval granularity.

### 7.3 Hugging Face Embeddings

The application uses the following embedding model:

`sentence-transformers/all-MiniLM-L6-v2`

```python
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
```

The embedding model converts text chunks into numerical vector representations.

These vectors capture semantic relationships between text passages.

For example, questions with different wording but similar meaning can retrieve related document content.

### 7.4 ChromaDB Vector Store

ChromaDB stores the document chunks and their corresponding embeddings.

```python
store = Chroma.from_documents(
    documents=chunks,
    embedding=load_embeddings(),
    collection_name=f"docs_{file_hash[:16]}"
)
```

The collection name is based on the uploaded document's hash.

This helps associate the vector collection with the specific uploaded PDF.

The application uses an in-memory Chroma collection rather than a configured persistent database directory.

### 7.5 Semantic Similarity Search

When a user asks a question, the application searches the vector store.

```python
results = vector_store.similarity_search_with_score(
    question,
    k=top_k
)
```

The application retrieves three candidate passages.

```python
top_k = 3
```

The returned results are sorted by distance:

```python
results = sorted(
    results,
    key=lambda r: r[1]
)
```

Lower distance indicates a closer match in the selected similarity metric.

The most relevant passage is placed first.

### 7.6 Relevance Score Display

The application calculates a display score using:

```python
scores = [
    round(100 / (1 + s), 1)
    for _, s in results
]
```

The score is displayed as a percentage-style relevance indicator.

**Important:** This is a transformed vector distance for display, not a calibrated probability or guaranteed measure of answer correctness.

### 7.7 Prompt Engineering

The project uses LangChain's `PromptTemplate` to structure the LLM instructions.

The prompt includes:

- Document context.
- Recent conversation history.
- Current user question.

The model is instructed to answer only from the retrieved document context.

It also prioritizes the most relevant passage and uses additional passages only when necessary.

This helps reduce unsupported answers and irrelevant information.

### 7.8 Groq LLM Integration

The application uses Groq through LangChain's `ChatGroq`.

Configured model:

`openai/gpt-oss-20b`

```python
llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=temperature,
    groq_api_key=api_key
)
```

The temperature is controlled through the Streamlit sidebar.

### 7.9 Streaming Responses

The application streams the generated response instead of waiting for the entire answer.

```python
def token_stream():
    for chunk in llm.stream(prompt):
        if chunk.content:
            yield chunk.content

answer = st.write_stream(token_stream())
```

This improves the interactive experience by displaying generated content progressively.

### 7.10 Conversation History

The application stores chat messages using Streamlit session state.

```python
if "messages" not in st.session_state:
    st.session_state.messages = []
```

The latest six messages are formatted and passed into the prompt.

```python
def format_history(messages, limit=6):
    recent = messages[-limit:]

    return "\n".join(
        f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
        for m in recent
    ) or "None"
```

This supports follow-up questions while keeping the conversation context limited.

### 7.11 Source Attribution

The most relevant retrieved passage is used to identify the primary source page.

```python
pages = [
    (docs[0].metadata.get("page", 0) or 0) + 1
] if docs else []
```

The application displays:

- Best matching page.
- Relevance display score.
- Top three retrieved passages.

PDF page metadata is converted to human-readable page numbering by adding one.

---

## 8. User Interface Walkthrough

### Campus Knowledge Assistant

The main interface contains a gradient header, example questions, chat messages, and a question input field.

![Campus Knowledge Assistant Interface](./campus-knowledge-assistant.png)

### Sidebar Configuration

The sidebar provides the following controls:

| Setting | Description |
|---|---|
| Groq API Key | Enter or load the API key |
| PDF Upload | Upload a PDF document |
| Temperature | Adjust LLM response temperature |
| Show Sources | Enable or disable source references |
| Clear Chat | Reset the conversation |

### Example Questions

Users can ask questions such as:

```text
What is the admission process?

What is the fee structure?

What hostel facilities are available?

What is the minimum attendance requirement?
```

The assistant retrieves relevant information from the active PDF document.

---

## 9. Project Structure

```text
Campus-Knowledge-Assistant/
│
├── main.py
├── information.pdf
├── requirements.txt
├── .env
├── .gitignore
├── README.md
│
└── campus-knowledge-assistant.png
```

### File Description

| File | Description |
|---|---|
| `main.py` | Main Streamlit application |
| `information.pdf` | Optional default PDF document |
| `requirements.txt` | Project dependencies |
| `.env` | Stores the Groq API key |
| `.gitignore` | Excludes sensitive and unnecessary files |
| `README.md` | Project documentation |
| `campus-knowledge-assistant.png` | Application screenshot |

---

## 10. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
```

Move into the project directory:

```bash
cd Campus-Knowledge-Assistant
```

### Step 2: Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

Create a `requirements.txt` file:

```text
streamlit
python-dotenv
langchain
langchain-groq
langchain-community
langchain-text-splitters
langchain-huggingface
langchain-chroma
chromadb
sentence-transformers
pypdf
```

Install the packages:

```bash
pip install -r requirements.txt
```

### Step 4: Configure Groq API Key

Create a `.env` file in the project root directory.

```env
GROQ_API_KEY=your_groq_api_key_here
```

Replace the placeholder with your actual Groq API key.

The application also supports Streamlit secrets.

For deployment, configure the key through the platform's environment variables or secrets management.

**Security Note:** Never upload your `.env` file or expose your API key in a public GitHub repository.

### Step 5: Run the Application

```bash
streamlit run main.py
```

The application will start on the local Streamlit server.

Open the local URL displayed in your terminal, usually:

```text
http://localhost:8501
```

### Step 6: Upload a PDF

1. Open the application.
2. Enter or configure your Groq API key.
3. Upload a PDF document from the sidebar.
4. Wait for document processing.
5. Enter a question in the chat input.
6. Review the generated answer and source references.

---

## 11. Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | API key used for Groq LLM access |

The application loads environment variables using `python-dotenv`.

```python
load_dotenv()
```

It first checks the environment and then attempts to load the key from Streamlit secrets.

---

## 12. Important Implementation Details

### Document-Specific Vector Store

The vector store is cached using the uploaded PDF bytes and file hash.

This avoids rebuilding the same document's embeddings unnecessarily during Streamlit reruns within the application's cache lifecycle.

### In-Memory Storage

The current implementation creates an in-memory Chroma collection.

The application does not configure a persistent ChromaDB directory in its active Streamlit workflow.

Therefore, long-term vector persistence is not part of the current implementation.

### Document-Based Context

The prompt explicitly instructs the LLM to use the retrieved document context rather than general knowledge.

If the requested information is unavailable, the assistant should communicate that it was not found in the document.

### Source Ranking

Three candidate passages are retrieved and sorted by distance.

The first passage is treated as the primary source, while the remaining passages are used when additional context is needed.

---

## 13. Practical Applications

The Campus Knowledge Assistant architecture can be adapted for:

**Educational Institutions**

Students can ask questions about admission guidelines, academic policies, attendance requirements, and course information.

**University Documentation**

Search academic handbooks, examination rules, and institutional documents.

**HR Knowledge Management**

Retrieve information from employee handbooks, HR policies, and workplace guidelines.

**Business Documentation**

Ask questions about reports, manuals, operational documents, and internal knowledge resources.

**Research Assistance**

Retrieve relevant information from research papers, reports, and technical PDFs.

**Personal Document Assistant**

Convert personal PDF collections into searchable question-answering systems.

---

## 14. Limitations

- The application currently supports PDF documents only.
- Scanned PDFs without an OCR text layer may not produce usable extracted text.
- The current ChromaDB implementation uses in-memory storage.
- Large PDFs may require additional processing time and memory.
- Answer quality depends on document quality and retrieval relevance.
- The displayed relevance score is not a calibrated confidence probability.
- The system depends on access to the Groq API.
- The application does not currently implement authentication or multi-user access control.
- Chat history is maintained in Streamlit session state rather than a permanent database.
- The current implementation uses similarity search rather than a hybrid keyword and semantic retrieval strategy.

---

## 15. Future Improvements

Potential improvements for future versions include:

- Add OCR support for scanned PDF documents.
- Support multiple PDF uploads.
- Implement persistent ChromaDB storage.
- Add document management and deletion features.
- Introduce hybrid search using keyword and vector retrieval.
- Add reranking for better passage selection.
- Implement conversation export.
- Add user authentication.
- Add multi-user document isolation.
- Support DOCX, TXT, and other document formats.
- Add document summarization.
- Add citation-level source highlighting.
- Integrate LangGraph for more advanced agentic workflows.
- Deploy the application using Streamlit Community Cloud or another hosting platform.
- Add automated evaluation for retrieval and answer quality.

---

## 16. Key Learnings

Through this project, I gained practical experience with:

- Retrieval-Augmented Generation (RAG).
- PDF document loading and text extraction.
- Recursive text splitting.
- Hugging Face sentence embeddings.
- Semantic similarity search.
- ChromaDB vector storage.
- LangChain document processing.
- Groq LLM integration.
- Prompt engineering.
- Context-aware question answering.
- Streaming LLM responses.
- Conversation history management.
- Source-page attribution.
- Streamlit application development.
- Environment variable and API key management.

---

## 17. Conclusion

Campus Knowledge Assistant demonstrates how Retrieval-Augmented Generation can transform static PDF documents into interactive knowledge sources.

The project combines PDF extraction, text chunking, embedding generation, vector storage, semantic retrieval, and LLM-based answer generation into a single application.

By integrating LangChain, Hugging Face, ChromaDB, Groq, and Streamlit, the application provides an accessible way to ask questions and retrieve document-grounded answers.

The project demonstrates practical implementation knowledge of modern RAG architecture and provides a foundation for developing more advanced document intelligence applications.

---

## Author

**Parth Solanki**

BCA (Hons) Student | AI/ML | Data Science | Generative AI | RAG Systems

---

## License

This project is intended for educational, learning, and portfolio purposes. Add a formal license file if you wish to define reuse permissions.
