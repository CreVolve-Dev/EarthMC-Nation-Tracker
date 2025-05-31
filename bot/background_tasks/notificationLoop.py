import os
import json
import constants

from disnake.ext import commands, tasks

import utils.asyncPostAPI as asyncPostAPI

class NotificationLoop(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.notification_loop.start()

    def cog_unload(self):
        self.notification_loop.cancel()

    @tasks.loop(seconds=30)
    async def notification_loop(self):
        nations_to_track = [nations.replace(".json", "") for nations in os.listdir(constants.GROUP_STORAGE_DATA)]

        if nations_to_track:
            for nation in nations_to_track:
                with open(f"{constants.GROUP_STORAGE_DATA}/{nation}.json", "r") as f:
                    nation_data = json.load(f)

                api_nation_data = await asyncPostAPI.post_api_data('nations', nation)
                api_resident_data = list(api_nation_data[0]["residents"])
                api_resident_list = [resident['name'] for resident in api_resident_data]

                residents_gained = list(set(api_resident_list) - set(nation_data["residents"]))
                residents_lost = list(set(nation_data["residents"]) - set(api_resident_list))

                audience_list = nation_data.get("audience")

                for audience in audience_list:
                    with open(f"{constants.SERVER_CONFIGURATION_PATH}/{audience}.json", "r") as f:
                        audience_data = json.load(f)
                    try:
                        if audience_data["notifications_channel"] is not None:
                            send_channel = await self.bot.fetch_channel(int(audience_data["notifications_channel"]))

                        if audience_data["notifications_status"] == "True":
                            if send_channel is not None:
                                for resident in residents_gained:
                                    await send_channel.send(
                                        f"**{resident}** has joined **{api_nation_data[0]["name"]}**")

                                for resident in residents_lost:
                                    await send_channel.send(f"**{resident}** has left **{api_nation_data[0]["name"]}**")
                    except KeyError:
                        pass

                updated_nation_data = nation_data
                updated_nation_data["residents"] = api_resident_list

                with open(f"{constants.GROUP_STORAGE_DATA}/{nation}.json", "w") as f:
                    json.dump(updated_nation_data, f)

    @notification_loop.before_loop
    async def before_notification_loop(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(NotificationLoop(bot))