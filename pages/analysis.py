import streamlit as st
st.set_page_config(
    page_title='analysis_time_series',
    page_icon='📊'
)
st.sidebar.success("Выберете интересующий раздел")
data_file = st.file_uploader("Загрузите данные временного ряда CSV файлом")