import streamlit as st
import logging
from services.upload_service import (
    list_user_tables,
    save_uploaded_file,
    process_and_import_file,
    delete_user_table,
)
from tools.schema_tool import get_schema
from services.history_service import get_history, clear_history
from database.db_manager import reset_db

logger = logging.getLogger(__name__)

def render_sidebar() -> None:
    """Renders the sidebar interface containing file ingestion, schema views, and history."""
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align: center; margin-bottom: 20px;">
                <h2 style="color: #636EFA; margin-bottom: 5px;">📊 AnalyticsGPT</h2>
                <p style="color: #8c8c8c; font-size: 0.85rem;">Natural Language to SQL Agent</p>
            </div>
            <hr style="border-color: #2d2d2d; margin-top: 0; margin-bottom: 20px;" />
            """,
            unsafe_allow_html=True
        )

        # ---------------------------------------------
        # New Chat control
        # ---------------------------------------------
        if st.button("➕ New Chat", use_container_width=True, help="Start a fresh chat session, clearing current query and context"):
            for k in ["current_query", "history_replay_question"]:
                if k in st.session_state:
                    del st.session_state[k]
            st.toast("Started new chat.")
            st.rerun()

        # ---------------------------------------------
        # Section 1: File Uploader
        # ---------------------------------------------
        st.markdown("### 📥 Ingest Datasets")
        uploaded_files = st.file_uploader(
            "Upload CSV or Excel files",
            type=["csv", "xlsx"],
            accept_multiple_files=True,
            help="Upload data tables to convert them automatically to SQLite tables."
        )

        if uploaded_files:
            for uploaded_file in uploaded_files:
                # Use a session state set to prevent infinite loop reprocessing
                processed_key = f"processed_{uploaded_file.name}_{uploaded_file.size}"
                if processed_key not in st.session_state:
                    with st.spinner(f"Ingesting {uploaded_file.name}..."):
                        try:
                            # Save raw file
                            bytes_content = uploaded_file.getvalue()
                            saved_path = save_uploaded_file(uploaded_file.name, bytes_content)
                            
                            # Ingest into DB
                            table_name, rows = process_and_import_file(saved_path)
                            st.toast(f"✅ Table '{table_name}' ingested! ({rows} rows)", icon="🔥")
                            st.session_state[processed_key] = True
                        except Exception as e:
                            st.error(f"Failed to ingest {uploaded_file.name}: {str(e)}")
                            logger.error(f"Ingest failed for {uploaded_file.name}: {str(e)}")

        # ---------------------------------------------
        # Section 2: Uploaded Tables & Schema Discoverer
        # ---------------------------------------------
        st.markdown("### 🗄️ Database Tables")
        tables = list_user_tables()
        
        if not tables:
            st.info("No tables uploaded yet. Use the uploader above.")
        else:
            selected_table = st.selectbox("Select table to inspect schema:", tables)
            
            if selected_table:
                # Fetch schema from schema tool
                schema = get_schema()
                columns = schema.get(selected_table, [])
                
                # Display fields as neat expandable list
                with st.expander(f"📋 {selected_table} Schema", expanded=True):
                    for col in columns:
                        pk_indicator = "🔑" if col["primary_key"] else "🔹"
                        st.markdown(
                            f"<div style='font-size: 0.85rem; padding: 2px 0;'>"
                            f"<strong>{pk_indicator} {col['name']}</strong>: "
                            f"<span style='color: #636EFA;'>{col['type']}</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )

                st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
                if st.button("🗑️ Delete Selected Table", use_container_width=True, help="Permanently drops the selected table from SQLite."):
                    try:
                        delete_user_table(selected_table)
                        st.toast(f"Table '{selected_table}' deleted successfully.", icon="🗑️")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to delete table '{selected_table}': {str(e)}")
                        logger.error(f"Delete table failed for {selected_table}: {str(e)}")

        st.markdown("<hr style='border-color: #2d2d2d; margin: 20px 0;' />", unsafe_allow_html=True)

        # ---------------------------------------------
        # Section 3: History & Session State Recall
        # ---------------------------------------------
        st.markdown("### 🕰️ Query History")
        history = get_history(limit=15)
        
        if not history:
            st.info("No queries executed yet.")
        else:
            for entry in history:
                success_emoji = "🟢" if entry["success"] else "🔴"
                btn_label = f"{success_emoji} {entry['question'][:30]}..."
                
                # Render query history trigger button
                if st.button(btn_label, key=f"hist_{entry['id']}", help=entry["question"], use_container_width=True):
                    # Replay the saved question in the dashboard so the user sees the prior result again.
                    st.session_state.current_query = entry["question"]
                    st.session_state.history_replay_question = entry["question"]
                    st.rerun()

            # Clear history helper button
            st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️ Clear History", use_container_width=True):
                clear_history()
                st.toast("Query history cleared successfully!")
                st.rerun()

        # ---------------------------------------------
        # Section 4: DB Reset Utility
        # ---------------------------------------------
        st.markdown("<hr style='border-color: #2d2d2d; margin: 20px 0;' />", unsafe_allow_html=True)
        if st.button("⚠️ Reset Database", help="Wipes all tables and data history", use_container_width=True):
            reset_db()
            # Clear all session states
            for k in list(st.session_state.keys()):
                del st.session_state[k]
            st.toast("Database reset completely!")
            st.rerun()
