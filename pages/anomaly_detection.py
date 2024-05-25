import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from datetime import date, datetime


st.set_page_config(
    page_title='analysis_time_series',
    page_icon='📊'
)
st.sidebar.success("Выберете интересующий раздел")

@st.cache_data() # suppress_st_warning=True
def grath(ts_df, metric: str):
    # Создаем данные временного ряда
    
    dates = ts_df['time'].head(1000)
    values = ts_df[metric].head(1000)

    # Вычисляем квантили
    q25 = np.percentile(values, 25)
    median = np.percentile(values, 50)
    q75 = np.percentile(values, 75)

    # Построение графиков
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6), gridspec_kw={'width_ratios': [3, 1]})

    # График временного ряда
    ax1.plot(dates, values, label='Временной ряд')
    ax1.axhline(median, color='black', linestyle='-', label='Медиана')
    ax1.axhline(q25, color='green', linestyle='-', label='0.25 квантиль')
    ax1.axhline(q75, color='orange', linestyle='-', label='0.75 квантиль')
    ax1.legend()
    ax1.set_title('Временной ряд с линиями квантилей')
    ax1.set_xlabel('Дата')
    ax1.set_ylabel('Значение')

    # Гистограмма распределения значений временного ряда (горизонтальная)
    ax2.hist(values, bins=10, orientation='horizontal', color='blue', alpha=0.7)
    ax2.axhline(median, color='black', linestyle='-', label='Медиана')
    ax2.axhline(q25, color='green', linestyle='-', label='1 квартиль')
    ax2.axhline(q75, color='orange', linestyle='-', label='3 квартиль')
    ax2.set_title('Распределение значений временного ряда')
    ax2.set_xlabel('Частота')
    ax2.set_ylabel('Значение')
    ax2.legend()

    # Устанавливаем одинаковые пределы оси y для обоих графиков
    ax1.set_ylim(min(values), max(values))
    ax2.set_ylim(min(values), max(values))

    plt.tight_layout()
    plt.style.use('https://github.com/dhaitz/matplotlib-stylesheets/raw/master/pitayasmoothie-light.mplstyle')
    plt.show()
    st.write(fig)

def init_state(state:str, default):
    if state not in st.session_state:
        st.session_state[state] = default

def save(end_date,is_recreate, grath1_vis,grath2_vis,grath3_vis,grath4_vis,slider_val):
    st.session_state["grath1_vis"] = grath1_vis
    st.session_state["grath2_vis"] = grath2_vis
    st.session_state["grath3_vis"] = grath3_vis
    st.session_state["grath4_vis"] = grath4_vis
    #st.session_state["start_date"] = start_date
    st.session_state["end_date"] = end_date
    st.session_state["is_recreate"] = is_recreate
    st.session_state["slider_val"] = (st.session_state["start_date"], end_date)
    
# типо у меня есть эти константы откуда-нибудь
START_DATE = datetime(year=2024, month=1, day=1,hour=5, minute=10)
END_DATE = datetime(year=2024, month=1, day=31,hour=11, minute=30)

init_state("start_date", START_DATE)
init_state("end_date", END_DATE)
init_state("is_recreate", False)
init_state("grath1_vis", True)
init_state("grath2_vis", True)
init_state("grath3_vis", True)
init_state("grath4_vis", True)
init_state("slider_val", (START_DATE.date(),END_DATE.date()))


st.markdown("""<h1 style = 'text-align: center'> Анализ временного ряда</h1>""", unsafe_allow_html=True)
data = pd.read_csv('data.csv')

if st.session_state["grath1_vis"]:
    grath(data, "throughput")
if st.session_state["grath2_vis"]:
    grath(data, "apdex")
if st.session_state["grath3_vis"]:     
    grath(data, "throughput")
if st.session_state["grath4_vis"]:   
    grath(data, "apdex")

slider_val = st.slider("TEST",START_DATE.date(), END_DATE.date(), value=st.session_state["slider_val"])

st.write("Настройки")
col1, col2 = st.columns(2)
col1.date_input("Выберите дату старта", min_value=START_DATE, max_value=END_DATE,key="start_date") #key="start_date"
end_date = col2.date_input("Выберите дату конца", min_value=st.session_state.start_date, max_value=END_DATE) #, key="end_date"
is_recreate = col2.checkbox("Пересчитывать аномалии в диапазоне?") #, key="is_recreate"
st.write("Фильтрация")
col1, col2 = st.columns(2)
grath1_vis = col1.checkbox("Метрика 1", value=st.session_state["grath1_vis"]) # , key="grath1_vis"
grath2_vis = col1.checkbox("Метрика 2", value=st.session_state["grath2_vis"]) # , key="grath2_vis"
grath3_vis = col2.checkbox("Метрика 3", value=st.session_state["grath3_vis"]) # , key="grath3_vis"
grath4_vis = col2.checkbox("Метрика 4", value=st.session_state["grath4_vis"]) # , key="grath4_vis"

st.button("Принять", on_click=save, args=(end_date,is_recreate, grath1_vis,grath2_vis,grath3_vis,grath4_vis,slider_val,))







data_file = st.file_uploader(label='Вы можете загрузить свой собственный файл с данными!',accept_multiple_files=False,type="tsv")
if data_file is not None:
    try:
        # Пытаемся загрузить файл как TSV
        data = pd.read_tsv(data_file)
        st.success("Файл успешно загружен!")
    except Exception as e:
        st.error("Ошибка при загрузке файла: убедитесь, что файл имеет формат .tsv")
    
