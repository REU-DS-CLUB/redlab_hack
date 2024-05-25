import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from datetime import datetime


st.set_page_config(
    page_title='analysis_time_series',
    page_icon='📊'
)
st.sidebar.success("Выберете интересующий раздел")


# типо у меня есть эти константы откуда-нибудь
START_DATE = datetime(year=2024, month=1, day=1)
END_DATE = datetime(year=2024, month=1, day=31)
if "len" not in st.session_state:
    st.session_state.len = 10
if "start_date" not in st.session_state:
    st.session_state.start_date = START_DATE
if "end_date" not in st.session_state:
    st.session_state.end_date = END_DATE
if "is_recreate" not in st.session_state:
    st.session_state.is_recreate = False

st.markdown("""<h1 style = 'text-align: center'> Анализ временного ряда</h1>""", unsafe_allow_html=True)
grath13, grath24 = st.columns(2)
with grath13:
    x = np.linspace(0,int(st.session_state.len),100)
    fig = plt.figure()
    plt.plot(x, np.sin(x))
    st.write(fig)
    
    x = np.linspace(0,int(st.session_state.len),100)
    fig = plt.figure()
    plt.plot(x, np.sin(x))
    st.write(fig)
    
with grath24:
    x = np.linspace(0,int(st.session_state.len),100)
    fig = plt.figure()
    plt.plot(x, np.sin(x))
    st.write(fig)
    
    x = np.linspace(0,int(st.session_state.len),100)
    fig = plt.figure()
    plt.plot(x, np.sin(x))
    st.write(fig)

st.write("Настройки")
col1, col2 = st.columns(2)
col1.date_input("Выберите дату старта", min_value=START_DATE, max_value=END_DATE, key="start_date")
col1.text_input("Длина", key="len")
col2.date_input("Выберите дату конца", min_value=st.session_state.start_date, max_value=END_DATE, key="end_date")
col2.checkbox("Пересчитывать аномалии?", key="is_recreate")







data_file = st.file_uploader(label='Вы можете загрузить свой собственный файл с данными!',accept_multiple_files=False,type="tsv")
if data_file is not None:
    try:
        # Пытаемся загрузить файл как TSV
        data = pd.read_tsv(data_file)
        st.success("Файл успешно загружен!")
    except Exception as e:
        st.error("Ошибка при загрузке файла: убедитесь, что файл имеет формат .tsv")
    
