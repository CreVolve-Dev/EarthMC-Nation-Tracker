import disnake
from disnake.ext import commands

from models.serverConfiguration import ServerConfiguration

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="roles", description="Manage roles", default_member_permissions=disnake.Permissions(manage_guild=True))
    async def roles(self, inter):
        pass

    @roles.sub_command(name="set-citizen", description="Set the role given to citizens of your nation")
    @commands.has_guild_permissions(manage_guild=True)
    async def citizen_role(self, inter: disnake.GuildCommandInteraction, role: disnake.Role):
        await ServerConfiguration.update_or_create(server_name=inter.guild.name, server_id=inter.guild.id, defaults={"citizen_role": role.id})
        await inter.response.send_message(f"Updated citizen role to **{role.mention}**")
        print(f"Guild {inter.guild.id} has updated their citizen role to **{role.mention}**")


    @roles.sub_command(name="set-foreign", description="Set the role given to foreigners of your nation")
    @commands.has_guild_permissions(manage_guild=True)
    async def foreign_role(self, inter: disnake.GuildCommandInteraction, role: disnake.Role):
        await ServerConfiguration.update_or_create(server_name=inter.guild.name, server_id=inter.guild.id, defaults={"foreigner_role": role.id})
        await inter.response.send_message(f"Updated foreign role to **{role.mention}**")
        print(f"Guild {inter.guild.id} has updated their foreigner role to {role.mention}")

def setup(bot):
    bot.add_cog(Roles(bot))