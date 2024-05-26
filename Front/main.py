"""
Входная точка для приложения FastAPI
"""
from st_pages import Page, show_pages, add_page_title
import  streamlit as st

show_pages(
    [
        Page("Front/pages/home.py", "О проекте", "🏠"),
        Page("Front/pages/anomaly_detection.py", "Анализ временного ряда", "📊"),
    ]
)
st.sidebar.success("Выберете интересующий раздел")
st.rerun()