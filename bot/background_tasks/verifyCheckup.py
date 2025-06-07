import os
import json
import disnake
from disnake.ext import commands, tasks

from models.serverConfiguration import ServerConfiguration
from utils.grabObjects import GrabObjects
from utils.grabAPI import GrabAPI

import constants
import logging
import asyncio

class VerifyCheckup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verify_checkup.start()

    def cog_unload(self):
        self.verify_checkup.cancel()

    @tasks.loop(seconds=30)
    async def verify_checkup(self):
        logging.info("[verify_checkup] Starting...")
        servers_to_check = await ServerConfiguration.all()

        tasks = [self.process_server(server) for server in servers_to_check]
        await asyncio.gather(*tasks)

        logging.info("[verify_checkup] Finished.")

    async def process_server(self, server):
        if not server.verified_checkup:
            return
        server_object = await GrabObjects.get_guild(self, server.server_id)
        if server_object is None:
            return
        try:
            give_citizen_role = await server_object.fetch_role(server.citizen_role)
        except disnake.NotFound:
            server.citizen_role = None
            await server.save()
            return
        await self.process_citizens(server, server_object, give_citizen_role)

    async def process_citizens(self, server, server_object, give_citizen_role):
        for citizen in server.verified_citizens:
            try:
                citizen_object = await server_object.fetch_member(citizen["discord"])
                await citizen_object.add_roles(give_citizen_role)
            except disnake.NotFound:
                server.verified_citizens.remove(citizen)
            except disnake.Forbidden:
                continue
            await asyncio.sleep(0)
        await server.save()

    @verify_checkup.before_loop
    async def before_verify_checkup(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(VerifyCheckup(bot))