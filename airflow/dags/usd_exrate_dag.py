# Описание дага
'''
Этот даг каждый день загружает курсы доллара к рублю и сохраняет в БД
Он состоит из:
1. питон оператора (pandas читает файл XML с ЦБРФ, немного преобразует, сохраняет в csv)
2. питон оператора (читает csv с помощью хука PostgresHook)
Администратор - Евгений Ларин
'''
# импорты
from airflow import DAG # импортируем фукнцию DAG из пакета airflow
from datetime import datetime, timedelta
import pandas as pd

# импорты операторов Airflow
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook

# переменные по умолчанию (наследуются всеми таксами в даге)
DEFAULT_ARGS = {
    'owner':'ELarin',
    'depends_on_past':False, # запустится ли скрипт, если прошлое выполнение было неудачным
    'start_date': datetime(2023, 6, 2), # даг начнёт выполняться начиная с ПРЕДЫДУЩЕЙ даты,
    'catchup': True, # если False - все предыдущие запуски от start_date до сегодня будут пропущены
    #'end_date': datetime(2023, 9, 3), # не будет выполняться после этой даты
    'retries': 2, # сколько раз даг после ошибки будет пытаться выполниться повторно
    'retry_delay': timedelta(minutes = 1) # через какое время будет запущен retry
}

# сохраняем из переменных JINJA дату выполнения дага для использования в коде Python
date = "{{ ds }}"

dag =  DAG("usd_exrate_dag", # название дага
         schedule_interval = '@daily', # интервал выполнения
         default_args=DEFAULT_ARGS,
         max_active_runs = 1, # сколько процессов дага будет выполняться одновременно
         tags=['usd_exrate_dag, usd']) # теги

# функция для чтения данных с сайта cbr.ru. Получает параметр date из op_kwargs (перменная JINJA)
def read_data(date):
    date = datetime.strptime(date, '%Y-%m-%d')
    link = f'https://www.cbr.ru/scripts/XML_daily.asp?date_req={date.strftime("%d/%m/%Y")}'
    df = pd.read_xml(link, encoding='windows-1251')
    df['Date'] = date - timedelta(days = 1)
    df = df[['Date', 'ID', 'NumCode', 'CharCode', 'Nominal', 'Name', 'Value']]
    usd = df[(df['CharCode'] == 'USD')]
    usd.to_csv(f'exrates.csv', index=False, sep = ';', header=False)

t1 = PythonOperator(
    task_id = 'read_data', # название таска
    python_callable = read_data, # действие для оператора
    op_kwargs = {'date': date}, # доп параметры для функции таска
    dag = dag
)

# функция с хуком к 'psql_conn' (connection настраивается в интерфейсе во вкладке admin) 
def export_psql():
    pg_hook = PostgresHook(postgres_conn_id='psql_conn')
    pg_hook.copy_expert("COPY rub_usd_exrate FROM STDIN DELIMITER ';'", 'exrates.csv')

t2 = PythonOperator(
    task_id = 'export_psql',
    python_callable = export_psql,
    dag = dag
)

t1 >> t2