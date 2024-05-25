import streamlit as st
import base64

st.set_page_config(
    page_title="DS_club_main",
    page_icon="👋",
)
st.title('Добро пожаловать на сервис от команды [REU DS CLUB ](https://vk.com/reu_ds_club)!')
st.sidebar.success('Выберете интересующий раздел')
st.markdown('''С помощью алгоритмов машинного обучения и статистики вы можете 
легко провести анализ временного ряда, а также детекцию аномалий ''')

def make_participant_list():
    participants = {
        "Леша - Data scientist/Frontend dev": "https://t.me/gasboy04",
        "Саша - ML engineer": "https://t.me/lild1tz",
        "Пелагея - ML engineer": "https://t.me/polyanka003",
        "Артем - Backend/DevOps": "https://t.me/artemmichurin",
        "Максим - Data analyst/Frontend dev": "https://t.me/Maksoit"
    }
    # Формирование списка ссылок на основе участников
    participants_list = "\n".join([f"* [{name}]({profile_link})" for name, profile_link in participants.items()])
    return participants_list


# Вывод списка участников в виде ссылок
st.markdown(f"### Над нашим решением хакатона работали:\n{make_participant_list()}", unsafe_allow_html=True)
st.markdown('Подробно изучить наше решение вы можете [здесь](https://github.com/REU-DS-CLUB/redlab_hack)',
            unsafe_allow_html=True)
