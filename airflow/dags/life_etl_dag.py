import pendulum
from airflow.decorators import dag, task
from airflow.hooks.mysql_hook import MySqlHook
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator
from sqlalchemy import create_engine
from life.life_etl import ETLProcessor

@dag(
    schedule_interval=None,
    start_date=pendulum.datetime(2025, 1, 1, tz="UTC"),
    catchup=False,
    tags=["life_etl"],
)
def life_etl_dag():
    life_schema = SQLExecuteQueryOperator(
        task_id="life-schema",
        sql="life/life-schema.sql",
        conn_id="mysql_sys",
    )
    
    @task()
    def run_etl():
        hook = MySqlHook(mysql_conn_id="mysql_life")
        cnx = hook.get_conn()
        engine = create_engine(hook.get_uri(), creator=lambda: cnx)
        qol_path = "/opt/airflow/data/quality_of_life.csv"
        whr_path = "/opt/airflow/data/world-happiness-2022.xls"
        regions_path = "/opt/airflow/data/country_regions.csv"
        processor = ETLProcessor(qol_path, whr_path, regions_path, engine)
        processor.process()
        engine.dispose()
    
    life_schema >> run_etl()

life_etl_dag()