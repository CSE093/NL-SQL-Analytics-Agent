import streamlit as st
import logging
import os
from dotenv import load_dotenv

# Initialize logging configuration before anything else
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("analytics_agent.log", encoding="utf-8")
    ]
)
logger = logging.getLogger(__name__)

# Load config
load_dotenv()

from database.db_manager import init_db
from ui.sidebar import render_sidebar
from ui.dashboard import render_dashboard

# Streamlit page configurations
st.set_page_config(
    page_title="AnalyticsGPT - NL SQL Analytics Agent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Premium Styling (Dark Mode & Professional Polish)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700&display=swap');

    /* Global body styling override */
    html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {
        font-family: 'Inter', sans-serif;
        background-color: #0e0e11 !important;
        color: #e5e5e7 !important;
    }
    
    /* Sidebar styling overrides */
    [data-testid="stSidebar"] {
        background-color: #121215 !important;
        border-right: 1px solid #202025 !important;
    }
    
    /* Input search form overrides */
    input {
        background-color: #16161a !important;
        border: 1px solid #2b2b35 !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif;
    }
    input:focus {
        border-color: #636EFA !important;
        box-shadow: 0 0 0 1px #636EFA !important;
    }
    
    /* Button transition animation polish */
    div.stButton > button {
        background-color: #26262b !important;
        color: #ffffff !important;
        border: 1px solid #3c3c45 !important;
        border-radius: 6px !important;
        font-family: 'Outfit', sans-serif !important;
        font-weight: 500 !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }
    
    div.stButton > button:hover {
        background-color: #636EFA !important;
        color: #ffffff !important;
        border-color: #636EFA !important;
        box-shadow: 0 4px 12px rgba(99, 110, 250, 0.3) !important;
        transform: translateY(-1px);
    }
    
    div.stButton > button:active {
        transform: translateY(1px);
    }

    /* Target specific form execute submit button */
    form[data-testid="stForm"] div.stButton > button {
        background-color: #636EFA !important;
        border-color: #636EFA !important;
    }
    form[data-testid="stForm"] div.stButton > button:hover {
        background-color: #5059d4 !important;
    }
    
    /* Hide default Streamlit footer */
    footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    logger.info("Starting AnalyticsGPT Application...")
    
    # Initialize the database (creates tables like query_history)
    try:
        init_db()
    except Exception as e:
        st.error(f"Database initialization failed: {str(e)}")
        logger.critical(f"Failed to start database manager: {str(e)}")
        return
        
    # Render layout segments
    render_sidebar()
    render_dashboard()

if __name__ == "__main__":
    main()
