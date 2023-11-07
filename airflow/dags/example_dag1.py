# Описание дага
'''
Это простейший даг
Он состоит из:
баш оператора (выводит текущую дату)
двух питон-операторов (выводят по строке в логи)
'''
# импорты
from airflow import DAG # импортируем фукнцию DAG из пакета airflow
from datetime import datetime, timedelta

# импорты операторов
from airflow.operators.bash import BashOperator
from airflow.operators.python_operator import PythonOperator

# переменные по умолчанию (наследуются всеми таксами в даге)
DEFAULT_ARGS = {
    'owner':'ELarin',
    'depends_on_past':False, # запустится ли скрипт, если прошлое выполнение было неудачным
    'start_date': datetime(2023, 9, 1), # даг начнёт выполняться начиная с этой даты,
    'catchup': False, # если False - все предыдущие запуски от start_date до сегодня будут пропущены
    'end_date': datetime(2023, 9, 3), # не будет выполняться после этой даты
    'retries': 1, # сколько раз даг после ошибки будет пытаться выполниться повторно
    'retry_delay': timedelta(minutes = 1) # через какое время будет запущен retry
}

dag =  DAG("example_dag1", # название дага
         schedule_interval = '@hourly', # интервал выполнения
         default_args=DEFAULT_ARGS,
         max_active_runs = 1,
         tags=['example_dag1'])
dag.doc_md = __doc__ # включить функцию документирования для дага

def hello():
    return print('Hello world!')

def sum_int():
    return print(2+2)

t1 = PythonOperator(
    task_id = 'helloworld_task', # название таска
    python_callable = hello, # действие для оператора
    dag = dag # ссылаемся на даг
)
t1.doc_md = 'Питон оператор. Пишет в лог Hello world!'

t2 = PythonOperator(
    task_id = 'calculate_task', # название таска2
    python_callable = sum_int, # действие для оператора
    dag = dag # ссылаемся на даг
)
t2.doc_md = 'Питон оператор. Пишет в лог сумму 2+2'

t3 = BashOperator(
    task_id = 'bash_task', # название таска3
    bash_command = 'echo {{ ds }}', # шаблон Jinja
    dag = dag # ссылаемся на даг
)
t3.doc_md = 'Баш оператор. Пишет в лог дату запуска дага'

t1 >> t2 >> t3