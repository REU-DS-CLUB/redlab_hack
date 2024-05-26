from typing import Dict
import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots
from datetime import date, datetime, time, timedelta
from host.request import get_marc


st.set_page_config(
    page_title='analysis_time_series',
    page_icon='📊'
)
st.sidebar.success("Выберете интересующий раздел")

@st.cache_data() # suppress_st_warning=True
def write(data: Dict[str, pd.DataFrame], feature_name : str):
    
    df = data[feature_name]

    fig = plt.figure(figsize=(20, 8))

    plt.plot(df['time'], df['value'], color='blue', label=f'Значения показателя {feature_name}')
    anomalies = df[df['labels'] == 1]
    plt.scatter(anomalies['time'], anomalies['value'], color='red', s=100, label='Аномалия')
    plt.title(f'Временной ряд с аномалиями показателя {feature_name}')
    plt.xlabel('Временной ряд')
    plt.ylabel(f'{feature_name}')
    plt.legend()
    plt.grid(True)

    st.write(fig)


@st.cache_data()
def grath(ts_df, metric: str):
    # Создаем данные временного ряда
    dates = ts_df['time'].head(1000)
    values = ts_df[metric].head(1000)

    # Вычисляем квантили
    q25 = np.percentile(values, 25)
    median = np.percentile(values, 50)
    q75 = np.percentile(values, 75)

    # Создаем подграфики
    fig = make_subplots(rows=1, cols=2, column_widths=[0.9, 0.25], subplot_titles=('Временной ряд', 'Распределение значений'))



    fig.add_trace(go.Scatter(x=dates, y=values, mode='lines', name='Временной ряд'), row=1, col=1)
    fig.add_trace(go.Scatter(x=dates, y=[median]*len(dates), mode='lines', name='Медиана', line=dict(color='red', dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=dates, y=[q25]*len(dates), mode='lines', name='1 квартиль', line=dict(color='green', dash='dash')), row=1, col=1)
    fig.add_trace(go.Scatter(x=dates, y=[q75]*len(dates), mode='lines', name='3 квартиль', line=dict(color='orange', dash='dash')), row=1, col=1)

    # Гистограмма распределения значений временного ряда (горизонтальная)
    fig.add_trace(go.Histogram(y=values, nbinsy=10, orientation='h', marker_color='aqua', opacity=0.7, showlegend=False, name='Распределение'), row=1, col=2)
    fig.add_trace(go.Scatter(x=[0, 0], y=[min(values), max(values)], mode='lines', showlegend=False, line=dict(color='black', dash='dash')), row=1, col=2)
    fig.add_trace(go.Scatter(x=[0, 0], y=[q25, q25], mode='lines', showlegend=False, line=dict(color='green', dash='dash')), row=1, col=2)
    fig.add_trace(go.Scatter(x=[0, 0], y=[q75, q75], mode='lines', showlegend=False, line=dict(color='orange', dash='dash')), row=1, col=2)

    fig.update_layout(
        title='Временной ряд с распределением значений',
        width=1000,
        height=600,
        template='plotly_white',
        showlegend=True
    )

    # Настройки оформления
    fig.update_layout(title='Временной ряд с распределением значений', xaxis_title='Дата', yaxis_title='Значение', template='plotly_white')
    fig.update_xaxes(title_text='Частота', row=1, col=1)
    fig.update_yaxes(title_text='Значение', row=1, col=1)
    fig.update_yaxes(title_text='Значение', row=1, col=2)

    # Показать графики с помощью Streamlit
    st.plotly_chart(fig)

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
    response = get_marc('2024-10-01 20:36:00', '2024-10-30 23:36:00')
    json_text = response.json()
    json_text = pd.DataFrame(json_text)
    print( json_text )
    

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

slider_val = st.slider("TEST",START_DATE.date(), END_DATE.date(), value=st.session_state["slider_val"], key="slider_val")

st.write("Настройки")
col1, col2 = st.columns(2)
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
    
