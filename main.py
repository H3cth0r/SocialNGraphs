import requests
import time
import sqlite3
import json
import pandas as pd
import sys
from tqdm import tqdm
from credentials import headers, headers_info, example_user
from functionalities import user_info_create, generate_user_info_insert_query, get_values_by_key

conn = sqlite3.connect('users_db.db')
cursor = conn.cursor()
pd.set_option('display.max_columns', None)

def fetchFriendships(user_id, list_t, count_t, max_id=0):
    url = f"https://www.instagram.com/api/v1/friendships/{user_id}/{list_t}/?count={count_t}&max_id={max_id}"
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # print("GET request successful")
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
        # print("GET request successful")
        json_data = response.json()
        # print(json_data.keys())
        return json_data
    else:
        print(f"GET request failed with status code {response.status_code}")
        print(response.text) 
        return
def insertData(user_id_t, json_data):
    ids = []
    for user_data in json_data["users"]:
        cursor.execute('''
            INSERT OR IGNORE INTO users
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

        # Check if a new user was inserted
        # ids.append(user_data["pk_id"])
        if cursor.rowcount > 0:
            ids.append(user_data["pk_id"])

        cursor.execute('''
            INSERT OR IGNORE INTO friendships (user_pk_id, friend_pk_id)
            VALUES (?, ?)
        ''', (user_id_t, user_data["pk_id"]))
        conn.commit()
    return ids
def insertIntoGenericTable(tableName_t, jsonObj):
    columns = get_column_names(tableName_t)
    values = []
    for column in columns:
        column_values = get_values_by_key(jsonObj, column)
        value = column_values[0] if column_values else None
        values.append(value)
    placeholders = ','.join(['?' for _ in values])
    query = f"INSERT OR IGNORE INTO {tableName_t} ({', '.join(columns)}) VALUES ({placeholders});"

    try:
        cursor.execute(query, values)
        conn.commit()
    except Exception as e:
        print(f"Error: {str(e)}")
        conn.rollback()
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
    query = f"INSERT OR IGNORE INTO user_info ({', '.join(columns)}) VALUES ({placeholders});"

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

    """
    0 - not processed
    1 - in process 
    2 - processed
    """
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users_queue (
            user_pk_id TEXT,
            status INTEGER DEFAULT 0,
            PRIMARY KEY (user_pk_id),
            FOREIGN KEY (user_pk_id) REFERENCES users(pk_id)
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
def iterateUserList(referal_user_id, type_list="following", count=50, max_it=1000):
    progress_bar = tqdm(total=max_it, desc=f"Fetching User list - {type_list}", unit="iteration")
    max_id = 0
    counter_samples = 0
    while max_id != None:
        user_data = fetchFriendships(referal_user_id, "following", count, max_id)
        ids = insertData(referal_user_id, user_data)
        # print(user_data)
        for pk in ids:
            # if user already in db, then dont fetch data
            cursor.execute('''
                SELECT * FROM user_info
                WHERE pk_id = ?
            ''', (pk,))
            result = cursor.fetchone()
            time.sleep(6)

            if result is not None:continue

            user_info = fetchUserInfo(pk)['user']
            insertUserInfo(user_info)
            cursor.execute('''
                INSERT OR IGNORE INTO users_queue (user_pk_id, status) 
                VALUES (?, ?)
            ''', (pk,0))
            conn.commit()
            counter_samples += 1 
            progress_bar.update(1)

        if counter_samples > max_it:
            break
        max_id = int(user_data.get('next_max_id', None))
        time.sleep(3)
    progress_bar.close()
def fetchTargetUser(user_id_t):
    # Add target user info to db
    target_user_info = fetchUserInfo(user_id_t)['user']
    insertIntoGenericTable('users', target_user_info) 
    insertUserInfo(target_user_info) 

    # iterate over all the following 
    # add users to stack
    iterateUserList(user_id_t, max_it=int(target_user_info['following_count']))

    # iterate over all the followers 
    # add users to stack
    iterateUserList(user_id_t, type_list="followers", max_it=int(target_user_info['follower_count']))

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--initDB":
            initDB()
        elif sys.argv[1] == "--printDB":
            printDB()
        else:
            exit(0) 
    else:
        # createCorpus(example_user)
        fetchTargetUser(example_user)
    conn.close()
     
