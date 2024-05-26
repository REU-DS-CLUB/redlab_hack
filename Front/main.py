"""
Входная точка для приложения FastAPI
"""
from st_pages import Page, show_pages
import streamlit as st

show_pages(
    [
        Page("pages/home.py", "О проекте", "🏠"),
        Page("pages/anomaly_detection.py", "Анализ временного ряда", "📊"),
    ]
)
st.sidebar.success("Выберете интересующий раздел")
st.rerun()