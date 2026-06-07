import io
import streamlit as st
import pandas as pd
from typing import Optional

def render_metric_card(label: str, value: str, subtext: Optional[str] = None, icon: Optional[str] = None) -> None:
    """
    Renders a premium styled metric card with support for dark mode.
    """
    icon_html = f"<span style='font-size: 1.5rem; margin-right: 8px;'>{icon}</span>" if icon else ""
    subtext_html = f"<div style='font-size: 0.8rem; color: #a3a3a3; margin-top: 4px;'>{subtext}</div>" if subtext else ""
    
    st.markdown(
        f"""
        <div style="
            background-color: #1e1e1e;
            border: 1px solid #2d2d2d;
            border-radius: 8px;
            padding: 16px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            margin-bottom: 12px;
        ">
            <div style="display: flex; align-items: center; color: #8c8c8c; font-size: 0.9rem; font-weight: 500;">
                {icon_html} {label}
            </div>
            <div style="font-size: 1.8rem; font-weight: 700; color: #ffffff; margin-top: 8px; font-family: 'Outfit', sans-serif;">
                {value}
            </div>
            {subtext_html}
        </div>
        """,
        unsafe_allow_html=True
    )

def render_download_buttons(df: pd.DataFrame, filename_prefix: str = "query_results") -> None:
    """
    Generates download buttons for CSV and Excel formats of a DataFrame side-by-side.
    """
    col1, col2 = st.columns(2)
    
    # CSV generation
    csv_data = df.to_csv(index=False).encode('utf-8')
    with col1:
        st.download_button(
            label="📥 Download CSV",
            data=csv_data,
            file_name=f"{filename_prefix}.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    # Excel generation
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Results')
    excel_data = excel_buffer.getvalue()
    
    with col2:
        st.download_button(
            label="📊 Download Excel",
            data=excel_data,
            file_name=f"{filename_prefix}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

def render_sql_code(sql_query: str) -> None:
    """Renders SQL code cleanly with a copy block."""
    st.markdown("#### 🔍 Generated SQL Query")
    st.code(sql_query, language="sql")
