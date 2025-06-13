from aiohttp.web_exceptions import HTTPError

import disnake
from disnake.ext import commands, tasks
import logging

from models.nationData import Nation, Town, Citizen
from models.serverConfiguration import ServerConfiguration

from utils.grabObjects import GrabObjects
from utils.grabAPI import GrabAPI
import logging

from aiolimiter import AsyncLimiter

import asyncio

checks = ["residents", "towns"]

class NotificationLoop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notification_loop.start()
        self.rate_limit = AsyncLimiter(100)

    def cog_unload(self):
        self.notification_loop.cancel()

    async def grab_api_with_throttle(self, endpoint, data):
        async with self.rate_limit:
            return await GrabAPI.post_async(endpoint, data)

    async def process_server(self, server, gained, lost, check, nation):
        object_grabber = GrabObjects(self.bot)
        server_object = await object_grabber.get_guild(server)
        server_config_object = await ServerConfiguration.get(server_id=server)

        if server_object is None:
            return

        channel_check = server_config_object.player_updates_channel if check == "residents" else server_config_object.town_updates_channel
        status_check = server_object.player_updates_status if check == "residents" else server_object.town_updates_status

        print(f"{server} has their status at {status_check}")

        send_channel = await object_grabber.get_channel(channel_check) if channel_check is not None else None

        if status_check:
            if send_channel is not None:
                if check == "residents":
                    if gained:
                        await send_channel.send("\n".join([f"**{thing}** has joined **{nation}**" for thing in gained]))
                    if lost:
                        await send_channel.send("\n".join([f"**{thing}** has left **{nation}**" for thing in lost]))
                else:
                    if gained:
                        await send_channel.send("\n".join([f"The town **{thing}** has joined **{nation}**" for thing in gained]))
                    if lost:
                        await send_channel.send("\n".join([f"The town **{thing}** has left **{nation}**" for thing in lost]))

    async def process_nation(self, nation, check):
        api_nation_data = await self.grab_api_with_throttle('nations', nation.name)

        api_data = list(resident["name"] for resident in api_nation_data[0]["residents"]) if check == "residents" else list(town["name"] for town in api_nation_data[0]["towns"])
        db_data = list(citizen.name for citizen in await Citizen.filter(nation=nation.name)) if check == "residents" else list(town.name for town in await Town.filter(nation=nation.name))
        gained = [item for item in api_data if item not in db_data]
        lost = [item for item in db_data if item not in api_data]

        audience_list = nation.player_updates_audience if check == "residents" else nation.town_updates_audience

        if not gained and not lost:
            return

        server_tasks = [
            self.process_server(server, gained, lost, check, api_nation_data[0]["name"])
            for server in audience_list
        ]
        await asyncio.gather(*server_tasks, return_exceptions=True)

        if check == "residents":
            await Citizen.bulk_create([Citizen(name=thing, nation=nation) for thing in gained])
            await Citizen.filter(name__in=lost, nation=nation.name).delete()
        else:
            await Town.bulk_create([Town(name=thing, nation=nation) for thing in gained])
            await Town.filter(name__in=lost, nation=nation.name).delete()

    @tasks.loop(seconds=30)
    async def notification_loop(self):
        logging.info("[notification_loop] Starting...")
        try:
            nations_to_track = await Nation.all()

            for check in checks:
                if nations_to_track:
                    nation_tasks = [
                        self.process_nation(nation, check)
                        for nation in nations_to_track
                    ]
                    await asyncio.gather(*nation_tasks, return_exceptions=True)

            logging.info("[notification_loop] Finished.")

        except Exception as e:
            logging.error(f"[notification_loop] Error: {e}")

    @notification_loop.before_loop
    async def before_notification_loop(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(NotificationLoop(bot))