from contextlib import ExitStack
from pickletools import read_stringnl_noescape
from typing import Dict
import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from datetime import date, datetime, time, timedelta
from host.request import get_marc, get_new_anomalies


st.set_page_config(
    page_title='analysis_time_series',
    page_icon='📊'
)
st.sidebar.success("Выберете интересующий раздел")

@st.cache_data() # suppress_st_warning=True
def write(data: Dict[str, pd.DataFrame], feature_name : str):
    
    df = (data[feature_name]).astype(float)

    fig = plt.figure(figsize=(20, 8))

    plt.plot(data['time'], df, color='blue', label=f'Значения показателя {feature_name}')
    ind = feature_name+'_labels'
    anomalies = data[data[ind] == 1]
    #print((anomalies['time'].replace("T", " ")).iloc[-1,0])
    # anomalies.loc[:, "time"] = pd.to_datetime((anomalies['time']).str.replace("T", " "))
    
    plt.scatter(anomalies['time'], anomalies[feature_name], color='red', s=100, label='Аномалия')
    plt.title(f'Временной ряд с аномалиями показателя {feature_name}')
    plt.xlabel('Временной ряд')
    plt.ylabel(f'{feature_name}')
    plt.legend()
    plt.grid(True)

    st.write(fig)


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
    st.write(fig)

def init_state(state:str, default):
    if state not in st.session_state:
        st.session_state[state] = default

def save(end_date,is_recreate, selected_hour1, selected_hour2, selected_minute1, selected_minute2, grath1_vis,grath2_vis,grath3_vis,grath4_vis,slider_val):
    st.session_state["grath1_vis"] = grath1_vis
    st.session_state["grath2_vis"] = grath2_vis
    st.session_state["grath3_vis"] = grath3_vis
    st.session_state["grath4_vis"] = grath4_vis
    
    tm1 = time(selected_hour1, selected_minute1,0)
    tm2 = time(selected_hour2, selected_minute2,0)
    st.session_state["end_date"] = end_date
    st.session_state["start_date"] = datetime.combine(st.session_state["start_date"], tm1)
    st.session_state["end_date"] = datetime.combine(st.session_state["end_date"], tm2)
    st.session_state["is_recreate"] = is_recreate
    st.session_state["slider_val"] = (st.session_state["start_date"].date(), st.session_state["end_date"].date())
    print(st.session_state["end_date"])
    print(st.session_state["start_date"])
    
    if (st.session_state["is_recreate"]):
        pass
        # http запрос с пересчетом
    else:
        pass
        # http запрос без пересчета
    
    
@st.cache_data()
def download(data_file):
    return pd.read_tsv(data_file)

def request():
    try:
        #response = get_marc('2024-04-01 20:36:00', '2024-04-30 23:36:00')
        response = get_new_anomalies('2024-04-01 20:36:00', '2024-04-30 23:36:00')
        json_text = response.json()
        json_text = pd.DataFrame(json_text)
        print("="*1000)
        print( json_text )
        write(json_text, "apdex")
        # grath(json_text, "apdex")
    except (...):
        print("SOME ERROR IN REQUEST")
    

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
init_state("is_expanded", False)
init_state("slider_val", (START_DATE.date(),END_DATE.date()))
init_state("data", pd.read_csv('data.csv'))


st.markdown("""<h1 style = 'text-align: center'> Анализ временного ряда</h1>""", unsafe_allow_html=True)

data = st.session_state["data"]
if st.session_state["grath1_vis"]:
    grath(data, "throughput")
if st.session_state["grath2_vis"]:
    grath(data, "apdex")
if st.session_state["grath3_vis"]:     
    grath(data, "throughput")
if st.session_state["grath4_vis"]:   
    grath(data, "apdex")

slider_val = st.slider("Неточный диапазон",START_DATE.date(), END_DATE.date(), value=st.session_state["slider_val"], key="slider_val", label_visibility="visible")



exp = st.expander("Точный диапазон", expanded=st.session_state["is_expanded"])
col1, col2 = exp.columns(2)
with col1:
    st.date_input("Выберите дату старта", min_value=START_DATE, max_value=END_DATE, value=st.session_state["slider_val"][0],key="start_date") #key="start_date"
    selected_hour1 = st.number_input("Час", min_value=0, max_value=23, key="qwe")
    selected_minute1 = st.number_input("Минута", min_value=0, max_value=59, key="wer")
with col2:
    end_date = st.date_input("Выберите дату конца", min_value=st.session_state.start_date + timedelta(days=1), max_value=END_DATE, value=st.session_state["slider_val"][1]) #, key="end_date"
    selected_hour2 = st.number_input("Час", min_value=0, max_value=23)
    selected_minute2 = st.number_input("Минута", min_value=0, max_value=59)
    
is_recreate = st.checkbox("Пересчитывать аномалии в диапазоне?") #, key="is_recreate"
st.write("Фильтрация")
col1, col2 = st.columns(2)
grath1_vis = col1.checkbox("Метрика 1", value=st.session_state["grath1_vis"]) # , key="grath1_vis"
grath2_vis = col1.checkbox("Метрика 2", value=st.session_state["grath2_vis"]) # , key="grath2_vis"
grath3_vis = col2.checkbox("Метрика 3", value=st.session_state["grath3_vis"]) # , key="grath3_vis"
grath4_vis = col2.checkbox("Метрика 4", value=st.session_state["grath4_vis"]) # , key="grath4_vis"

st.button("Принять", on_click=save, args=(end_date,is_recreate,selected_hour1,selected_hour2,selected_minute1,selected_minute2,  grath1_vis,grath2_vis,grath3_vis,grath4_vis,slider_val,))

st.button("REQUEST", on_click=request)





data_file = st.file_uploader(label='Вы можете загрузить свой собственный файл с данными!',accept_multiple_files=False,type="tsv")
if data_file is not None:
    try:
        # Пытаемся загрузить файл как TSV
        data = download(data_file)
        
        # типо http запрос на загрузку файла на сервер и получение start_date, end_date
        # типо http запрос на получение датафрейма для графиков

        st.success("Файл успешно загружен!")
    except Exception as e:
        st.error("Ошибка при загрузке файла: убедитесь, что файл имеет формат .tsv")
    
