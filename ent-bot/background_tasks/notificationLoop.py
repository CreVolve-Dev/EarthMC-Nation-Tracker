from aiohttp.web_exceptions import HTTPError

import disnake
from disnake.ext import commands, tasks
import logging

from models.nationData import Nation, Town, Citizen
from models.serverConfiguration import ServerConfiguration

from utils.grabObjects import GrabObjects
from utils.grabAPI import GrabAPI

from aiolimiter import AsyncLimiter
import asyncio
from tortoise.exceptions import DoesNotExist, IntegrityError, OperationalError

checks = ["residents", "towns"]


class NotificationLoop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notification_loop.start()
        self.rate_limit = AsyncLimiter(10, 1)  # FIX: 10 requests per second instead of 100 concurrent

    def cog_unload(self):
        self.notification_loop.cancel()

    async def grab_api_with_throttle(self, endpoint, data):
        try:
            async with self.rate_limit:
                return await GrabAPI.post_async(endpoint, data)
        except Exception as e:
            logging.error(f"API call failed for {endpoint}/{data}: {e}")
            return None

    async def process_server(self, server, gained, lost, check, nation):
        try:
            object_grabber = GrabObjects(self.bot)

            server_object = await object_grabber.get_guild(server)
            if server_object is None:
                logging.warning(f"Could not fetch guild {server}, skipping...")
                return

            try:
                server_config_object = await ServerConfiguration.get_or_none(server_id=server)
                if server_config_object is None:
                    logging.warning(f"No configuration found for server {server}")
                    return
            except OperationalError as e:
                logging.error(f"Database connection error for server {server}: {e}")
                return
            except Exception as e:
                logging.error(f"Database error for server {server}: {e}")
                return

            channel_check = server_config_object.player_updates_channel if check == "residents" else server_config_object.town_updates_channel
            status_check = server_config_object.player_updates_status if check == "residents" else server_config_object.town_updates_status

            if not status_check:
                return

            send_channel = None
            if channel_check:
                try:
                    send_channel = await object_grabber.get_channel(channel_check)
                except (disnake.NotFound, disnake.Forbidden) as e:
                    logging.warning(f"Cannot access channel {channel_check} in server {server}: {e}")
                    return
                except Exception as e:
                    logging.error(f"Error fetching channel {channel_check}: {e}")
                    return

            if send_channel is None:
                logging.warning(f"No valid notification channel for server {server}")
                return

            try:
                if check == "residents":
                    if gained:
                        message = "\n".join(
                            [f"**{thing}** has joined **{nation}**" for thing in gained[:10]])  # Limit message length
                        await send_channel.send(message)
                    if lost:
                        message = "\n".join(
                            [f"**{thing}** has left **{nation}**" for thing in lost[:10]])  # Limit message length
                        await send_channel.send(message)
                else:
                    if gained:
                        message = "\n".join([f"The town **{thing}** has joined **{nation}**" for thing in gained[:10]])
                        await send_channel.send(message)
                    if lost:
                        message = "\n".join([f"The town **{thing}** has left **{nation}**" for thing in lost[:10]])
                        await send_channel.send(message)
            except (disnake.Forbidden, disnake.HTTPException) as e:
                logging.error(f"Failed to send notification to channel {channel_check}: {e}")
            except Exception as e:
                logging.error(f"Unexpected error sending notification: {e}")

        except Exception as e:
            logging.error(f"Critical error in process_server for server {server}: {e}", exc_info=True)

    async def process_nation(self, nation, check):
        try:
            api_nation_data = await self.grab_api_with_throttle('nations', nation.name)

            if not api_nation_data:
                logging.warning(f"No API data returned for nation: {nation.name}")
                return

            if not isinstance(api_nation_data, list) or len(api_nation_data) == 0:
                logging.warning(f"Invalid API response format for nation: {nation.name}")
                return

            nation_info = api_nation_data[0]

            if check == "residents":
                if "residents" not in nation_info:
                    logging.warning(f"No residents data for nation: {nation.name}")
                    return
                api_data = sorted(
                    [resident.get("name") for resident in nation_info["residents"] if resident.get("name")])
            else:
                if "towns" not in nation_info:
                    logging.warning(f"No towns data for nation: {nation.name}")
                    return
                api_data = sorted([town.get("name") for town in nation_info["towns"] if town.get("name")])

            try:
                if check == "residents":
                    db_data = sorted([citizen.name for citizen in await Citizen.filter(nation=nation.name)])
                else:
                    db_data = sorted([town.name for town in await Town.filter(nation=nation.name)])
            except OperationalError as e:
                logging.error(f"Database connection error when fetching {check} for {nation.name}: {e}")
                return
            except Exception as e:
                logging.error(f"Database error when fetching {check} for {nation.name}: {e}")
                return

            gained = [item for item in api_data if item not in db_data]
            lost = [item for item in db_data if item not in api_data]

            audience_list = nation.player_updates_audience if check == "residents" else nation.town_updates_audience

            if not gained and not lost:
                return

            server_tasks = [
                self.process_server(server, gained, lost, check, nation_info.get("name", nation.name))
                for server in audience_list
            ]
            results = await asyncio.gather(*server_tasks, return_exceptions=True)
            for result in results:
                if isinstance(result, Exception):
                    logging.error(f"Server processing failed: {result}")

            try:
                if check == "residents":
                    if gained:
                        for name in gained:
                            try:
                                await Citizen.get_or_create(name=name, nation=nation)
                            except IntegrityError:
                                logging.debug(f"Citizen {name} already exists, skipping...")
                    if lost:
                        await Citizen.filter(name__in=lost, nation=nation.name).delete()
                else:
                    if gained:
                        for name in gained:
                            try:
                                await Town.get_or_create(name=name, nation=nation)
                            except IntegrityError:
                                logging.debug(f"Town {name} already exists, skipping...")
                    if lost:
                        await Town.filter(name__in=lost, nation=nation.name).delete()
            except OperationalError as e:
                logging.error(f"Database connection error during update for {nation.name}: {e}")
            except Exception as e:
                logging.error(f"Database update failed for {nation.name}: {e}")

        except Exception as e:
            logging.error(f"Critical error in process_nation for {nation.name}: {e}", exc_info=True)

    @tasks.loop(seconds=30)
    async def notification_loop(self):
        logging.info("[notification_loop] Starting...")
        try:
            try:
                nations_to_track = await Nation.all()
            except OperationalError as e:
                logging.error(f"Database connection error in notification_loop: {e}")
                return
            except Exception as e:
                logging.error(f"Database error fetching nations: {e}")
                return

            for check in checks:
                if nations_to_track:
                    nation_tasks = [
                        self.process_nation(nation, check)
                        for nation in nations_to_track
                    ]
                    results = await asyncio.gather(*nation_tasks, return_exceptions=True)
                    for result in results:
                        if isinstance(result, Exception):
                            logging.error(f"Nation processing failed: {result}")

            logging.info("[notification_loop] Finished.")

        except Exception as e:
            logging.error(f"[notification_loop] Critical error: {e}", exc_info=True)
        finally:
            pass

    @notification_loop.before_loop
    async def before_notification_loop(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(NotificationLoop(bot))