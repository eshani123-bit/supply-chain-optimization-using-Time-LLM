import pandas as pd
import mysql.connector
from prophet import Prophet

def predict_demand(product_name):
    # Connect to your MySQL DB
    conn = mysql.connector.connect(
        host='localhost',
        port='3307',
        user='root',
        password='eshani@2004',
        database='supply_chain'
    )

    # Read sales data for the selected product
    query = f"""
        SELECT date AS ds, sales AS y
        FROM sales_data
        WHERE product = '{product_name}'
    """

    df = pd.read_sql(query, conn)

    # Prophet model training
    model = Prophet()
    model.fit(df)

    # Predict next 7 days
    future = model.make_future_dataframe(periods=7)
    forecast = model.predict(future)

    # Extract forecast for last 7 days
    next_7 = forecast.tail(7)[['ds', 'yhat']]
    predictions = list(zip(next_7['ds'].dt.strftime('%Y-%m-%d'), round(next_7['yhat'])))

    # Sum of predicted sales
    total = round(next_7['yhat'].sum())

    return total, predictions