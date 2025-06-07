import disnake
from disnake.ext import commands

import constants

import utils.checkNation as checkNation

from models.serverConfiguration import ServerConfiguration
from models.nationData import Nation

class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="embed", description="commands related to embeds", default_member_permissions=disnake.Permissions(manage_guild=True))
    async def embed(self, inter : disnake.GuildCommandInteraction):
        pass

    @embed.sub_command(name="add", description="Creates a new online embed")
    @commands.has_guild_permissions(manage_guild=True)
    async def add(self, inter : disnake.GuildCommandInteraction, target : str = None):
        if not checkNation.check_nation(target):
            return await inter.response.send_message(f"**{target}** is not a real nation")

        if not target:
            config = await ServerConfiguration.get_or_none(server_name=inter.guild.name, server_id=inter.guild.id)
            if not config or not config.default_nation:
                return await inter.response.send_message("Provide a nation name or set your default nation with /configure nation")
            target = config.default_nation

        nations = await Nation.all()
        for nation in nations:
            if inter.guild.id in nation.embed_audience:
                nation.embed_audience.remove(inter.guild.id)
                await nation.save()

        await inter.response.send_message(f"Online embed set to **{target}**. A temporary message has been made that will become the embed.", ephemeral=True)
        set_message = await inter.followup.send("This is a placeholder until an online embed is ready...")

        await ServerConfiguration.update_or_create(server_name=inter.guild.name, server_id=inter.guild.id, defaults={"online_embed_channel": set_message.channel.id, "online_embed_message": set_message.id})

        nation_data = await Nation.get_or_none(name=target.lower())
        if not nation_data:
            await Nation.create(name=target.lower(), embed_audience=[inter.guild.id])
        else:
            nation_data.embed_audience.append(inter.guild.id)
            await nation_data.save()

    @embed.sub_command(name="remove", description="Removes your current online embed")
    @commands.has_guild_permissions(manage_guild=True)
    async def remove(self, inter : disnake.GuildCommandInteraction):
        for nation in await Nation.all():
            if inter.guild.id == nation.embed_audience:
                nation.embed_audience.remove(inter.guild.id)
                await nation.save()
                await ServerConfiguration.update_or_create(server_name=inter.guild.name, server_id=inter.guild.id, defaults={"online_embed_channel": None, "online_embed_message": None})
                await inter.response.send_message(f"Removed your online embed")
            else:
                await inter.response.send_message(f"You don't have an online embed")

def setup(bot):
    bot.add_cog(Embeds(bot))