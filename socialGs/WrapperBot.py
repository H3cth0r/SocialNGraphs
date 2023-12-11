import sys
import requests
import json
import time

class WrapperBot: 
    def __init__(self, headers_t):
        """
        @brief  Bot for fetching data
        """
        self.headers    = headers_t
    def fetchFriendShips(self, user_id, list_t, count_t, max_id=0):
        """
        @brief  Make requests and return obj
        @param  user_id
        @param  list_t
        @param  count_t
        @param max_id 
        """
        url = f"https://www.instagram.com/api/v1/friendships/{user_id}/{list_t}/?count={count_t}&max_id={max_id}"
        response = requests.get(url, headers=self.headers)

        if response.status_code == 200:
            json_data = response.json()
            return json_data
        else:
            print(f"GET request failed with status code {response.status_code}")
            print(response.text) 
            return
    def fetchUserInfo(self, user_id):
        """
        @brief  fetch single user data
        """
        url_info = f"https://www.instagram.com/api/v1/users/{user_id}/info/"
        response = requests.get(url_info, headers=self.headers)

        if response.status_code == 200:
            # print("GET request successful")
            json_data = response.json()
            # print(json_data.keys())
            return json_data
        else:
            print(f"GET request failed with status code {response.status_code}")
            print(response.text) 
            return
    def fetchTargetUser(self):
        """
        @brief  fetch target user data
        """
        target_user_info = fetchUserInfo(user_id_t)['user']
        insertIntoGenericTable('users', target_user_info) 
        insertUserInfo(target_user_info) 

        iterateUserList(user_id_t, max_it=int(target_user_info['following_count']))

        iterateUserList(user_id_t, type_list="followers", max_it=int(target_user_info['follower_count']))
    def iterateUserList(sefl, referal_user_id, type_list="following", count=50, max_it=1000):
        """
        @brief  method that iterates over a single following/followers list
        """
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

