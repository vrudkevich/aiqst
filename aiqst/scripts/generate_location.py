import os
import random

import pandas as pd
from shapely.geometry import Point, Polygon


def polygon_random_point(min_x, min_y, max_x, max_y):
    return Point([random.uniform(min_x, max_x), random.uniform(min_y, max_y)])


def generate_points(orders_per_customer: dict, poly: Polygon) -> dict:

    """
    Generate random coordinates for customers based on the number of orders they have, 
    assuming that customer may have picked up several orders from the same pos.

    Parameters:
        orders_per_customer (dict): Dictionary containing customer_id as keys and total_orders as values.
        polygon_bounds (dict): Dictionary containing bounding box coordinates for the polygon.

    Returns:
        dict: Dictionary containing customer_id as keys and a list of Point coordinates as values.
    """

    customer_coordinates = {}

    # Iterate through customers
    for customer_id, total_orders in orders_per_customer.items():
        
        customer_coordinates[customer_id] = []

        # Generate coordinates for each order
        for _ in range(total_orders):
            # 70% chance to reuse the same coordinates, 30% chance to generate new coordinates
            if random.random() < 0.7 and customer_coordinates[customer_id]:
                coordinates = random.choice(customer_coordinates[customer_id])
            else:
                coordinates = polygon_random_point(*(poly.bounds))

            customer_coordinates[customer_id].append(coordinates)
    
    return customer_coordinates

def map_users_coordinates(df: pd.DataFrame, coordinates_dict: dict) -> pd.DataFrame:
    """
    Randomly map generated coordinates to the corresponding customer_ids in the DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame containing customer data.
        coordinates (dict): Dictionary containing customer_id as keys and a list of Point coordinates as values.

    Returns:
        pd.DataFrame: Updated DataFrame with latitude and longitude columns.
    """

    for row in df.itertuples():
        customer_id = int(row.customer_id)

        # Retrieve coordinates for the customer
        coordinates = coordinates_dict.get(customer_id, [])

        # Assign coordinates based on order_id
        if coordinates:
            point = coordinates.pop()
            df.at[row.Index, 'latitude'] = point.x
            df.at[row.Index, 'longitude'] = point.y

    return df 

# def get_coordinates_range():

#     load_dotenv()

#     poly = Polygon([(37.8392594, 138.4017597), (38.3134395,140.1449626),
#                 (35.1469915,136.6144705), (35.6681207,139.4290279)])
    
#     min_x, min_y, max_x, max_y = poly.bounds

#     return min_x, min_y, max_x, max_y