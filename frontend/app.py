"""
LegalRAG India - Streamlit Frontend
AI-Powered Legal Research Assistant
"""

import streamlit as st
import requests
from typing import Dict, List
import json

# Configuration
API_URL = "http://localhost:8000"

# Page config
st.set_page_config(
    page_title="Legal AI Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Skeuomorphic beige design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    /* Rich beige background with texture */
    .stApp {
        background: linear-gradient(135deg, #f5e6d3 0%, #e8d5c4 100%);
    }
    
    /* Main content - paper-like card */
    .main .block-container {
        background-color: #fdfbf7;
        padding: 2.5rem;
        box-shadow: 
            0 4px 6px rgba(0, 0, 0, 0.07),
            0 10px 20px rgba(0, 0, 0, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.9);
        border: 1px solid #e8dcc8;
        border-radius: 12px;
    }
    
    /* Headers - embossed style */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #5d4e37;
        margin-bottom: 0.5rem;
        letter-spacing: -0.02em;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.08);
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #8b7355;
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Citation boxes - raised card effect */
    .citation-box {
        background: linear-gradient(145deg, #ffffff 0%, #f9f6f1 100%);
        padding: 1.4rem;
        border-radius: 10px;
        border: 1px solid #ddd0bf;
        border-left: 4px solid #b8956a;
        margin: 0.8rem 0;
        box-shadow: 
            0 2px 4px rgba(0, 0, 0, 0.08),
            0 4px 8px rgba(0, 0, 0, 0.04),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
        transition: all 0.3s ease;
    }
    
    .citation-box:hover {
        box-shadow: 
            0 4px 12px rgba(0, 0, 0, 0.12),
            0 8px 16px rgba(0, 0, 0, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
        transform: translateY(-2px);
    }
    
    .citation-box strong {
        color: #3d2f1f;
        font-size: 1.05rem;
        font-weight: 600;
    }
    
    .citation-box small {
        color: #6b5d4f;
        line-height: 1.6;
    }
    
    /* Confidence badges - embossed pills */
    .confidence-high {
        background: linear-gradient(145deg, #e8f5e9 0%, #d4edda 100%);
        color: #2d5016;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        border: 1px solid #c3e6cb;
        box-shadow: 
            0 2px 4px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }
    
    .confidence-medium {
        background: linear-gradient(145deg, #fff8e1 0%, #fff3cd 100%);
        color: #6d4c00;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        border: 1px solid #ffeaa7;
        box-shadow: 
            0 2px 4px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }
    
    .confidence-low {
        background: linear-gradient(145deg, #ffebee 0%, #f8d7da 100%);
        color: #5f2120;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.9rem;
        display: inline-block;
        border: 1px solid #f5c6cb;
        box-shadow: 
            0 2px 4px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }
    
    /* Input fields - inset effect */
    .stTextInput input {
        background: linear-gradient(145deg, #f9f6f1 0%, #ffffff 100%);
        border: 1.5px solid #d4c4b0;
        border-radius: 8px;
        padding: 0.75rem 1rem;
        font-size: 0.95rem;
        color: #3d2f1f;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    
    .stTextInput input::placeholder {
        color: #9b8b7e !important;
        opacity: 1;
    }
    
    .stTextInput input:focus {
        border-color: #b8956a;
        box-shadow: 
            inset 0 2px 4px rgba(0, 0, 0, 0.05),
            0 0 0 3px rgba(184, 149, 106, 0.15);
        background: #ffffff;
    }
    
    /* Buttons - raised 3D effect */
    .stButton button {
        background: linear-gradient(145deg, #ffffff 0%, #f5f1eb 100%);
        border: 1.5px solid #d4c4b0;
        border-radius: 8px;
        font-weight: 600;
        font-size: 0.95rem;
        color: #5d4e37;
        padding: 0.65rem 1.5rem;
        box-shadow: 
            0 2px 0 #c9b89f,
            0 4px 8px rgba(0, 0, 0, 0.1);
        transition: all 0.15s ease;
    }
    
    .stButton button:hover {
        background: linear-gradient(145deg, #f5f1eb 0%, #ebe4d9 100%);
        border-color: #b8956a;
        transform: translateY(-1px);
        box-shadow: 
            0 3px 0 #c9b89f,
            0 6px 12px rgba(0, 0, 0, 0.12);
    }
    
    .stButton button:active {
        transform: translateY(1px);
        box-shadow: 
            0 1px 0 #c9b89f,
            0 2px 4px rgba(0, 0, 0, 0.08);
    }
    
    .stButton button[kind="primary"] {
        background: linear-gradient(145deg, #c9a876 0%, #b8956a 100%);
        border: 1.5px solid #a68455;
        color: #ffffff;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.2);
        box-shadow: 
            0 2px 0 #9d7a4f,
            0 4px 8px rgba(0, 0, 0, 0.15);
    }
    
    .stButton button[kind="primary"]:hover {
        background: linear-gradient(145deg, #d4b584 0%, #c9a876 100%);
        box-shadow: 
            0 3px 0 #9d7a4f,
            0 6px 12px rgba(0, 0, 0, 0.18);
    }
    
    /* Sidebar - warm paper texture */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #fdfbf7 0%, #f5f1eb 100%);
        border-right: 1px solid #d4c4b0;
        box-shadow: inset -4px 0 8px rgba(0, 0, 0, 0.03);
    }
    
    /* Fix sidebar text colors */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div {
        color: #5d4e37 !important;
    }
    
    /* Sidebar buttons - warm earth tones */
    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(145deg, #f5f1eb 0%, #ebe4d9 100%);
        color: #5d4e37 !important;
        border: 1px solid #d4c4b0;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: linear-gradient(145deg, #ebe4d9 0%, #e0d5c7 100%);
        border-color: #b8956a;
    }
    
    /* Sidebar success box - olive/sage green */
    [data-testid="stSidebar"] .stSuccess {
        background: linear-gradient(145deg, #e8f0e3 0%, #d8e8cf 100%) !important;
        border: 1px solid #c3d9b5 !important;
        color: #3d5a2c !important;
    }
    
    [data-testid="stSidebar"] .stSuccess * {
        color: #3d5a2c !important;
    }
    
    /* Sidebar info box - warm beige */
    [data-testid="stSidebar"] .stInfo {
        background: linear-gradient(145deg, #f0e8dc 0%, #e8dcc8 100%) !important;
        border: 1px solid #d4c4b0 !important;
        color: #5d4e37 !important;
    }
    
    [data-testid="stSidebar"] .stInfo * {
        color: #5d4e37 !important;
    }
    
    [data-testid="stSidebar"] .stInfo svg {
        fill: #b8956a !important;
    }
    
    /* Sidebar warning box - amber */
    [data-testid="stSidebar"] .stWarning {
        background: linear-gradient(145deg, #fff8e1 0%, #fff3cd 100%) !important;
        border: 1px solid #ffeaa7 !important;
        color: #6d4c00 !important;
    }
    
    [data-testid="stSidebar"] .stWarning * {
        color: #6d4c00 !important;
    }
    
    /* Sidebar error box - maroon */
    [data-testid="stSidebar"] .stError {
        background: linear-gradient(145deg, #f5e6e8 0%, #ead5d8 100%) !important;
        border: 1px solid #d8c1c4 !important;
        color: #6b3a3e !important;
    }
    
    [data-testid="stSidebar"] .stError * {
        color: #6b3a3e !important;
    }
    
    /* Nuclear option - override ALL Streamlit alert classes in sidebar */
    [data-testid="stSidebar"] div[data-baseweb="notification"] {
        background: linear-gradient(145deg, #f0e8dc 0%, #e8dcc8 100%) !important;
        border: 1px solid #d4c4b0 !important;
    }
    
    [data-testid="stSidebar"] div[data-baseweb="notification"] * {
        color: #5d4e37 !important;
    }
    
    /* Tabs - raised tab effect */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: linear-gradient(145deg, #ebe4d9 0%, #e0d5c7 100%);
        padding: 0.5rem;
        border-radius: 10px 10px 0 0;
        box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(145deg, #f5f1eb 0%, #ebe4d9 100%);
        border-radius: 6px;
        color: #5d4e37;
        font-weight: 600;
        padding: 0.65rem 1.25rem;
        border: 1px solid #d4c4b0;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(145deg, #ffffff 0%, #f9f6f1 100%);
        color: #3d2f1f;
        border-bottom: 3px solid #b8956a;
        box-shadow: 
            0 -2px 8px rgba(0, 0, 0, 0.08),
            inset 0 1px 0 rgba(255, 255, 255, 0.8);
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        color: #b8956a !important;
        font-weight: 700;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
    }
    
    /* Info/Success/Warning boxes - embossed */
    .stSuccess {
        background: linear-gradient(145deg, #e8f0e3 0%, #d8e8cf 100%);
        border: 1px solid #c3d9b5;
        border-radius: 8px;
        color: #3d5a2c !important;
        box-shadow: 
            0 2px 4px rgba(0, 0, 0, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }
    
    .stInfo {
        background: linear-gradient(145deg, #f0e8dc 0%, #e8dcc8 100%);
        border: 1px solid #d4c4b0;
        border-radius: 8px;
        color: #5d4e37 !important;
        box-shadow: 
            0 2px 4px rgba(0, 0, 0, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }
    
    .stWarning {
        background: linear-gradient(145deg, #fff8e1 0%, #fff3cd 100%);
        border: 1px solid #ffeaa7;
        border-radius: 8px;
        color: #6d4c00 !important;
        box-shadow: 
            0 2px 4px rgba(0, 0, 0, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }
    
    .stError {
        background: linear-gradient(145deg, #f5e6e8 0%, #ead5d8 100%);
        border: 1px solid #d8c1c4;
        border-radius: 8px;
        color: #6b3a3e !important;
        box-shadow: 
            0 2px 4px rgba(0, 0, 0, 0.06),
            inset 0 1px 0 rgba(255, 255, 255, 0.5);
    }
    
    /* Fix all text to be dark brown */
    .stMarkdown, p, h1, h2, h3, h4, h5, h6, label, span, div, li {
        color: #3d2f1f !important;
    }
    
    /* Markdown headings in main content */
    .main h1, .main h2, .main h3 {
        color: #5d4e37 !important;
        border-bottom: none !important;
    }
    
    /* Remove horizontal lines after headers */
    .main hr {
        display: none;
    }
    
    /* Input labels */
    .stTextInput label {
        color: #5d4e37 !important;
        font-weight: 500;
    }
    
    /* Fix placeholder text - make it visible */
    .stTextInput input::placeholder {
        color: #9d8b7a !important;
        opacity: 0.7;
    }
    
    /* Slider label */
    .stSlider label {
        color: #5d4e37 !important;
    }
    
    /* Fix sidebar markdown - remove all blue/green */
    [data-testid="stSidebar"] .stMarkdown,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] li,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] div,
    [data-testid="stSidebar"] strong,
    [data-testid="stSidebar"] em {
        color: #5d4e37 !important;
    }
    
    /* Example question buttons - make them look more clickable */
    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(145deg, #f5f1eb 0%, #ebe4d9 100%);
        color: #5d4e37 !important;
        border: 1px solid #d4c4b0;
        text-align: left;
        font-weight: 500;
        transition: all 0.2s ease;
    }
    
    [data-testid="stSidebar"] .stButton button:hover {
        background: linear-gradient(145deg, #e8dcc8 0%, #d9c9b5 100%);
        border-color: #b8956a;
        transform: translateX(4px);
        box-shadow: -2px 2px 8px rgba(0, 0, 0, 0.08);
    }
    
    /* Scrollbar - leather-like */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: linear-gradient(145deg, #ebe4d9 0%, #e0d5c7 100%);
        border-radius: 5px;
        box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.1);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(145deg, #b8956a 0%, #a68455 100%);
        border-radius: 5px;
        border: 2px solid #ebe4d9;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.15);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(145deg, #c9a876 0%, #b8956a 100%);
    }
</style>
""", unsafe_allow_html=True)


def check_backend_health():
    """Check if backend is running"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        return response.json()
    except:
        return None


def search_cases(query: str, top_k: int = 3) -> Dict:
    """Search for relevant cases"""
    try:
        response = requests.post(
            f"{API_URL}/search",
            json={"query": query, "top_k": top_k},
            timeout=30
        )
        return response.json()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def ask_question(query: str, top_k: int = 3) -> Dict:
    """Ask a legal question"""
    try:
        response = requests.post(
            f"{API_URL}/ask",
            json={"query": query, "top_k": top_k},
            timeout=60
        )
        return response.json()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def display_citations(citations: List[Dict]):
    """Display case citations nicely"""
    st.markdown("### 📚 Case Citations")
    
    for i, citation in enumerate(citations, 1):
        with st.container():
            st.markdown(f"""
<div class="citation-box">
    <strong>{i}. {citation['title']}</strong><br>
    <small>
        🏛️ {citation['court']}<br>
        📅 {citation['date']}<br>
        📋 {citation.get('case_number', 'N/A')}<br>
        🎯 Relevance: {citation['relevance_score']:.3f}
    </small>
</div>
            """, unsafe_allow_html=True)


def display_confidence(confidence: str):
    """Display confidence badge"""
    confidence_class = f"confidence-{confidence.lower()}"
    return f'<span class="{confidence_class}">Confidence: {confidence.upper()}</span>'


def main():
    # Header
    st.markdown('<p class="main-header">⚖️ Legal AI Assistant(न्याय सहायक)</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Your AI companion for Indian legal research. Whether you\'re a law student, paralegal, or just curious about Indian law, ask questions and get clear answers backed by real Supreme Court cases. Search hundreds of judgments instantly with smart semantic search.</p>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## About")
        st.info("""
        **Legal AI Assistant** uses AI to help you research Indian case law.
        
        - 🔍 Semantic search over 1,994+ Supreme Court judgments
        - 🤖 AI-powered answers with verified citations
        - ⚡ Powered by Groq (Llama 3.3 70B)
        """)
        
        # Check backend status
        health = check_backend_health()
        if health:
            st.success("✅ Backend: Online")
            if health.get("components"):
                total_docs = health["components"].get("total_documents", 0)
                st.metric("Total Cases", f"{total_docs:,}")
        else:
            st.error("❌ Backend: Offline")
            st.warning("Please start the backend:\n```\ncd backend\npython main.py\n```")
        
        st.markdown("---")
        
        # Example questions
        st.markdown("## Example Questions")
        example_questions = [
            "What are grounds for eviction of a tenant?",
            "Can employer terminate without notice?",
            "What is punishment for murder under IPC?",
            "How long to execute a civil decree?",
            "Grounds for termination of government employee?"
        ]
        
        for q in example_questions:
            if st.button(q, key=q, use_container_width=True):
                st.session_state.query = q
                st.rerun()
    
    # Default number of results (hidden from user)
    num_results = 3
    
    # Main content
    tab1, tab2 = st.tabs(["Ask Question", "Search Cases"])
    
    # Tab 1: Ask Question (RAG)
    with tab1:
        st.markdown("### Ask a Legal Question")
        st.markdown("Get AI-generated answers based on real Supreme Court cases.")
        
        # Get query from session state or input
        default_query = st.session_state.get("query", "")
        query = st.text_input(
            "Your question:",
            value=default_query,
            placeholder="e.g., What are the legal rights of a landlord to evict a tenant?",
            key="ask_input"
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            ask_button = st.button("Ask", type="primary", use_container_width=True)
        with col2:
            if st.button("Clear", use_container_width=True):
                st.session_state.query = ""
                st.rerun()
        
        if ask_button and query:
            with st.spinner("Searching case law and generating answer..."):
                result = ask_question(query, top_k=num_results)
            
            if result:
                # Display answer
                st.markdown("### 📝 Answer")
                
                # Confidence badge
                confidence = result.get("confidence", "unknown")
                st.markdown(display_confidence(confidence), unsafe_allow_html=True)
                
                # Warning if present
                if result.get("warning"):
                    st.warning(f"⚠️ {result['warning']}")
                
                # Answer
                st.markdown(result.get("answer", "No answer generated"))
                
                # Citations
                citations = result.get("citations", [])
                if citations:
                    st.markdown("---")
                    display_citations(citations)
                
                # Metadata
                with st.expander("ℹ️ Technical Details"):
                    st.json({
                        "model": result.get("model", "N/A"),
                        "retrieved_cases": result.get("retrieved_cases", 0),
                        "confidence": confidence
                    })
    
    # Tab 2: Search Cases
    with tab2:
        st.markdown("### Search Legal Cases")
        st.markdown("Find relevant Supreme Court judgments using semantic search.")
        
        search_query = st.text_input(
            "Search query:",
            placeholder="e.g., property dispute landlord tenant",
            key="search_input"
        )
        
        col1, col2 = st.columns([1, 5])
        with col1:
            search_button = st.button("Search", type="primary", use_container_width=True, key="search_btn")
        
        if search_button and search_query:
            with st.spinner("Searching..."):
                result = search_cases(search_query, top_k=num_results)
            
            if result:
                results = result.get("results", [])
                st.success(f"Found {len(results)} relevant cases")
                
                for i, case in enumerate(results, 1):
                    meta = case["metadata"]
                    score = case["score"]
                    
                    with st.container():
                        st.markdown(f"""
<div class="citation-box">
    <strong>{i}. {meta['title']}</strong><br>
    <small>
        🏛️ {meta['court']}<br>
        📅 {meta['date']}<br>
        📋 {meta.get('casenumber', 'N/A')}<br>
        🎯 Relevance Score: {score:.3f}
    </small>
</div>
                        """, unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #6b5d52; font-size: 0.9rem;'>
        <p>⚖️ Legal AI Assistant | Built with Streamlit, FastAPI, and Groq</p>
        <p><em>Disclaimer: This is an AI assistant for research purposes only. Not a substitute for legal advice.</em></p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()