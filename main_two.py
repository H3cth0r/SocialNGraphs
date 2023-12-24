from socialGs.DBHandler import DBHandler
from socialGs.WrapperBot import WrapperBot
from credentials import headers, example_user
import time
from tqdm import tqdm
import sys
"""
Main code refactorization testing script.
"""

dbh = DBHandler("users_db.db")
wpb = WrapperBot(headers)

def createCorpus(user_id_t):
    user_data   = wpb.fetchFriendShips(user_id_t, "following", 10)
    ids         = dbh.insertData(user_id_t, user_data)
    for pk in ids:
        user_info = wpb.fetchUserInfo(pk)['user']
        dbh.insertUserInfo(user_info)

def iterateUserList(referal_user_id, type_list="following", count=50, max_it=1000):
    progress_bar = tqdm(total=max_it, desc=f"Fetching User list - {type_list}", unit="iteration")
    max_id = 0
    counter_samples = 0
    while max_id != None:
        user_data   = wpb.fetchFriendShips(referal_user_id, "following", count, max_id)
        ids         = dbh.insertData(referal_user_id, user_data)
        for pk in ids:
            dbh.cursor.execute('''
                SELECT * FROM user_info
                WHERE pk_id = ?
            ''', (pk,))
            result = dbh.cursor.fetchone()
            time.sleep(6)

            if result is not None:continue

            user_info = wpb.fetchUserInfo(pk)['user']
            dbh.insertUserInfo(user_info)
            dbh.cursor.execute('''
                INSERT OR IGNORE INTO users_queue (user_pk_id, status) 
                VALUES (?, ?)
            ''', (pk,0))
            dbh.conn.commit()
            counter_samples += 1 
            progress_bar.update(1)

        if counter_samples > max_it:
            break
        max_id = int(user_data.get('next_max_id', None))
        time.sleep(3)
    progress_bar.close()

def fetchTargetUser(user_id_t):
    # Add target  user info to db
    target_user_info = wpb.fetchUserInfo(user_id_t) 
    dbh.insertIntoGenericTable('users', target_user_info)
    dbh.insertUserInfo(target_user_info)
    print('done inserting target user to db')
    
    # Iterate over following list
    # add users to stack
    iterateUserList(user_id_t, max_it=int(target_user_info["user"]['following_count']))

    # Iterate over followers list
    # add users to stack
    iterateUserList(user_id_t, type_list="followers", max_it=int(target_user_info['following_count']))

if __name__ == "__main__":
    # createCorpus(example_user) 
    if len(sys.argv) > 1:
        if sys.argv[1] == "--initDB":
            dbh.initDB()
        elif sys.argv[1] == "--printDB":
            dbh.printDB()
        else:
            exit(0) 
    else:
        fetchTargetUser(example_user)
        # createCorpus(example_user)
    dbh.conn.close()
