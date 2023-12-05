import datetime
import os

import pandas as pd
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from dotenv import load_dotenv
from shapely.geometry import Polygon

from aiqst.scripts.api_utils import get_users, get_weather
from aiqst.scripts.generate_location import generate_points, map_users_coordinates

load_dotenv()

default_args = {
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=1),
}

def run_alembic_initial_migration():
    import subprocess
    subprocess.run(["alembic", "upgrade", "head"])

def get_sales(**kwargs):
    df = pd.read_csv('./data/sales_with_pos.csv')
    pos = pd.read_csv('./data/pos_db.csv')
    df_pos = pd.merge(df, pos, left_on= ['latitude', 'longitude'], right_on = ['latitude', 'longitude'])
    
    df_sales = pd.DataFrame()
    df_sales[['order_id', 'customer_id', 'product_id', 'pos_id', 'price', 'qty', 'order_date']] = \
    df_pos[['order_id', 'customer_id',  'product_id','id', 'price', 'quantity', 'order_date']].drop_duplicates()
    df_sales.to_csv('./data/sales_temp.csv', index=False)

def obtain_customers(**kwargs):
    
    customers = pd.DataFrame()
    data = pd.json_normalize(get_users(), sep='_')
    user_columns = ['id', 'name', 'username', 'email']
    customers[['id', 'name', 'username', 'email']] = data[user_columns]
    customers.to_csv('./data/customers_temp.csv', index=False)

def generate_locations(file_path, **kwargs):
    df = pd.read_csv(file_path)

    orders_per_customer_df = df.groupby('customer_id')['order_id'].count().reset_index()
    orders_per_customer_dict = dict(zip(orders_per_customer_df['customer_id'], orders_per_customer_df['order_id']))

    poly = Polygon([(37.8392594, 138.4017597), (38.3134395,140.1449626),
                 (35.1469915,136.6144705), (35.6681207,139.4290279)])
    
    coordinates = generate_points(orders_per_customer_dict, poly)
    df = map_users_coordinates(df, coordinates)

    pos_data = pd.DataFrame()
    pos_data[['latitude', 'longitude']] = df[['latitude', 'longitude']].drop_duplicates()

    df.to_csv('./data/sales_with_pos.csv')
    pos_data.to_csv('./data/pos_data_temp.csv', index = False)


