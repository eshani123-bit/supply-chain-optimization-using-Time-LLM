import pandas as pd
import mysql.connector

def sync_sales():
    df = pd.read_csv('latest_sales.csv')

    conn = mysql.connector.connect(
        host='localhost',
        port='3307',
        user='root',
        password='eshani@2004',
        database='supply_chain'
    )
    cursor = conn.cursor()

    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO sales_data (date, product, sales)
            VALUES (%s, %s, %s)
        """, (row['date'], row['product'], row['sales']))

    conn.commit()
    cursor.close()
    conn.close()

if __name__ == '__main__':
    sync_sales()