import aiohttp
import asyncio

async def post_api_data(end_point, query):

    async with aiohttp.ClientSession() as session:
        async with session.post(url=f'https://api.earthmc.net/v3/aurora/{end_point}', json={"query": [query]}) as response:
            return await response.json(content_type=None)