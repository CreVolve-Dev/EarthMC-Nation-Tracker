import disnake
import os
import json
from disnake.ext import tasks, commands

import datetime

import utils.asyncPostAPI as asyncPostAPI
import utils.formatList as formatList
import utils.updateConfigurations as update_configurations

import constants

async def create_online_embed(target):
    online_players = []

    api_nation_data = await asyncPostAPI.post_api_data('nations', target)

    for resident in api_nation_data[0]["residents"]:
        player_data = await asyncPostAPI.post_api_data('players', resident["name"])

        if player_data[0]["status"]["isOnline"]:
            online_players.append(player_data[0]["name"])
            print(f"{player_data[0]["name"]} is online")

    print(f"{len(online_players)} players online")
    print(f"{formatList.format_list(online_players)} online players")

    embed_var = disnake.Embed(
        title=f"Online Players in {target} | 👥",
        description=f"Last updated: {datetime.datetime.now()}",
        color=0xffffff
    )

    embed_var.add_field(
        name="Online Players:",
        value=f"```{'\n'.join(f"- {name}" for name in online_players)}```" if online_players else "```NONE```",
        inline=False
    )

    embed_var.set_footer(
        text="v3.0 Programmed by CreVolve",
        icon_url="https://i.imgur.com/jdxtHVd.jpeg"
    )

    return embed_var

class OnlineEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.online_embed.start()

    def cog_unload(self):
        self.online_embed.cancel()

    @tasks.loop(seconds=30)
    async def online_embed(self):
        try:
            nations_to_embed = [nations.replace(".json", "") for nations in
                                os.listdir(constants.GROUP_STORAGE_DATA)]

            if nations_to_embed:
                for nation in nations_to_embed:
                    try:
                        with open(f"{constants.GROUP_STORAGE_DATA}/{nation}.json", "r") as f:
                            nation_data = json.load(f)

                        if nation_data["embed_audience"]:
                            embed_var = await create_online_embed(nation_data["target"])

                            for audience in nation_data["embed_audience"]:
                                audience_data = update_configurations.load_server_config(audience)
                                if not audience_data:
                                    print(f"[online_embed] No config for guild {audience}, skipping.")
                                    continue

                                channel_id = audience_data.get("embed_channel")
                                message_id = audience_data.get("embed_message")
                                if not channel_id or not message_id:
                                    print(
                                        f"[online_embed] Missing channel or message ID for guild {audience}, skipping.")
                                    continue

                                try:
                                    channel = await self.bot.fetch_channel(channel_id)
                                    message = await channel.fetch_message(message_id)
                                    await message.edit(content="", embed=embed_var)
                                except Exception as e:
                                    print(f"[online_embed] Error updating embed for guild {audience}: {e}")

                    except Exception as e:
                        print(f"[online_embed] Error processing nation {nation}: {e}")
        except Exception as e:
            print(e)

    @online_embed.before_loop
    async def online_embed_before_loop(self):
        await self.bot.wait_until_ready()

def setup(bot):
    bot.add_cog(OnlineEmbed(bot))