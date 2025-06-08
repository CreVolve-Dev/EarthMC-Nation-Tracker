import disnake
from disnake.ext import tasks, commands
import asyncio
import datetime
import logging

from aiolimiter import AsyncLimiter

from models.nationData import Nation
from models.serverConfiguration import ServerConfiguration
from utils.grabObjects import GrabObjects
from utils.grabAPI import GrabAPI

logging.basicConfig(level=logging.INFO)

class OnlineEmbed(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.rate_limit = AsyncLimiter(50)  # Limit concurrent API calls to 10
        self.online_embed.start()

    def cog_unload(self):
        self.online_embed.cancel()

    async def grab_api_with_throttle(self, endpoint, data):
        async with self.rate_limit:
            return await GrabAPI.post_async(endpoint, data)

    async def create_online_embed(self, target):
        online_players = []

        api_nation_data = await self.grab_api_with_throttle('nations', target)
        if not api_nation_data or "residents" not in api_nation_data[0]:
            logging.error(f"Failed to fetch nation data for: {target}")
            return None

        player_tasks = [
            self.grab_api_with_throttle('players', resident["name"])
            for resident in api_nation_data[0]["residents"]
        ]
        player_results = await asyncio.gather(*player_tasks, return_exceptions=True)

        for player_data in player_results:
            if isinstance(player_data, Exception):
                logging.error(f"Error fetching player data: {player_data}")
                continue

            if not isinstance(player_data, list) or not player_data:
                logging.error(f"Unexpected player data format: {player_data}")
                continue

            player = player_data[0]

            if player.get("status", {}).get("isOnline"):
                online_players.append(player.get("name", "Unknown"))

        embed_var = disnake.Embed(
            title=f"Online Players in {target} | 👥",
            description=f"Last updated: {datetime.datetime.now()}",
            color=0xffffff
        )

        if online_players:
            for i in range(0, len(online_players), 10):  # 10 players per field
                embed_var.add_field(
                    name=f"Players {i + 1}-{i + len(online_players[i:i + 10])}",
                    value=f"```{'\n'.join(f'- {name}' for name in online_players[i:i + 10])}```",
                    inline=False
                )
        else:
            embed_var.add_field(name="Online Players:", value="```NONE```", inline=False)

        embed_var.set_footer(
            text="v3.0 Programmed by CreVolve",
            icon_url="https://i.imgur.com/jdxtHVd.jpeg"
        )
        return embed_var

    @tasks.loop(seconds=30)
    async def online_embed(self):
        logging.info("[online_embed] Starting...")
        try:
            nations = await Nation.all()
            if not nations:
                logging.warning("[online_embed] No nations found.")
                return

            tasks = [self.process_nation(nation) for nation in nations]
            await asyncio.gather(*tasks)

        except Exception as e:
            logging.error(f"[online_embed] Unexpected error: {e}")
        logging.info("[online_embed] Finished.")

    async def process_nation(self, nation):
        if not nation.embed_audience:
            return

        embed_var = await self.create_online_embed(nation.name)
        if not embed_var:
            logging.error(f"[process_nation] Failed to create embed for: {nation.name}")
            return

        for audience in nation.embed_audience:
            audience_data = await ServerConfiguration.get_or_none(server_id=audience)
            if not audience_data:
                logging.warning(f"[process_nation] No config for guild {audience}, skipping.")
                continue

            channel_id = audience_data.online_embed_channel
            message_id = audience_data.online_embed_message
            if not channel_id or not message_id:
                logging.warning(f"[process_nation] Missing channel/message ID for guild {audience}.")
                continue

            try:
                channel = await GrabObjects.get_channel(self, channel_id)
                message = await GrabObjects.get_message(channel, message_id)

                if message:
                    await message.edit(content="", embed=embed_var)
                else:
                    logging.warning(f"[process_nation] Message not found for guild {audience}.")
            except Exception as e:
                logging.error(f"[process_nation] Error updating embed for guild {audience}: {e}")

    @online_embed.before_loop
    async def online_embed_before_loop(self):
        await self.bot.wait_until_ready()


def setup(bot):
    bot.add_cog(OnlineEmbed(bot))
