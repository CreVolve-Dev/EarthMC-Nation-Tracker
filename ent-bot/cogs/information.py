import disnake
from disnake.ext import commands

from utils.grabAPI import GrabAPI
import utils.formatList as formatList
import utils.checkNation as checkNation

from models.serverConfiguration import ServerConfiguration

class Information(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="information", description="Shows nation information")
    async def information(self, inter):
        pass

    @information.sub_command(name="relations", description="Shows your nation's relationships with other nations")
    async def relations(self, inter, target : str = "default"):
        if not target:
            config = await ServerConfiguration.get_or_none(server_name=inter.guild.name, server_id=inter.guild.id)
            if not config or not config.default_nation:
                return await inter.response.send_message(
                    "Provide a nation name or set your default nation with /configure nation")
            target = config.default_nation

        if await checkNation.check_nation(target):
            nation_data = await GrabAPI.post_async('nations', target)

            ally_data = nation_data[0]['allies']
            enemy_data = nation_data[0]['enemies']

            embed_variable = disnake.Embed(title=f"{nation_data[0]['name']} Relations | 🤝", description="", color=0xffffff)
            embed_variable.add_field(name="Alliances", value=f"```{formatList.format_list(ally_data)}```", inline=True)
            embed_variable.add_field(name="Enemies", value=f"```{formatList.format_list(enemy_data)}```", inline=True)

            embed_variable.set_footer(text=f"{"v3.0"} Programmed by CreVolve", icon_url="https://i.imgur.com/jdxtHVd.jpeg")

            await inter.response.send_message(embed=embed_variable)
        else:
            await inter.response.send_message(f"**{target}** is not a real nation")

def setup(bot):
    bot.add_cog(Information(bot))