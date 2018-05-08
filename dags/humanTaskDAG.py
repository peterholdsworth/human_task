
import airflow
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from datetime import timedelta
from airflow.operators import HumanTaskOperator


# these args will get passed on to each operator
# you can override them on a per-task basis during operator initialization
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(2),
    'email': ['airflow@airflow.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    # 'queue': 'bash_queue',
    # 'pool': 'backfill',
    # 'priority_weight': 10,
    # 'end_date': datetime(2016, 1, 1),
    # 'wait_for_downstream': False,
    # 'dag': dag,
    # 'adhoc':False,
    # 'sla': timedelta(hours=2),
    # 'execution_timeout': timedelta(seconds=300),
    # 'on_failure_callback': some_function,
    # 'on_success_callback': some_other_function,
    # 'on_retry_callback': another_function,
    # 'trigger_rule': u'all_success'
}

dag = DAG(
    'publish',
    default_args=default_args,
    description='A simple human task DAG',
    schedule_interval=None)


t1 = DummyOperator(task_id='publish_to_staging', dag=dag)
t2 = HumanTaskOperator(task_id='approve', dag=dag)
t3 = DummyOperator(task_id='publish_to_production', dag=dag)

t1 >> t2 >> t3
