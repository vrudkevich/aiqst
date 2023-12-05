# Building a Comprehensive Sales Data Pipeline

- [Environment](#Environment)
- [How to set up ](#how-to-set-up)
- [Pipeline Details](#pipeline-details)
- [DB Schema](#db-schema)
- [Data Transformations and Aggregations](#data-transformations-and-aggregations)
    - [Assumptions](#assumptions)


## Environment 
```
docker -v
Docker version 24.0.6, build ed223bc
```
```
docker compose version
Docker Compose version v2.21.0
```
**NOTE**: All further commands assume the user is added to the docker group.

## How to Set Up

>Modify the .env file, changing `POSTGRES_USER, POSTGRES_PWD, POSTGRES_DB, WEATHER_APIKEY` variables.


Run docker-compose:
```
docker compose -p pipeline up
```
**NOTE**: All ports utilized by docker compose should be free.


After all the images will be up and running, Airflow will be available [here](https://localhost:8080), username and password are airflow. Database connection can be set up using variables in the .env file with the default port.

Create a `postgres_default` connection in Airflow using [one of the following ways](https://airflow.apache.org/docs/apache-airflow/stable/howto/connection.html).

>**WARNING!**  When creating a connection, make sure to set host as `main-postgres`, setting up `localhost` is incorrect and will lead to not working dags.

To stop containers, run:
```
docker compose -p pipeline down
```

**NOTE**: The database state will persist in the same state it was in before the containers were shut down.

## Pipeline Details

Data pipeline consists of two DAGs. The first dag is either `process_sales_data` or `initial_data_load` . The second one is `generate_analytics`.

The first dag populates data and inserts it to the database, in case of `process_sales_data` data will be generated from scratch, including generation of coordinates and current weather extract. If running an `initial_data_load` database will be populated with an already prepared sample of data, that will provide consistency in calculations. Both DAGs run migrations beforehand.

The second dag in the pipeline calculates metrics per customer and product, trends by month and quarter, and how weather conditions impact sales.


## DB Schema

### Customers Table
- Represents information about customers.
- **Columns:**
  - `id`: Primary key, auto-incremented integer.
  - `name`: Customer name (up to 100 characters).
  - `username`: Customer username (up to 100 characters).
  - `email`: Customer email (up to 100 characters, non-nullable).
  - `date_registered`: Date and time of customer registration.
- **Relationships:**
  - One-to-Many with the Sales table on id.

### Pos_Details Table
- Represents information about point-of-sale details.
- **Columns:**
  - `id`: Primary key, auto-incremented integer.
  - `name`: Point-of-sale name (up to 100 characters).
  - `latitude`: Latitude of the point of sale.
  - `longitude`: Longitude of the point of sale.
  - `eff_start_date`: Effective start date and time.
  - `eff_end_date`: Effective end date and time.
  - `date_registered`: Date and time of registration.
- **Relationships:**
  - One-to-Many with the Sales table on id.
  - One-to-Many with the Weather_Data on id.

### Products Table
- Represents information about products.
- **Columns:**
  - `product_id`: Primary key, auto-incremented integer.
  - `sku`: Stock Keeping Unit (up to 100 characters, non-nullable).
  - `name`: Product name (up to 100 characters).
  - `qty`: Quantity of the product.
  - `date_registered`: Date and time of product registration.

*Note: One-to-Many relationship with the sales table should exist, but due to lack of data it was commented.*

### Sales Table
- Represents information about sales transactions.
- **Columns:**
  - `id`: Primary key, auto-incremented integer.
  - `order_id`: Order identifier (non-nullable).
  - `product_id`: product_id referencing the Products table.
  - `customer_id`: Foreign key referencing the Customers table.
  - `pos_id`: Foreign key referencing the Pos_Details table.
  - `price`: Sale price.
  - `qty`: Quantity of products sold.
  - `order_date`: Date of the sale order.
  - `date_registered`: Date and time of sale registration.
- **Relationships:**
  - Many-to-One relationship with the Customers table.
  - Many-to-One relationship with the Pos_Details table.

### Weather_Data Table
- Represents information about weather data associated with a point of sale.
- **Columns:**
  - `id`: Primary key, auto-incremented integer.
  - `pos_id`: Foreign key referencing the Pos_Details table.
  - Various columns representing weather data (e.g., `weather`, `temp`, `humidity`, etc.).
  - `dt`: Date and time of the weather data.
  - `date_registered`: Date and time of registration.
- **Relationship:**
  - Many-to-One relationship with the Pos_Details table.

*Note: Some columns and relationships are commented out in the provided code, and you can uncomment and modify them based on your specific requirements.*

## Data Transformations and Aggregations

Data transformations include calculating metrics per customer, including `total orders`, `total products quantity`,  `total amount of money spent`, ` total unique products ordered`, found `top buying customer`. 

For products the following metrics were calculated: `most selling product`, `average order quantity per product`.

Sales trends were calculated per month and quarter. 

To understand how weather impacts sales, `orders` and `revenue` per weather condition were evaluated. 

### Assumptions 

Before initiating any data transformations, I hypothesized that adverse weather conditions, such as heavy snow or rain, should significantly impact sales, as people tend to stay indoors. Conversely, sunny weather should positively influence sales. 

It's important to note that the coordinates were randomly selected within the chosen area, and the weather data was exported at a random moment in time. Upon examining the sales_weather dataset, it becomes evident that sales are indeed strongly influenced by bad weather, supporting the initial hypothesis. Unfortunately, the dataset did not provide sufficient instances of the best weather condition, clear sky, making it challenging to thoroughly test the second hypothesis. 