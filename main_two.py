from socialGs.DBHandler import DBHandler
from socialGs.WrapperBot import WrapperBot
from credentials import headers, example_user

dbh = DBHandler("users_db.db")
wpb = WrapperBot(headers)

def createCorpus(user_id_t):
    user_data   = wpb.fetchFriendShips(user_id_t, "following", 10)
    ids         = dbh.insertData(user_id_t, user_data)
    for pk in ids:
        user_info = wpb.fetchUserInfo(pk)['user']
        dbh.insertUserInfo(user_info)

if __name__ == "__main__":
    createCorpus(example_user) 
