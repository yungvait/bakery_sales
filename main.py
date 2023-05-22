import pandas as pd
import streamlit as st
import datetime
import matplotlib.pyplot as plt
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import calendar

with open('bootstrap.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def run_app():
    # Загрузка данных с указанием кодировки
    data = pd.read_csv('Bakery_sales.csv', delimiter=';', encoding='Windows-1251')

    # Преобразование столбца 'date' в тип datetime
    data['date'] = pd.to_datetime(data['date'], format='%d.%m.%Y')

    # Определение минимальной и максимальной даты
    min_date = data['date'].min().date()
    max_date = data['date'].max().date()

    # Боковая панель с фильтрами
    st.sidebar.subheader('Фильтры')

    # Фильтр диапазона дат
    start_date = st.sidebar.date_input('Выберите начальную дату', value=min_date, min_value=min_date, max_value=max_date)
    end_date = st.sidebar.date_input('Выберите конечную дату', value=max_date, min_value=min_date, max_value=max_date)

    # Преобразование столбца 'time' в тип datetime
    data['time'] = pd.to_datetime(data['time'], format='%H:%M')

    # Проверка, совпадают ли начальная и конечная даты
    same_date = start_date == end_date
    
    if same_date:
        # Фильтр диапазона времени только при совпадающих датах
        start_time = st.sidebar.time_input('Выберите начальное время', value=datetime.time(0, 0))
        end_time = st.sidebar.time_input('Выберите конечное время', value=datetime.time(23, 59))

        # Преобразование времени в формат строки
        start_time_str = start_time.strftime('%H:%M')
        end_time_str = end_time.strftime('%H:%M')

        # Фильтрация данных по дате и времени
        filtered_data = data[(data['date'] == pd.to_datetime(start_date)) &
                             (data['time'].dt.strftime('%H:%M') >= start_time_str) &
                             (data['time'].dt.strftime('%H:%M') <= end_time_str)]
    else:
        # Фильтрация данных только по дате
        filtered_data = data[(data['date'] >= pd.to_datetime(start_date)) & (data['date'] <= pd.to_datetime(end_date))]

    # Удаление времени из столбца 'date'
    filtered_data['date'] = filtered_data['date'].dt.date

    # Удаление даты из столбца 'time'
    filtered_data['time'] = filtered_data['time'].dt.time

    with st.container():
        st.markdown('---')
        st.title('Анализ данных')
        st.markdown('---')
        # Показать только первые 10 строк отфильтрованных данных
        with st.expander("Посмотреть первые 10 строк"):
            st.subheader('Отфильтрованные данные')
            st.dataframe(filtered_data.head(10), use_container_width=True)
        # Отобразить остальные строки с прокруткой
        with st.expander("Посмотреть все отфильтрованные строки"):
            st.dataframe(filtered_data, use_container_width=True)
        with st.expander('Сводная таблица "Сумма продаж по артикулу"'):
        
            st.write("pivot_table")

            

        # Топ-10 продаж за выбранный период
        top_sales = filtered_data.groupby('article')['Quantity'].sum().nlargest(10).reset_index()

        # Преобразование столбца 'total_price' в числовой тип данных
        filtered_data['total_price'] = filtered_data['total_price'].str.replace(',', '.').astype(float)

        # Топ-10 продуктов по сумме продаж за выбранный период
        top_products = filtered_data.groupby('article')['total_price'].sum().nlargest(10).reset_index()







        # Показать только первые 10 строк топ-10 продаж
        st.write("10 самых часто продаваемых продуктов")
        st.dataframe(top_sales, use_container_width=True)



    colgr1, colgr2 = st.columns(2)
    # Конвертация столбца 'total_price' в числовой тип данных
    data['total_price'] = pd.to_numeric(data['total_price'], errors='coerce')

    with colgr1:
        # Выбор года с помощью виджета
        selected_year11 = st.selectbox('Выберите год', data['date'].dt.year.unique())

        # Фильтрация данных по выбранному году
        filtered_data11 = data[data['date'].dt.year == selected_year11]
        # Группировка данных по месяцу и суммирование выручки
        revenue_by_month11 = filtered_data11.groupby(filtered_data11['date'].dt.month)['total_price'].sum().reset_index()

        # Преобразование числовых значений месяцев в названия
        revenue_by_month11['date'] = revenue_by_month11['date'].apply(lambda x: calendar.month_name[x])

    with colgr2:

        # Выбор типа графика с помощью селектбокса
        chart_type = st.selectbox('Выберите тип графика', ['Гистограмма', 'Круговая диаграмма'])

    with st.container():
        if chart_type == 'Гистограмма':
            # Создание графика выручки по месяцам
            fig = go.Figure(data=[go.Bar(x=revenue_by_month11['date'], y=revenue_by_month11['total_price'])])
            fig.update_layout(
                title=f'Выручка по месяцам ({selected_year11})',
                xaxis_title='Месяц',
                yaxis_title='Выручка'
            )
            fig.update_layout()
            st.plotly_chart(fig, use_container_width=True)

        elif chart_type == 'Круговая диаграмма':
            # Создание круговой диаграммы выручки по месяцам
            fig = go.Figure(data=[go.Pie(labels=revenue_by_month11['date'], values=revenue_by_month11['total_price'])])
            fig.update_layout(
                title=f'Круговая диаграмма выручки по месяцам ({selected_year11})'
            )
            fig.update_layout()
            st.plotly_chart(fig, use_container_width=True)


    
    # Показать только первые 10 строк 10 самых часто продаваемых продуктов
    st.write("Топ-10 продуктов по сумме продаж")
    st.dataframe(top_products, use_container_width=True)




   
    # Данные для графика "10 самых часто продаваемых продуктов"
    top_sales_data = top_sales.set_index('article')['Quantity']

    # Создание графика
    fig1 = go.Figure(data=[go.Pie(labels=top_sales_data.index, values=top_sales_data)])

    # Настройка макета и заголовка
    fig1.update_layout(title='10 самых часто продаваемых продуктов')

    # Отображение графика в Streamlit
    st.plotly_chart(fig1, use_container_width=True)


    if same_date:
        # Фильтрация данных по выбранному дню
        filtered_data_single_day = filtered_data[filtered_data['date'] == start_date]

        if not filtered_data_single_day.empty:
            # Группировка данных по времени и суммирование продаж
            sales_by_time = filtered_data_single_day.groupby('time')['Quantity'].sum()

            # Преобразование времени в формат строки для правильного отображения на графике
            sales_by_time_numeric = pd.DataFrame({'time': sales_by_time.index, 'sales': sales_by_time.values})
            sales_by_time_numeric['time'] = sales_by_time_numeric['time'].apply(lambda x: x.strftime('%H:%M'))

            # Создание графика почасовой динамики продаж с датой и днем недели
            fig_hourly = go.Figure()
            fig_hourly.add_trace(go.Scatter(
                x=sales_by_time_numeric['time'],
                y=sales_by_time_numeric['sales'],
                mode='lines',
                name=start_date.strftime('%A (%d.%m.%Y)'),
                hovertext=[f'{start_date.strftime("%A (%d.%m.%Y)")} {time}' for time in sales_by_time_numeric['time']],
                hovertemplate='<b>%{hovertext}</b><br>Продажи: %{y}'
            ))
            fig_hourly.update_layout(
                title='Почасовая динамика продаж (в пределах одного дня)',
                xaxis_title='Время',
                yaxis_title='Количество продаж',
                xaxis_tickformat='%H:%M'
            )
            st.plotly_chart(fig_hourly, use_container_width=True)
        else:
            st.write('Нет данных для выбранного дня.')
    else:
        # Группировка данных по дате и суммирование продаж
        sales_by_date = filtered_data.groupby('date')['Quantity'].sum()
        # Создание графика динамики продаж с датой и днем недели
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=sales_by_date.index,
            y=sales_by_date.values,
            mode='lines',
            name='Динамика продаж',
            hovertext=[f'{date.strftime("%A (%d.%m.%Y)")}' for date in sales_by_date.index],
            hovertemplate='<b>%{hovertext}</b><br>Продажи: %{y}'
        ))
        fig.update_layout(
            title='Динамика продаж',
            xaxis_title='Дата',
            yaxis_title='Количество продаж'
        )
        st.plotly_chart(fig, use_container_width=True)

















        
  

    # Данные для графика "Топ-10 продуктов по сумме продаж"
    top_products_data = top_products.set_index('article')['total_price']

    # Создание круговой диаграммы
    fig2 = go.Figure(data=[go.Pie(labels=top_products_data.index, values=top_products_data)])

    # Настройка макета и заголовка
    fig2.update_layout(title='Топ-10 продуктов по сумме продаж')

    # Отображение графика в Streamlit
    st.plotly_chart(fig2, use_container_width=True)



    if same_date:
        # Фильтрация данных по выбранному дню
        filtered_data_single_day = filtered_data[filtered_data['date'] == start_date]

        if not filtered_data_single_day.empty:
            # Группировка данных по времени и суммирование продаж
            sales_by_time = filtered_data_single_day.groupby('time')['total_price'].sum()

            # Удаление нулевых значений
            sales_by_time = sales_by_time[sales_by_time > 0]

            if not sales_by_time.empty:
                # Преобразование времени в формат строки для правильного отображения на графике
                sales_by_time_numeric = pd.DataFrame({'time': sales_by_time.index, 'sales': sales_by_time.values})
                sales_by_time_numeric['time'] = sales_by_time_numeric['time'].apply(lambda x: x.strftime('%H:%M'))

                # Создание графика почасовой динамики продаж по сумме продаж с датой и днем недели
                fig_hourly_sales = go.Figure()
                fig_hourly_sales.add_trace(go.Scatter(
                    x=sales_by_time_numeric['time'],
                    y=sales_by_time_numeric['sales'],
                    mode='lines',
                    name=start_date.strftime('%A (%d.%m.%Y)'),
                    hovertext=[f'{start_date.strftime("%A (%d.%m.%Y)")} {time}' for time in sales_by_time_numeric['time']],
                    hovertemplate='<b>%{hovertext}</b><br>Сумма продаж: %{y}'
                ))
                fig_hourly_sales.update_layout(
                    title='Почасовая динамика продаж по сумме продаж (в пределах одного дня)',
                    xaxis_title='Время',
                    yaxis_title='Сумма продаж',
                    xaxis_tickformat='%H:%M'
                )
                st.plotly_chart(fig_hourly_sales, use_container_width=True)
            else:
                st.write('Нет данных для выбранного дня.')
        else:
            st.write('Нет данных для выбранного дня.')
    else:
        # Фильтрация данных по выбранному временному диапазону
        filtered_data_range = filtered_data[(filtered_data['date'] >= start_date) & (filtered_data['date'] <= end_date)]

        if not filtered_data_range.empty:
            # Группировка данных по дате и суммирование продаж
            sales_by_date = filtered_data_range.groupby('date')['total_price'].sum()

            # Удаление нулевых значений
            sales_by_date = sales_by_date[sales_by_date > 0]

            if not sales_by_date.empty:
                # Создание графика динамики продаж по сумме продаж с датой и днем недели
                fig_sales = go.Figure()
                fig_sales.add_trace(go.Scatter(
                    x=[date.strftime('%d.%m.%Y') for date in sales_by_date.index],
                    y=sales_by_date.values,
                    mode='lines',
                    name='Динамика продаж по сумме',
                    hovertext=[date.strftime("%A (%d.%m.%Y)") for date in sales_by_date.index],
                    hovertemplate='<b>%{hovertext}</b><br>Сумма продаж: %{y:.2f}'
                ))
                fig_sales.update_layout(
                    title='Динамика продаж по сумме',
                    xaxis_title='Дата',
                    yaxis_title='Сумма продаж'
                )
                st.plotly_chart(fig_sales, use_container_width=True)
            else:
                st.write('Нет данных для отображения динамики продаж по сумме.')
        else:
            st.write('Нет данных для выбранного временного диапазона.')
                                        

           

































   
    # Определение минимальной и максимальной даты
    min_date_chart = data['date'].min().date()
    max_date_chart = data['date'].max().date()

    

   
    with st.container():
        col3, col4 = st.columns(2)
        with col3:
            # Фильтр даты
            start_date_chart = st.date_input('Выберите начальную дату', min_value=min_date_chart, max_value=max_date_chart, key='start_date', value=min_date_chart)
        with col4:
            end_date_chart = st.date_input('Выберите конечную дату', min_value=min_date_chart, max_value=max_date_chart, key='end_date', value=max_date_chart)



        # Фильтрация данных только по дате
        filtered_data_chart = data[(data['date'] >= pd.to_datetime(start_date_chart)) & (data['date'] <= pd.to_datetime(end_date_chart))]

        # Удаление времени из столбца 'date'
        filtered_data_chart['date'] = filtered_data_chart['date'].dt.date

        # Удаление даты из столбца 'time'
        filtered_data_chart['time'] = filtered_data_chart['time'].dt.time

        
        # Фильтр продуктов
        selected_products_chart = st.multiselect('Выберите продукты', filtered_data_chart['article'].unique())

        if selected_products_chart and start_date_chart and end_date_chart:
            # Фильтрация данных по выбранным продуктам и дате
            filtered_data_selected_products = filtered_data_chart[
                (filtered_data_chart['article'].isin(selected_products_chart)) &
                (filtered_data_chart['date'] >= start_date_chart) & (filtered_data_chart['date'] <= end_date_chart)
            ]

            if not filtered_data_selected_products.empty:
                # Группировка данных по продукту, дате и суммирование продаж
                sales_by_product_date = filtered_data_selected_products.groupby(['article', 'date'])['Quantity'].sum().reset_index()

                # Создание графика динамики продаж по каждому продукту
                fig_sales_by_product = go.Figure()

                for product in selected_products_chart:
                    data_product = sales_by_product_date[sales_by_product_date['article'] == product]
                    fig_sales_by_product.add_trace(go.Scatter(
                        x=data_product['date'],
                        y=data_product['Quantity'],
                        mode='lines',
                        name=product,
                        hovertext=[f'{date.strftime("%A (%d.%m.%Y)")}: {quantity}' for date, quantity in
                                zip(data_product['date'], data_product['Quantity'])],
                        hovertemplate='<b>%{hovertext}</b><br>Продажи: %{y}'
                    ))

                fig_sales_by_product.update_layout(
                    title='Динамика продаж по продуктам',
                    xaxis_title='Дата',
                    yaxis_title='Количество продаж',
                    legend=dict(orientation='h', yanchor='top', xanchor='left', x=0, y=1.2)
                )

                # Установка размера графика
                fig_sales_by_product.update_layout(height=400, width=600)  #height=600, width=1000

                st.plotly_chart(fig_sales_by_product, use_container_width=True)
   
    # Данные для графика "10 самых часто продаваемых продуктов"
    top_sales_data = top_sales.set_index('article')['Quantity']

    # Создание графика
    fig1 = go.Figure(data=[go.Pie(labels=top_sales_data.index, values=top_sales_data)])

    # Настройка макета и заголовка
    fig1.update_layout(title='10 самых часто продаваемых продуктов')

    # Отображение графика в Streamlit
    st.plotly_chart(fig1, use_container_width=True)
    
   
    # Данные для графика "10 самых часто продаваемых продуктов"
    top_sales_data = top_sales.set_index('article')['Quantity']

    # Создание графика
    fig1 = go.Figure(data=[go.Pie(labels=top_sales_data.index, values=top_sales_data)])

    # Настройка макета и заголовка
    fig1.update_layout(title='10 самых часто продаваемых продуктов')

    # Отображение графика в Streamlit
    st.plotly_chart(fig1, use_container_width=True)















if __name__ == '__main__':
    # Запуск приложения

    st.sidebar.title('Настройки')
    run_app()