import requests
import sqlite3
import json
import pandas as pd
import sys
from credentials import headers, headers_info, example_user
from functionalities import user_info_create, generate_user_info_insert_query, get_values_by_key

conn = sqlite3.connect('users_db.db')
cursor = conn.cursor()
pd.set_option('display.max_columns', None)

def fetchFriendships(user_id, list_t, count_t):
    url = f"https://www.instagram.com/api/v1/friendships/{user_id}/{list_t}/?count={count_t}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("GET request successful")
        json_data = response.json()
        # json_data = json.dumps(json_data, indent=2)
        # print(json_data['users'][0])
        return json_data
    else:
        print(f"GET request failed with status code {response.status_code}")
        print(response.text) 
        return
def fetchUserInfo(user_id):
    url_info = f"https://www.instagram.com/api/v1/users/{user_id}/info/"
    response = requests.get(url_info, headers=headers)

    if response.status_code == 200:
        print("GET request successful")
        json_data = response.json()
        print(json_data.keys())
        return json_data
    else:
        print(f"GET request failed with status code {response.status_code}")
        print(response.text) 
        return
def insertData(user_id_t, json_data):
    ids = []
    for user_data in json_data["users"]:
        cursor.execute('''
            INSERT INTO users
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user_data["pk_id"],
            user_data["full_name"],
            int(user_data["is_private"]),
            user_data["profile_pic_url"],
            int(user_data["is_verified"]),
            user_data["username"],
            int(user_data["latest_reel_media"]),
            int(user_data["is_favorite"])
        ))
        cursor.execute('''
            INSERT INTO friendships (user_pk_id, friend_pk_id)
            VALUES (?, ?)
        ''', (user_id_t, user_data["pk_id"]))
        conn.commit()
        ids.append(user_data["pk_id"])
    return ids

def insertUserInfo(user_info_t):
    columns = get_column_names("user_info")
    
    # Construct the list of values
    # values = [user_info_t.get(column, None) for column in columns]
    values = []
    for column in columns:
        column_values = get_values_by_key(user_info_t, column)
        # Use the first value if available, otherwise set to None
        value = column_values[0] if column_values else None
        values.append(value)

    # Create a string with placeholders for values
    placeholders = ','.join(['?' for _ in values])

    # Construct the SQL query
    query = f"INSERT INTO user_info ({', '.join(columns)}) VALUES ({placeholders});"

    try:
        # Execute the query with the values
        cursor.execute(query, values)
        # Commit the transaction
        conn.commit()
    except Exception as e:
        print(f"Error: {str(e)}")
        # Rollback the transaction in case of an error
        conn.rollback()

def printDB():
    query = "SELECT * FROM users"
    df = pd.read_sql_query(query, conn)
    print(df)
    print(80*"=")
    query = "SELECT * FROM friendships"
    df = pd.read_sql_query(query, conn)
    print(df)
    print(80*"=")
    query = "SELECT * FROM user_info"
    df = pd.read_sql_query(query, conn)
    print(df)
def initDB():
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            pk_id TEXT PRIMARY KEY,
            full_name TEXT,
            is_private INTEGER,
            profile_pic_url TEXT,
            is_verified INTEGER,
            username TEXT,
            latest_reel_media INTEGER,
            is_favorite INTEGER
        )
    ''')
    conn.commit()

    cursor.execute(user_info_create)
    conn.commit()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS friendships (
            user_pk_id TEXT,
            friend_pk_id TEXT,
            PRIMARY KEY (user_pk_id, friend_pk_id),
            FOREIGN KEY (user_pk_id) REFERENCES users(pk_id),
            FOREIGN KEY (friend_pk_id) REFERENCES users(pk_id)
        )
    ''')
    conn.commit()
def get_column_names(table_name):
    cursor = conn.cursor()

    try:
        # Execute the PRAGMA query to get table information
        cursor.execute(f"PRAGMA table_info({table_name})")

        # Fetch all rows from the result
        columns_info = cursor.fetchall()

        # Extract column names from the result
        column_names = [column[1] for column in columns_info]

        return column_names
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def createCorpus(user_id_t):
    user_data = fetchFriendships(user_id_t, "following", 10)
    ids = insertData(user_id_t, user_data)
    for pk in ids:
        user_info = fetchUserInfo(pk)['user']
        insertUserInfo(user_info)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--initDB":
            initDB()
        elif sys.argv[1] == "--printDB":
            printDB()
        else:
            exit(0) 
    else:
        createCorpus(example_user)
    conn.close()
     
