import sqlite3
import pandas as pd
from functionalities import user_info_create, generate_user_info_insert_query, get_values_by_key

class DBHandler:
    def __init__(self, dbPath_t):
        """
        @brief  Constructor 
        @param  dbPath_t        path and name of .db file(sqlite db).
        """
        self.conn       = sqlite3.connect('users_db.db')
        self.cursor     = self.conn.cursor()
        pd.set_option('display.max_columns', None)
    def initDB(self):
        self.cursor.execute('''
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
        self.conn.commit()

        self.cursor.execute(user_info_create)
        self.conn.commit()

        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS friendships (
                user_pk_id TEXT,
                friend_pk_id TEXT,
                PRIMARY KEY (user_pk_id, friend_pk_id),
                FOREIGN KEY (user_pk_id) REFERENCES users(pk_id),
                FOREIGN KEY (friend_pk_id) REFERENCES users(pk_id)
            )
        ''')
        self.conn.commit()

        """
        0 - not processed
        1 - in process 
        2 - processed
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users_queue (
                user_pk_id TEXT,
                status INTEGER DEFAULT 0,
                PRIMARY KEY (user_pk_id),
                FOREIGN KEY (user_pk_id) REFERENCES users(pk_id)
            )
        ''')
        self.conn.commit()
    def printDB(self):
        """
        @brief  method to print all the tables in the database.
        """
        query = "SELECT * FROM users"
        df = pd.read_sql_query(query, self.conn)
        print(df)
        print(80*"=")
        query = "SELECT * FROM friendships"
        df = pd.read_sql_query(query, self.conn)
        print(df)
        print(80*"=")
        query = "SELECT * FROM user_info"
        df = pd.read_sql_query(query, self.conn)
        print(df)
    def insertData(self, userId_t, jsonData_t):
        """
        @brief  Insert list of users from request
        @param  userId_t        target user id.
        @param  jsonData_t      json Object 
        """
        ids = []
        for user_data in jsonData_t["users"]:
            self.cursor.execute('''
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

            if self.cursor.rowcount > 0:
                ids.append(user_data["pk_id"])

            self.cursor.execute('''
                INSERT OR IGNORE INTO friendships (user_pk_id, friend_pk_id)
                VALUES (?, ?)
            ''', (userId_t, user_data["pk_id"]))
            self.conn.commit()
        return ids

    def insertIntoGenericTable(self, tableName_t, jsonObject_t):
        """
        @brief  Insert json atributes into table.
        @param  tableName_t     name of the table to insert into.
        @param  jsonObject_t    json object to insert.
        """
        columns = get_column_names(tableName_t)
        values = []
        for column in columns:
            column_values = get_values_by_key(jsonObject_t, column)
            value = column_values[0] if column_values else None
            values.append(value)
        placeholders = ','.join(['?' for _ in values])
        query = f"INSERT OR IGNORE INTO {tableName_t} ({', '.join(columns)}) VALUES ({placeholders});"

        try:
            self.cursor.execute(query, values)
            self.conn.commit()
        except Exception as e:
            print(f"Error: {str(e)}")
            self.conn.rollback()
    def insertUserInfo(self, userInfo_t):
        """
        @brief  insert single target user to the db
        @param  userInfo_t target user to insert
        """
        columns = get_column_names("user_info")
        
        # Construct the list of values
        # values = [userInfo_t.get(column, None) for column in columns]
        values = []
        for column in columns:
            column_values = get_values_by_key(userInfo_t, column)
            # Use the first value if available, otherwise set to None
            value = column_values[0] if column_values else None
            values.append(value)

        # Create a string with placeholders for values
        placeholders = ','.join(['?' for _ in values])

        # Construct the SQL query
        query = f"INSERT OR IGNORE INTO user_info ({', '.join(columns)}) VALUES ({placeholders});"

        try:
            # Execute the query with the values
            self.cursor.execute(query, values)
            # Commit the transaction
            self.conn.commit()
        except Exception as e:
            print(f"Error: {str(e)}")
            # Rollback the transaction in case of an error
            self.conn.rollback()
    def getColumnNames(self, tableName):
        """
        @brief      get the names of columns
        @param      table to get column names from
        """
        # self.cursor = self.conn.cursor()

        try:
            # Execute the PRAGMA query to get table information
            self.cursor.execute(f"PRAGMA table_info({tableName})")

            # Fetch all rows from the result
            columns_info = self.cursor.fetchall()

            # Extract column names from the result
            column_names = [column[1] for column in columns_info]

            return column_names
        except Exception as e:
            print(f"Error: {str(e)}")
            return None
