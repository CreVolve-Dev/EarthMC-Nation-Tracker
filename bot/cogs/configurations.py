import disnake
from disnake.ext import commands
import utils.updateConfigurations as updateConfigurations
import utils.checkNation as checkNation

def status_string(value):
    """Returns a status string based on truthiness of value."""
    return "ACTIVE ✅" if value not in [None, "None", False, "False"] else "FALSE ❌"

def mention_or_none(obj):
    """Returns the mention of a Discord object or 'NONE'."""
    return obj.mention if obj else "NONE"

class Configurations(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="configure", description="Commands related to setting configurations")
    async def configure(self, inter : disnake.GuildCommandInteraction):
        pass

    @configure.sub_command(name="nation", description="Set your server's nation. This is used for majority of commands.")
    @commands.has_guild_permissions(manage_guild=True)
    async def nation(self, inter: disnake.GuildCommandInteraction, target : str):
        if checkNation.check_nation(target):
            updateConfigurations.update_configuration(context=inter, default_nation=target, tracked_nations=target)
            await inter.response.send_message(f"**{target}** is now the nation of this server")
        else:
            await inter.response.send_message(f"**{target}** is not a real nation")

    @configure.sub_command(name="settings", description="See your server's configuration settings")
    @commands.has_guild_permissions(manage_guild=True)
    async def settings(self, inter : disnake.GuildCommandInteraction):
        json_data = updateConfigurations.load_server_config(inter.guild.id)

        if not json_data:
            json_data = {}

        # Notifications
        notification_status = status_string(json_data.get("notifications_status"))
        notification_channel = mention_or_none(
            inter.guild.get_channel(json_data.get("notifications_channel"))
        )

        # Roles
        citizen_role = mention_or_none(
            inter.guild.get_role(json_data.get("citizen_role"))
        )
        foreign_role = mention_or_none(
            inter.guild.get_role(json_data.get("foreign_role"))
        )

        # Online Embed
        embed_active = status_string(json_data.get("embed_message"))
        embed_channel = mention_or_none(
            inter.guild.get_channel(json_data.get("embed_channel"))
        )

        # Verifications
        verified_checkup = status_string(json_data.get("verified_checkup"))
        give_verified_role = status_string(json_data.get("give_verified_role"))

        # Tracked Nations
        tracked_nations = json_data.get("tracked_nations", [])
        # If it's a string or None, treat as empty
        if not isinstance(tracked_nations, list):
            tracked_nations = []
        tracked_nations_str = (
            f"```{"\n".join(f"- {nation}" for nation in tracked_nations)}```"
            if tracked_nations else "```None```"
        )

        embed_variable = disnake.Embed(
            title=f'"{inter.guild.name}" Configuration Settings | ⚙️',
            description="",
            color=0xffffff
        )
        embed_variable.add_field(
            name="Notifications",
            value=f"Notifications Status: **{notification_status}**\n"
                  f"Notifications Channel: **{notification_channel}**",
            inline=False
        )
        embed_variable.add_field(
            name="Roles",
            value=f"Citizen Role: **{citizen_role}**\n"
                  f"Foreigner Role: **{foreign_role}**",
            inline=False
        )
        embed_variable.add_field(
            name="Online Embed",
            value=f"Embed Active: **{embed_active}**\n"
                  f"Embed Channel: **{embed_channel}**",
            inline=False
        )
        embed_variable.add_field(
            name="Verifications",
            value=f"Verified Checkup: **{verified_checkup}**\n"
                  f"Give Verified Role: **{give_verified_role}**",
            inline=False
        )
        embed_variable.add_field(
            name="Tracked Nations",
            value=tracked_nations_str,
            inline=False
        )

        embed_variable.set_footer(
            text="v3.0 Programmed by CreVolve",
            icon_url="https://i.imgur.com/jdxtHVd.jpeg"
        )

        await inter.response.send_message(embed=embed_variable)

def setup(bot):
    bot.add_cog(Configurations(bot))