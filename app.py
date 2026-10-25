import os
import pandas as pd
import streamlit as st
from urllib.parse import quote
import requests
from datetime import date

BACKUP_FILE="backup_schedule.xlsx"

st.set_page_config(page_title='Название',layout='wide')
st.title('Рассписание дополнительных занятий')

@st.cache_data(ttl=1800)
def load_data():
    UrL=st.secrets['YANDEX_URL']
    api=('https://cloud-api.yandex.net/v1/disk/public/resources/download?public_key='+ quote(UrL))

    try:
        response=requests.get(api,timeout=5)
        if response.status_code==200:
            data=response.json()
            down_url=data["href"]
            df=pd.read_excel(down_url)
            df.to_excel(BACKUP_FILE, index=False)
            return df
    except Exception as e:
        pass

    if os.path.exists(BACKUP_FILE):
        st.sidebar.warning("Нет связи с облаком. Загружена автономная копия расписания.")
        df=pd.read_excel(BACKUP_FILE)
        return df
    return None

today=date.today()
exam_oge=date(2027,6,2)
exam_ege=date(2027,6,1)

day_oge=(exam_oge-today).days
day_ege=(exam_ege-today).days
col_1,col_2=st.columns(2)
with col_1:
    st.metric(label='Дней до начала ОГЕ', value=f'{day_oge}')
with col_2:
    st.metric(label='Дней до начала ЕГЕ', value=f'{day_ege}')
st.markdown('---')

#print(response.status_code)
df=load_data()

if df is not None:
    #st.dataframe(df)
    required_columns=["Класс","Предмет","Учитель"]
    missing_cols=[col for col in required_columns if col not in df.columns]
    if missing_cols:
        st.error(f"Ошибка структуры данных: в Excel-файле не найдены обязательные"
                 f"колонки {missing_cols}. Проверьте заголовки в таблице!")
        st.stop()
        
    st.sidebar.header('Панель управления')
    if "Класс" in df.columns:
        classes=['Все классы']+list(df["Класс"].dropna().unique())
        select_cl=st.sidebar.selectbox("Выберите класс:", classes)

        if select_cl!="Все классы":
            df_filter=df[df["Класс"]==select_cl]
        else:
            df_filter=df.copy()
    else:
        df_display=df.copy()
    if "Учитель" in df.columns:
        teachers=['Все учителя']+list(df_filter["Учитель"].dropna().unique())
        select_teach=st.sidebar.selectbox("Выберите учителя:", teachers)

        if select_teach!="Все учителя":
            df_display=df_filter[df_filter["Учитель"]==select_teach]
        else:
            df_display=df_filter
    else:
        df_display=df_filter

    tab1,tab2,tab3=st.tabs(['Рассписание','Важная информация','Обратная связь'])

    with tab1:
       st.dataframe(df_display,use_container_width=True) 

    with tab2:
        st.subheader('Официальные банки заданий и ресурсы')
        col1,col2=st.columns(2)
        with col1:
            st.link_button('Банк ОГЕ (ФИПИ)','https://fipi.ru')
        with col2:
            st.link_button('Банк ЕГЕ ( ФИПИ)','https://fipi.ru')
        st.markdown('---')

        with st.expander('Важные даты и итоговые работы'):
            st.write('Итоговое собеседование (9 класс): Февраль 2027 г.')
            st.write('Итоговое сочинение (11 класс): Декабрь 2026 г.')
        with st.expander('что делать если возниклт вопросы или ошибки?'):
            st.write('Если не нашли свое рассписание или хотите уточнить:')
            st.write('Тут прописать завуча', 'кабинет:')

    with tab3:
        st.subheader("Обратная связь и развитие проекта")
        st.write("Помогите сделать рассписание и проект еще удобнее! Вы можете оставить свой отзыв."
                 "или предложить идею для добавления новых функций."
        )
        colus1,colus2=st.columns(2)
        with colus1:
            st.link_button("Написать в Telegram - канал","t.me/+SzWQWPo7yExhMmly")
        with colus2:
            st.link_button("Написать в MAX - канал","https://max.ru/join/8xRyuS1aUwLlpKEYtGZIZ4lUq5qSAXZDLR2CGMfVIH8")
else:
    st.error("Ненайдено на диске")
