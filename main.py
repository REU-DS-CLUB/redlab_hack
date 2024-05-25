from st_pages import Page, show_pages, add_page_title
import  streamlit as st

show_pages(
    [
        Page("pages/home.py", "О проекте", "🏠"),
        Page("pages/anomaly_detection.py", "Анализ временного ряда", "📊"),
    ]
)