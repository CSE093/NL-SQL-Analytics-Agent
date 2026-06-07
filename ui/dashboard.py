import streamlit as st
import logging
from agent.controller import run_agent_stream
from services.upload_service import list_user_tables
from services.history_service import log_query
from ui.components import render_metric_card, render_download_buttons, render_sql_code

logger = logging.getLogger(__name__)

def render_dashboard() -> None:
    """Renders the main dashboard search bar, status loader, and result panels."""
    st.markdown(
        """
        <div style="margin-top: -30px; margin-bottom: 25px;">
            <h1 style="font-family: 'Outfit', sans-serif; font-weight: 700; color: #ffffff;">📊 Business Intelligence Center</h1>
            <p style="color: #a3a3a3; font-size: 1.1rem; margin-top: -5px;">Ask business questions in natural language and get SQL results and interactive charts instantly.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Check database status
    tables = list_user_tables()
    if not tables:
        st.warning("⚠️ Welcome! Please start by uploading your data files (CSV/Excel) in the sidebar to populate the database.")
        st.info("💡 Once uploaded, you'll be able to query tables like 'customers', 'orders', etc., in plain English.")
        return

    # Initialize current_query key in session state if not present
    if "current_query" not in st.session_state:
        st.session_state.current_query = ""

    replay_question = st.session_state.pop("history_replay_question", "")

    def run_analysis(query_text: str, record_history: bool = True) -> None:
        """Executes the agent and renders the result panels for a query."""
        with st.status("🔮 Analytical Agent thinking...", expanded=True) as status:
            agent_stream = run_agent_stream(query_text)
            final_res = None

            try:
                for step in agent_stream:
                    node_name = step["node"]
                    node_status = step["status"]

                    logger.info(f"Node execution: {node_name} | Status: {node_status}")
                    status.update(label=f"🔄 {node_status}", state="running")
                    st.write(f"✓ {node_status}")
                    final_res = step["state"]

                if final_res and final_res.get("success", False):
                    status.update(label="✨ Analysis Completed Successfully!", state="complete", expanded=False)
                else:
                    status.update(label="❌ Analysis Failed to resolve.", state="error", expanded=True)

            except Exception as e:
                status.update(label=f"💥 Critical error occurred: {str(e)}", state="error", expanded=True)
                logger.error(f"Error while rendering stream: {str(e)}")

        if not final_res:
            return

        st.session_state.current_query = ""

        success = final_res.get("success", False)
        sql_query = final_res.get("generated_sql")
        errors = final_res.get("errors", [])
        df = final_res.get("data")
        explanation = final_res.get("explanation")
        fig = final_res.get("visualization")
        exec_time = final_res.get("execution_time_ms", 0.0)
        retries = final_res.get("retry_count", 0)

        if record_history:
            last_err = errors[-1] if errors else None
            log_query(
                question=query_text,
                sql_query=sql_query,
                explanation=explanation,
                success=success,
                error_message=last_err,
                execution_time_ms=exec_time
            )

        if success:
            st.balloons()

            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                render_metric_card("Query Execution", f"{exec_time:.1f} ms", "Database retrieval speed", "⚡")
            with col_m2:
                render_metric_card("Dataset Rows", f"{len(df) if df is not None else 0}", "Total records returned", "📊")
            with col_m3:
                render_metric_card("Self-Correction Loops", f"{retries} / 3", "Model retries required", "🔧")

            st.markdown("### 📝 Business Summary")
            st.info(explanation)

            if fig is not None:
                st.markdown("### 📈 Data Visualization")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ℹ️ No dynamic visualization generated (results require at least two attributes or numeric values).")

            st.markdown("### 📋 Results Dataset")
            if df is not None and not df.empty:
                st.dataframe(df, use_container_width=True)
                render_download_buttons(df, filename_prefix="sql_analysis_results")
            else:
                st.warning("The query executed successfully but returned zero rows of data.")

            if sql_query:
                with st.expander("🛠️ Show SQL Query Details", expanded=False):
                    render_sql_code(sql_query)
                    if retries > 0:
                        st.write("---")
                        st.markdown("**Correction History Logs:**")
                        for idx, err in enumerate(errors):
                            st.error(f"Attempt {idx+1} Error: {err}")

        else:
            st.error("### ❌ Could not resolve your query")
            st.markdown(
                "The Analytics Agent failed to generate or execute a working query. "
                "This usually happens due to missing columns or complex requirements. Details below:"
            )

            for idx, err in enumerate(errors):
                st.markdown(f"**Error Log {idx+1}:**")
                st.code(err)

            if sql_query:
                st.markdown("**Last SQL attempted:**")
                st.code(sql_query, language="sql")

    # Input search form
    with st.form(key="query_form", clear_on_submit=False):
        # We tie the input to session state value
        query_input = st.text_input(
            "💬 Ask a question about your data:",
            value=st.session_state.current_query,
            placeholder="e.g., Show top 10 products by revenue",
            help="Type your question in natural language. The agent will discover the database schema, write safe SQL, and explain the result."
        )
        submit_button = st.form_submit_button(label="🚀 Execute Analysis")

    # If the user submitted a query
    if submit_button and query_input.strip():
        # Sync the session state
        st.session_state.current_query = query_input
        run_analysis(query_input, record_history=True)

    if replay_question:
        run_analysis(replay_question, record_history=False)
