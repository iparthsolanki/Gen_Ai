from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from typing import TypedDict,Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph,START,END
from pathlib import Path

load_dotenv()

Embedding_model = HuggingFaceEmbeddings(model_name = "sentence-transformers/all-MiniLM-L6-v2")

def build_retriver(pdf_path:str):
    loader = PyPDFLoader(pdf_path)
    document = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = 500,
        chunk_overlap = 100
    )
    
    chunks = splitter.split_documents(document)
    vectorstore = FAISS.from_documents(chunks,Embedding_model)
    
    return vectorstore.as_retriever(search_kwargs = {"k":3})


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

rules_retriever = build_retriver(
    str(DATA_DIR / "01_Amazon_Rules_and_Company_Policies.pdf")
)

hr_retriever = build_retriver(
    str(DATA_DIR / "02_Amazon_Employee_Benefits_and_HR.pdf")
)

it_retriever = build_retriver(
    str(DATA_DIR / "03_Amazon_IT_and_Cybersecurity.pdf")
)

finance_retriever = build_retriver(
    str(DATA_DIR / "04_Amazon_Finance_Payroll_and_Expenses.pdf")
)

workplace_retriever = build_retriver(
    str(DATA_DIR / "05_Amazon_Other_Workplace_Policies.pdf")
)

llm_model = ChatGroq(model = "openai/gpt-oss-20b", temperature=0.4)

class State(TypedDict):
    messages : Annotated[list,add_messages]
    query_type : str
    retrived_context : str 
    
def classifier_node(state:State)->dict:
    """Look at the latest user message and decide which path to take"""
    
    last_message = state['messages'][-1].content
    
    prompt = (
    "Classify the following employee query into exactly ONE category: "
    "'rules', 'hr', 'it', 'finance', 'workplace', or 'general'.\n\n"

    "Use 'rules' for questions about company rules, code of conduct, "
    "conflicts of interest, ethics, anti-bribery, insider trading, "
    "disciplinary conduct, compliance, leadership principles, "
    "or reporting misconduct.\n\n"

    "Use 'hr' for questions about employee benefits, health insurance, "
    "paid leave, sick leave, parental leave, maternity/paternity benefits, "
    "employee assistance programs, career development, promotions, "
    "performance, financial wellness, or employee eligibility for benefits.\n\n"

    "Use 'it' for questions about IT policies, cybersecurity, "
    "passwords, multi-factor authentication, phishing, company laptops, "
    "software usage, data privacy, confidential information, remote access, "
    "security incidents, or responsible AI tool usage.\n\n"

    "Use 'finance' for questions about salary, payslips, payroll, "
    "tax deductions, PF, gratuity, TDS, reimbursements, travel expenses, "
    "expense claims, procurement, invoices, purchasing approvals, "
    "financial records, or business expenses.\n\n"

    "Use 'workplace' for questions about onboarding, recruitment, "
    "workplace harassment, discrimination, POSH, diversity and inclusion, "
    "employee grievances, accommodations, workplace safety, emergencies, "
    "training, business travel, vendor interactions, or environmental "
    "responsibility.\n\n"

    "Use 'general' for greetings, casual conversation, general knowledge, "
    "or questions unrelated to the five employee policy categories.\n\n"

    "Classification rules:\n"
    "1. Choose the category that best matches the main intent of the query.\n"
    "2. If a query clearly concerns a specific benefit, classify it as 'hr'.\n"
    "3. If a query concerns salary calculations, payslips, taxes, or "
    "reimbursements, classify it as 'finance'.\n"
    "4. If a query concerns harassment or workplace complaints, classify "
    "it as 'workplace'.\n"
    "5. Do not answer the query. Only classify it.\n"
    "6. Return exactly one lowercase word from this list: "
    "rules, hr, it, finance, workplace, general.\n\n"

    f"Employee query: {last_message}\n\n"
    "Category:"
) 


# Step 3 - Nodes Generation

# def classifier_node(state: State) -> dict:
#     """Classifies the employee query into the correct category."""

#     last_message = state["messages"][-1].content

#     prompt = (
#         "Classify the following employee query into exactly one category: "
#         "'rules', 'hr', 'it', 'finance', 'workplace', or 'general'.\n\n"

#         "Use 'rules' for company policies, code of conduct, ethics, "
#         "conflicts of interest, compliance, anti-bribery, and misconduct.\n\n"

#         "Use 'hr' for employee benefits, health insurance, leaves, "
#         "parental benefits, career development, performance, and promotions.\n\n"

#         "Use 'it' for cybersecurity, passwords, phishing, company devices, "
#         "data privacy, software usage, and security incidents.\n\n"

#         "Use 'finance' for salary, payslips, payroll, taxes, PF, gratuity, "
#         "reimbursements, expense claims, travel expenses, and procurement.\n\n"

#         "Use 'workplace' for onboarding, recruitment, harassment, POSH, "
#         "discrimination, inclusion, grievances, workplace safety, training, "
#         "and emergency procedures.\n\n"

#         "Use 'general' for greetings, casual conversation, and questions "
#         "unrelated to these employee policy categories.\n\n"

#         "Return only one lowercase word: "
#         "rules, hr, it, finance, workplace, or general.\n\n"

#         f"Employee query: {last_message}\n"
#         "Category:"
#     )

    response = llm_model.invoke(prompt)
    category = response.content.strip().lower()

    valid_categories = [
        "rules", "hr", "it", "finance", "workplace", "general"
    ]

    if category not in valid_categories:
        category = "general"

    return {"query_type": category}


