from airflow import DAG
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator # <--- NEW IMPORT
from datetime import datetime, timedelta
import os

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'dynamic_pricing_pipeline',
    default_args=default_args,
    description='Daily ingestion of competitor prices',
    schedule_interval='@daily',
    catchup=False
)

# Task 1: The Heavy Lifter (Spark)
# Crunching the numbers so you don't have to.
ingest_prices = DockerOperator(
    task_id='ingest_competitor_prices',
    image='my-project/spark-custom:latest',
    container_name='spark-job-runner',
    api_version='auto',
    auto_remove=True,
    command='/opt/spark/bin/spark-submit --packages org.apache.hadoop:hadoop-aws:3.3.4 --master spark://spark-master:7077 /opt/spark/jobs/etl/ingest_competitor_prices.py',
    docker_url='unix://var/run/docker.sock',
    network_mode='revenueoptimizationengine_data-network',
    environment={
        'AWS_ACCESS_KEY_ID': os.getenv('AWS_ACCESS_KEY_ID'),
        'AWS_SECRET_ACCESS_KEY': os.getenv('AWS_SECRET_ACCESS_KEY'),
        'S3_BUCKET_NAME': os.getenv('S3_BUCKET_NAME'),
        'SCRAPINGDOG_API_KEY': os.getenv('SCRAPINGDOG_API_KEY')
    },
    dag=dag,
)

# Task 2: The Warehouse Delivery (Snowflake)
# Yeeting the data into the cloud warehouse. Look ma, no SQL client needed!
load_to_snowflake = SnowflakeOperator(
    task_id='load_to_snowflake',
    snowflake_conn_id='snowflake_conn',
    sql="""
        COPY INTO DYNAMIC_PRICING.RAW.competitor_prices (asin, price, currency, scraped_at)
        FROM (
            SELECT $1:asin, $1:price, $1:currency, $1:scraped_at 
            FROM @DYNAMIC_PRICING.RAW.competitors_pricing_stage
        )
        FILE_FORMAT = (TYPE = 'PARQUET')
        ON_ERROR = 'CONTINUE';
    """,
    dag=dag,
)

# The Circle of Life: Spark does the work, THEN Snowflake taketh the data.
ingest_prices >> load_to_snowflake