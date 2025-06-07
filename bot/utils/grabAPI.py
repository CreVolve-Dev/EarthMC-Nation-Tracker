import requests
import aiohttp

class GrabAPI:
    BASE_URL = 'https://api.earthmc.net/v3/aurora/'

    @staticmethod
    def post_sync(endpoint, query):
        url = f"{GrabAPI.BASE_URL}{endpoint}"
        payload = {"query": [query]}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()

    @staticmethod
    async def post_async(endpoint, query):
        url = f"{GrabAPI.BASE_URL}{endpoint}"
        payload = {"query": [query]}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=payload) as response:
                response.raise_for_status()
                return await response.json(content_type=None)