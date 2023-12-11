import sqlite3
import pandas as pd

conn = sqlite3.connect('users_db.db')
cursor = conn.cursor()
pd.set_option('display.max_columns', None)

if __name__ == "__main__":
    query = "SELECT * FROM user_info"
    df = pd.read_sql_query(query, conn)
    print(df[(df['contact_phone_number'] != "") & pd.notna(df['contact_phone_number'])])
