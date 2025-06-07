from utils.grabAPI import GrabAPI

async def check_nation(target):
    return True if await GrabAPI.post_async("nations", target) else False