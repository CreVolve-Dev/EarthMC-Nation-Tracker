from utils.grabAPI import GrabAPI

def check_nation(target):
    return True if GrabAPI.post_async("/nations", target) else False