def rules_rag_node(state: State) -> dict:
    """Retrieves relevant information from the rules PDF."""

    query = state["messages"][-1].content
    docs = rules_retriever.invoke(query)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    return {"retrived_context": context}


def hr_rag_node(state: State) -> dict:
    """Retrieves relevant information from the HR PDF."""

    query = state["messages"][-1].content
    docs = hr_retriever.invoke(query)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    return {"retrived_context": context}


def it_rag_node(state: State) -> dict:
    """Retrieves relevant information from the IT PDF."""

    query = state["messages"][-1].content
    docs = it_retriever.invoke(query)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    return {"retrived_context": context}


def finance_rag_node(state: State) -> dict:
    """Retrieves relevant information from the finance PDF."""

    query = state["messages"][-1].content
    docs = finance_retriever.invoke(query)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    return {"retrived_context": context}


def workplace_rag_node(state: State) -> dict:
    """Retrieves relevant information from the workplace PDF."""

    query = state["messages"][-1].content
    docs = workplace_retriever.invoke(query)

    context = "\n\n".join(
        [doc.page_content for doc in docs]
    )

    return {"retrived_context": context}


def general_node(state: State) -> dict:
    """Handles general questions without PDF retrieval."""

    return {
        "retrived_context": "NO_RETRIEVAL_NEEDED"
    }


def response_node(state: State) -> dict:
    """Generates the final employee assistant response."""

    query = state["messages"][-1].content
    context = state.get("retrived_context", "")

    if context == "NO_RETRIEVAL_NEEDED":
        prompt = (
            "You are a friendly AI assistant. Answer greetings and "
            "general questions naturally and concisely.\n\n"
            "Do not invent Amazon employee policies or benefits. "
            "If the user asks for a specific company policy, explain "
            "that the relevant policy document should be consulted.\n\n"
            f"Question: {query}"
        )

    else:
        prompt = (
            "You are an Amazon Employee Policy Assistant.\n\n"
            "Answer the employee's question using only the supplied "
            "document context for Amazon-specific policy claims.\n\n"
            "Rules:\n"
            "1. Do not invent policies, benefits, amounts, deadlines, "
            "eligibility rules, or procedures.\n"
            "2. If the context does not contain the answer, clearly say "
            "that the information could not be verified from the "
            "available documents.\n"
            "3. Remember that the PDFs are public-source research guides, "
            "not official internal Amazon policy manuals.\n"
            "4. Do not present US-specific benefits as applicable to "
            "Amazon India without supporting evidence.\n"
            "5. Give a clear, helpful answer in simple language.\n"
            "6. If the context contains a relevant source name or URL, "
            "include it when useful.\n\n"
            f"Document context:\n{context}\n\n"
            f"Employee question: {query}\n\n"
            "Answer:"
        )

    response = llm_model.invoke(prompt)

    return {"messages": [("ai", response.content.strip())]}


# Step 4 - Router Function

def route_query(state: State) -> str:

    if state["query_type"] == "rules":
        return "rules_rag"

    elif state["query_type"] == "hr":
        return "hr_rag"

    elif state["query_type"] == "it":
        return "it_rag"

    elif state["query_type"] == "finance":
        return "finance_rag"

    elif state["query_type"] == "workplace":
        return "workplace_rag"

    else:
        return "general"


# Step 5 - Building the Graph

graph = StateGraph(State)

graph.add_node("classifier", classifier_node)

graph.add_node("rules_rag", rules_rag_node)
graph.add_node("hr_rag", hr_rag_node)
graph.add_node("it_rag", it_rag_node)
graph.add_node("finance_rag", finance_rag_node)
graph.add_node("workplace_rag", workplace_rag_node)

graph.add_node("general", general_node)
graph.add_node("response", response_node)


# Edges

graph.add_edge(START, "classifier")

graph.add_conditional_edges("classifier",route_query)

graph.add_edge("rules_rag", "response")
graph.add_edge("hr_rag", "response")
graph.add_edge("it_rag", "response")
graph.add_edge("finance_rag", "response")
graph.add_edge("workplace_rag", "response")
graph.add_edge("general", "response")

graph.add_edge("response", END)

app = graph.compile()


# Step 6 - Run the Assistant
# CLI code sirf tab chalega jab rag_app.py directly run hogi.
# FastAPI se import karne par ye code execute nahi hoga.

if __name__ == "__main__":

    print("\nWelcome to Amazon Employee Policy Assistant!\n")

    print("Select a category:")
    print("1. Rules & Company Policies")
    print("2. Employee Benefits & HR")
    print("3. IT Policies & Cybersecurity")
    print("4. Finance, Payroll & Expenses")
    print("5. Other Workplace Policies")
    print("6. General Questions")

    category_map = {
        "1": "rules",
        "2": "hr",
        "3": "it",
        "4": "finance",
        "5": "workplace",
        "6": "general"
    }

    choice = input("\nEnter category number (1-6): ").strip()
    selected_category = category_map.get(choice, "general")

    print(f"\nSelected category: {selected_category}")
    print("Ask your question or type 'exit' to quit.\n")

    while True:

        user_query = input("You: ").strip()

        if user_query.lower() in ["exit", "quit"]:
            print("Goodbye!")
            break

        if not user_query:
            continue

        result = app.invoke({
            "messages": [("human", user_query)],
            "query_type": selected_category,
            "retrived_context": ""
        })

        print(
            f"\nAssistant: {result['messages'][-1].content}\n"
        )