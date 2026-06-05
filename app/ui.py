import streamlit as st
import requests

API_URL = "http://localhost:8000"

st.set_page_config(
    page_title="Real Estate Document Intelligence",
    page_icon="🏠",
    layout="wide"
)

# Initialize session state
if "uploaded" not in st.session_state:
    st.session_state.uploaded = False
if "question" not in st.session_state:
    st.session_state.question = ""

st.title("🏠 Real Estate Document Intelligence")
st.caption("Upload any Indian property document and ask questions in plain English")

# Sidebar — upload
with st.sidebar:
    st.header("📄 Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF", type="pdf")
    
    if uploaded_file and not st.session_state.uploaded:
        with st.spinner("Ingesting document..."):
            response = requests.post(
                f"{API_URL}/upload",
                files={"file": (uploaded_file.name, uploaded_file, "application/pdf")}
            )
        if response.status_code == 200:
            data = response.json()
            st.session_state.uploaded = True
            st.success(f"✅ Ingested successfully")
            st.metric("Pages", data["pages"])
            st.metric("Chunks", data["chunks"])
        else:
            st.error("Upload failed")
    
    if st.session_state.uploaded:
        st.success("✅ Document ready")
    
    st.divider()
    st.header("💡 Sample Questions")
    sample_questions = [
        "What is the penalty if builder delays possession?",
        "What is the grace period for the developer?",
        "Under which act is arbitration conducted?",
        "What are the payment milestones?",
        "Can the allottee cancel the agreement?"
    ]
    for q in sample_questions:
        if st.button(q, use_container_width=True):
            st.session_state.question = q

# Main area — query
st.header("Ask a Question")

question = st.text_input(
    "Your question",
    value=st.session_state.question,
    placeholder="e.g. What is the penalty if builder delays possession?"
)

if st.button("🔍 Search", type="primary") and question:
    health = requests.get(f"{API_URL}/health").json()
    if not health["vectorstore_ready"]:
        st.warning("Please upload a document first")
    else:
        with st.spinner("Searching document..."):
            response = requests.post(
                f"{API_URL}/query",
                json={"question": question}
            )
        
        if response.status_code == 200:
            data = response.json()
            st.subheader("Answer")
            st.write(data["answer"])
            st.subheader("Sources")
            for i, source in enumerate(data["sources"]):
                with st.expander(f"Source {i+1} — Page {source['page'] + 1}"):
                    st.text(source["content"])
        else:
            st.error(f"Query failed: {response.text}")