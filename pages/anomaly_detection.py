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

def foo(input_):
    st.write(input_)
    if input_.isdigit():
        st.session_state.len = int(input_)
        st.write(str(st.session_state.len))
    else:
        st.error('Введите')

START_DATE = datetime(year=2024, month=1, day=1)
END_DATE = datetime(year=2024, month=1, day=31)
if "len" not in st.session_state:
    st.session_state.len = 10

st.header('Анализ временного ряда')


st.write("Место для графика")
x = np.linspace(0,int(st.session_state.len),100)
fig = plt.figure()
plt.plot(x, np.sin(x))
st.write(fig)


st.write("Настройки")
col1, col2 = st.columns(2)
col1.text_input("Длина", key="len")
# col2.button('Кнопка')
col2.text_input("Текст")




data_file = st.file_uploader(label='Вы можете загрузить свой собственный файл с данными!',accept_multiple_files=False,type="tsv")
if data_file is not None:
    try:
        # Пытаемся загрузить файл как TSV
        data = pd.read_tsv(data_file)
        st.success("Файл успешно загружен!")
    except Exception as e:
        st.error("Ошибка при загрузке файла: убедитесь, что файл имеет формат .tsv")
    
