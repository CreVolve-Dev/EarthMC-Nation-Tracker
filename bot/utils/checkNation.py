import utils.postAPI as postAPI

def check_nation(target):
    return True if postAPI.post_api_data("/nations", target) else False