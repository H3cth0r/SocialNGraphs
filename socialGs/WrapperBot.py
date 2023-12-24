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
