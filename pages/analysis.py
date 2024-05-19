import streamlit as st
import pandas as pd
st.set_page_config(
    page_title='analysis_time_series',
    page_icon='📊'
)
st.sidebar.success("Выберете интересующий раздел")
st.header('Анализ временного ряда')
data_file = st.file_uploader(label='')
if data_file is not None:
    try:
        # Пытаемся загрузить файл как CSV
        data = pd.read_csv(data_file)
        st.success("Файл успешно загружен!")

    except Exception as e:
        st.error("Ошибка при загрузке файла: убедитесь, что файл имеет формат .csv")
else:
    st.warning("Пожалуйста, загрузите CSV файл для анализа.")