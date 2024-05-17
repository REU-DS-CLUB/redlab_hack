from st_pages import Page, show_pages, add_page_title
import  streamlit as st

show_pages(
    [
        Page("pages/home.py", "О проекте", "🏠"),
        Page("pages/analysis.py", "Анализ временного ряда", "📊"),
        Page("pages/detection_annomaly.py", "Поиск аномалий в временно ряду", ":chart_with_upwards_trend:")
    ]
)