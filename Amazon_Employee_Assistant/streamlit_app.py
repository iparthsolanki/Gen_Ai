# python -m streamlit run streamlit_app.py 

import streamlit as st

st.set_page_config(
    page_title="Amazon Employee Policy Assistant",
    page_icon="🤖",
    layout="centered",
)

CATEGORY_LABELS = {
    "rules": "📜 Rules & Company Policies",
    "hr": "🧑‍💼 Employee Benefits & HR",
    "it": "🔐 IT & Cybersecurity",
    "finance": "💰 Finance, Payroll & Expenses",
    "workplace": "🏢 Other Workplace Policies",
    "general": "💬 General",
}

EXAMPLES = [
    "How many days of paid sick leave do I get?",
    "What should I do if I get a phishing email?",
    "How do I claim travel expenses?",
    "How do I report workplace harassment?",
    "What is the code of conduct on conflicts of interest?",
]


@st.cache_resource(show_spinner="Loading PDFs and building indexes... (pehli baar thoda time lagega)")
def load_graph():
    # rag_app import hone par retrievers ek hi baar build hote hain
    from rag_app import app
    return app


graph_app = load_graph()

# ---------- Session state ----------
if "history" not in st.session_state:
    st.session_state.history = []  # list of {"role", "content", "category"}
if "pending" not in st.session_state:
    st.session_state.pending = None

# ---------- Sidebar ----------
with st.sidebar:
    st.header("ℹ️ About")
    st.write(
        "Ye assistant LangGraph + FAISS + Groq se bana hai. "
        "Query ko automatically classify karke sahi PDF se answer deta hai."
    )
    st.markdown("**Categories**")
    for label in CATEGORY_LABELS.values():
        st.markdown(f"- {label}")
    st.caption(
        "⚠️ PDFs public-source research guides hain, official internal "
        "Amazon policy manuals nahi."
    )
    st.divider()
    st.markdown("**Try these**")
    for q in EXAMPLES:
        if st.button(q, use_container_width=True):
            st.session_state.pending = q
    st.divider()
    if st.button("🗑️ Clear chat", use_container_width=True):
        st.session_state.history = []
        st.session_state.pending = None
        st.rerun()

# ---------- Main ----------
st.title("🤖 Amazon Employee Policy Assistant")
st.caption("HR, IT, Finance, Rules aur Workplace policies ke baare mein kuch bhi poochho.")

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("category"):
            st.caption(f"Category: {CATEGORY_LABELS.get(msg['category'], msg['category'])}")

user_input = st.chat_input("Apna sawaal likho...")
query = user_input or st.session_state.pending
st.session_state.pending = None

if query:
    st.session_state.history.append({"role": "user", "content": query})
    with st.chat_message("user"):
        st.markdown(query)

    with st.chat_message("assistant"):
        with st.spinner("Soch raha hu..."):
            try:
                result = graph_app.invoke({
                    "messages": [("human", query)],
                    "query_type": "general",
                    "retrived_context": "",
                })
                answer = result["messages"][-1].content
                category = result.get("query_type", "general")
            except Exception as e:
                answer = f"❌ Error aaya: `{e}`"
                category = None

        st.markdown(answer)
        if category:
            st.caption(f"Category: {CATEGORY_LABELS.get(category, category)}")

    st.session_state.history.append(
        {"role": "assistant", "content": answer, "category": category}
    )