def get_pos_data():
    from sqlalchemy import create_engine

    engine = create_engine(f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PWD')}@{os.getenv('POSTGRES_HOST')}/{os.getenv('POSTGRES_DB')}")
    
    pos = pd.read_sql('select id, latitude, longitude from source.pos_details', engine)
    pos.to_csv('./data/pos_db.csv', index=False)


def get_weather_data( **kwargs):
    df = pd.read_csv('./data/pos_data_temp.csv')

    for index, row in df.iterrows():
        weather = get_weather(round(row.latitude, 4), round(row.longitude,4))
        df.loc[index, 'weather_main'] = weather['weather'][0]['main']
        df.loc[index, 'weather_description'] = weather['weather'][0]['description']
        df.loc[index, 'main_temp'] = weather['main']['temp']
        df.loc[index, 'main_feels_like'] = weather['main']['temp']
        df.loc[index, 'main_temp_min'] = weather['main']['temp_min']
        df.loc[index, 'main_temp_max'] = weather['main']['temp_max']
        df.loc[index, 'main_pressure'] = weather['main']['pressure']
        df.loc[index, 'main_humidity'] = weather['main']['humidity']
        df.loc[index, 'main_visibility'] = weather['visibility']
        df.loc[index, 'wind_speed'] = weather['wind']['speed']
        df.loc[index, 'wind_deg'] = weather['wind']['deg']
        df.loc[index, 'country'] = weather['sys']['country']
        df.loc[index, 'main_pressure'] = weather['main']['pressure']
        df.loc[index, 'dt'] = datetime.datetime.strftime(datetime.datetime.now(), "%Y-%m-%d %H:%M:%S")

    
    pos = pd.read_csv('./data/pos_db.csv')
    df_pos = pd.merge(df, pos, left_on= ['latitude', 'longitude'], right_on = ['latitude', 'longitude'])
    
    df_weather = pd.DataFrame()
    df_weather[['pos_id', 'weather', 'weather_des', 'temp','temp_feels_like', 'temp_min', 'temp_max', 'pressure', 
             'humidity', 'visibility', 'wind_speed', 'wind_deg', 'dt']] = df_pos[['id', 'weather_main', 'weather_description', 
                                                                               'main_temp', 'main_feels_like','main_temp_min', 
                                                                               'main_temp_max', 'main_pressure', 'main_humidity',
                                                                                         'main_visibility', 'wind_speed', 'wind_deg', 'dt']].drop_duplicates()
    df_weather.to_csv('./data/df_weather.csv', index=False)                                                                  


def load_data_to_db(file_path, table_name, **kwags):

    df = pd.read_csv(file_path)

    from sqlalchemy import create_engine

    # Replace 'your_database_uri' with the actual URI of your database
    engine = create_engine(f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PWD')}@{os.getenv('POSTGRES_HOST')}/{os.getenv('POSTGRES_DB')}")
    
    # Assuming 'your_table_name' is the table where you want to insert data
    df.to_sql(table_name, engine, schema = 'source', if_exists='append', index=False)


with DAG(
    dag_id="process_data",
    start_date=datetime.datetime(2023, 12, 5),
    catchup=False,
    schedule=None,
    default_args=default_args,
    tags=["test"],
    render_template_as_native_obj=True,
) as dag:
    start = EmptyOperator(
        task_id="start",
    )
    create_schema = PostgresOperator(
        task_id = 'create_schema',
        sql = "CREATE SCHEMA IF NOT EXISTS source;"
    )
    run_alembic_migration = PythonOperator(
         task_id='run_alembic_migration',
         python_callable=run_alembic_initial_migration,
    )
    get_customers = PythonOperator(
        task_id = 'get_customers',
        python_callable=obtain_customers,
    )
    load_customers_to_db = PythonOperator(
         task_id = 'load_customers_to_db',
         python_callable=load_data_to_db,
         op_kwargs={'file_path': './data/customers_temp.csv', 
                    'table_name': 'customers'}
     )
    generate_locations_task = PythonOperator(
        task_id = 'generate_locations',
        python_callable=generate_locations,
        op_kwargs={'file_path': './data/sales_data.csv'}
    )
    load_pos_data_to_db = PythonOperator(
        task_id = 'load_pos_to_db',
        python_callable=load_data_to_db,
        op_kwargs={'file_path': './data/pos_data_temp.csv', 
                   'table_name': 'pos_details'}
    )
    get_pos_data_task = PythonOperator(
        task_id = 'extract_pos_ids',
        python_callable=get_pos_data
    )
    get_weather_task = PythonOperator(
        task_id = 'get_weather_data',
        python_callable=get_weather_data,
    )
    load_weather_data_to_db = PythonOperator(
        task_id = 'load_weather_to_db',
        python_callable=load_data_to_db,
        op_kwargs={'file_path': './data/df_weather.csv', 
                   'table_name': 'weather_data'}
    )
    get_sales_data = PythonOperator(
        task_id='get_sales_data',
        python_callable=get_sales,
        op_kwargs={'file_path': './data/sales_data.csv'},
    )
    load_sales_data_to_db = PythonOperator(
        task_id = 'load_sales_to_db',
        python_callable=load_data_to_db,
        op_kwargs={'file_path': './data/sales_temp.csv', 
                   'table_name': 'sales'}
    ) 
    end = EmptyOperator(
        task_id="end",
    )

    start >> create_schema >> run_alembic_migration >> get_customers >> load_customers_to_db >> generate_locations_task >> load_pos_data_to_db >> get_pos_data_task >> get_weather_task >> load_weather_data_to_db >> get_sales_data >> load_sales_data_to_db >> end
