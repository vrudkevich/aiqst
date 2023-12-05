import datetime

from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator

default_args = {
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": datetime.timedelta(minutes=1),
}

with DAG(
    dag_id="generate_analytics",
    start_date=datetime.datetime(2023, 8, 10),
    catchup=False,
    schedule=None,
    default_args=default_args,
    tags=["test"],
    render_template_as_native_obj=True,
) as dag:
    start = EmptyOperator(
        task_id="start",
    )
    customer_metrics = PostgresOperator(
        task_id="calculate_customer_metrics",
        sql = """
                create table if not exists source.sales_metrics_per_customer as 
                select customer_id, 'total_orders_per_customer' as metric, count(order_id) as value, CURRENT_DATE as snapshot_date
                from source.sales
                group by customer_id
                union all 
                select customer_id, 'total_products_qty_per_customer' as metric, sum(qty) as value, CURRENT_DATE as snapshot_date
                from source.sales
                group by customer_id
                union all 
                select customer_id, 'total_spent_per_customer' as metric, sum(price) as value, CURRENT_DATE as snapshot_date
                from source.sales
                group by customer_id
                union all 
                select customer_id, 'total_unique_products_per_customer' as metric, count(distinct product_id) as value, CURRENT_DATE as snapshot_date
                from source.sales
                group by customer_id
                union all
                select customer_id, 'top_buying_customer' as metric, value, CURRENT_DATE as snapshot_date
                from (
                    select customer_id, sum(qty*price) as value
                    from source.sales
                    group by customer_id
                ) t 
                order by value desc;

                CREATE INDEX IF NOT EXISTS idx_sales_metrics_per_customer ON source.sales_metrics_per_customer(customer_id, metric);
            """
    )
    product_metrics = PostgresOperator(
         task_id = 'calculate_products_metrics',
         sql = """  
                create table if not exists source.sales_metrics_per_product as 
                with base as (
                    select product_id, w.weather_des, sum(qty) as total_qty
                    from source.sales s
                    join source.weather_data w ON s.pos_id = w.pos_id
                    group by product_id , w.weather_des
                    order by sum(qty) desc
                    limit 1
                )
                select product_id, 'most_selling_product' as metric, total_qty as value, CURRENT_DATE as snapshot_date
                from base
                union all
                select product_id, 'avg_order_quantity_per_product' as metric, round(sum(qty)/count(order_id), 2) as value, CURRENT_DATE as snapshot_date
                from source.sales
                group by product_id;

                CREATE INDEX IF NOT EXISTS idx_sales_metrics_per_product ON source.sales_metrics_per_product(product_id, metric);
             """
     )
    trends_metrics = PostgresOperator(
        task_id = 'calculate_metrics_trends',
        sql = """
                create table if not exists source.sales_trends as
                select date_part('year', order_date) AS year, 
                date_part('month', order_date) AS trend_period,
                'month' as thend_type,
                SUM(price * qty) AS value, CURRENT_DATE as snapshot_date
                FROM source.sales
                GROUP BY year, trend_period
                union all 
                select date_part('year', order_date) AS year, 
                date_part('quarter', order_date) AS trend_period,
                'month' as thend_type,
                SUM(price * qty) AS value, CURRENT_DATE as snapshot_date
                FROM source.sales
                GROUP BY year, trend_period;

                CREATE INDEX IF NOT EXISTS idx_sales_trends ON source.sales_trends(year, trend_period);
        """
    )
    weathe_metrics = PostgresOperator(
        task_id = 'calculate_metrics_weather',
        sql = """
                create table if not exists source.sales_weather as
                select date_part('year', order_date) AS year, w.weather_des,
                'orders_per_weather_conition' as metric,
                count(s.order_id) AS value,
                CURRENT_DATE as snapshot_date
                from source.sales s
                join source.weather_data w ON s.pos_id = w.pos_id
                group by year, weather_des
                union all
                select date_part('year', order_date) AS year, w.weather_des,
                'revenue_per_weather_conition' as metric,
                sum(s.qty*s.price) AS value,
                CURRENT_DATE as snapshot_date
                from source.sales s
                join source.weather_data w ON s.pos_id = w.pos_id
                group by year, weather_des
                union all
                select date_part('year', order_date) AS year, w.wind_speed::text as weather_des,
                'revenue_per_wind_speed' as metric,
                sum(s.qty*s.price) AS value,
                CURRENT_DATE as snapshot_date
                from source.sales s
                join source.weather_data w ON s.pos_id = w.pos_id
                group by year, wind_speed;

                CREATE INDEX IF NOT EXISTS idx_sales_weather ON source.sales_weather(year, metric);
            """
    )
    end = EmptyOperator(
        task_id="end",
    )

    start >> customer_metrics >> product_metrics >> trends_metrics >> weathe_metrics>> end
