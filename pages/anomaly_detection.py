import streamlit as st
import pandas as pd
from datetime import datetime
st.set_page_config(
    page_title='analysis_time_series',
    page_icon='📊'
)
st.sidebar.success("Выберете интересующий раздел")

# типо у меня есть эти константы откуда-нибудь
START_DATE = datetime(year=2024, month=1, day=1)
END_DATE = datetime(year=2024, month=1, day=31)

st.header('Анализ временного ряда')
data_file = st.file_uploader(label='',accept_multiple_files=False,type="tsv")
if data_file is not None:
    try:
        # Пытаемся загрузить файл как TSV
        data = pd.read_tsv(data_file)
        st.success("Файл успешно загружен!")
    except Exception as e:
        st.error("Ошибка при загрузке файла: убедитесь, что файл имеет формат .tsv")
    
    st.write("Место для графика")
    st.write("Настройки")
    start, end, recreate = st.columns(3)
    start.date_input("Дата старта", min_value=START_DATE, max_value=END_DATE)
    end.date_input("Дата старта", min_value=START_DATE, max_value=END_DATE)
    recreate.checkbox("Пересчет аномалий в промежутке?")
    

else:
    st.warning("Пожалуйста, загрузите TSV файл для анализа.")