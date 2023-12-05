import os
import sys
from datetime import datetime

import pandas as pd
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from aiqst.db.base_class import Base

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # noqa

def perform_bulk_insert():

    load_dotenv()

    DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PWD')}@{os.getenv('POSTGRES_HOST')}/{os.getenv('POSTGRES_DB')}"

    df = pd.read_csv('data/ready_data.csv')

    engine = create_engine(DATABASE_URL)

    # Create the table if not exists
    Base.metadata.create_all(engine, checkfirst=True)

    # Convert Pandas DataFrame to a list of dictionaries
    customers = pd.DataFrame()
    customers[['id', 'name', 'username', 'email']] = df[['customer_id', 'name', 'username', 'email']].drop_duplicates()
    customers.to_sql('customers',engine, schema = 'source', if_exists='append', index=False)
    
    df[['latitude', 'longitude']].drop_duplicates().to_sql('pos_details', engine, schema = 'source', if_exists='append', index=False)

    pos = pd.read_sql('select id, latitude, longitude from source.pos_details', engine)

    df_pos = pd.merge(df, pos, left_on= ['latitude', 'longitude'], right_on = ['latitude', 'longitude'])
    
    df_sales = pd.DataFrame()
    df_sales[['order_id', 'customer_id', 'product_id', 'pos_id', 'price', 'qty', 'order_date']] = df_pos[['order_id', 'customer_id',  'product_id','id_y', 'price', 'quantity', 'order_date']].drop_duplicates()
    
    df_sales.to_sql('sales', engine, schema = 'source', if_exists='append', index=False)
    
    df_weather = pd.DataFrame()
    df_weather[['pos_id', 'weather', 'weather_des', 'temp','temp_feels_like', 'temp_min', 'temp_max', 'pressure', 
            'humidity', 'visibility', 'wind_speed', 'wind_deg', 'dt']] = df_pos[['id_y', 'weather_main', 'weather_description', 
                                                                                 'main_temp', 'main_feels_like','main_temp_min', 
                                                                                 'main_temp_max', 'main_pressure', 'main_humidity',
                                                                                 'main_visibility', 'wind_speed', 'wind_deg', 'dt']].drop_duplicates()
    
    df_weather.to_sql('weather_data', engine, schema ='source', if_exists='append', index=False)

