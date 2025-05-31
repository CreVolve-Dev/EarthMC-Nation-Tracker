import os
import json
import disnake
from disnake.ext import commands, tasks

import constants

class VerifyCheckup(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.verify_checkup.start()

    def cog_unload(self):
        self.verify_checkup.cancel()

    @tasks.loop(seconds=30)
    async def verify_checkup(self):
        servers_to_check = [server.replace(".json", "") for server in os.listdir(constants.SERVER_CONFIGURATION_PATH)]

        for server in servers_to_check:
            with open(f"{constants.SERVER_CONFIGURATION_PATH}/{server}.json", "r+") as file:
                data = json.load(file)
                try:
                    if data["verified_checkup"] not in ["None", None, "False", False]:
                        server_object = await self.bot.fetch_guild(server)
                        try:
                            citizen_role = server_object.fetch_role(data["citizen_role"])
                        except disnake.NotFound:
                            data["citizen_role"] = None
                            file.seek(0)
                            json.dump(data, file, indent=4)
                            file.truncate()
                        verified_citizens = data["verified_citizens"]
                        for verified_citizen in data["verified_citizens"]:
                            try:
                                citizen_object = await server_object.fetch_user(verified_citizen["discord"])
                                await citizen_object.add_roles(citizen_role)
                            except disnake.NotFound:
                                verified_citizens.remove(verified_citizen)
                        data["verified_citizens"] = verified_citizens
                        file.seek(0)
                        json.dump(data, file, indent=4)
                        file.truncate()
                except KeyError:
                    pass

    @verify_checkup.before_loop
    async def before_verify_checkup(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(VerifyCheckup(bot))