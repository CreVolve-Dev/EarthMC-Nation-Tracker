import disnake
from disnake.ext import commands
import utils.checkNation as checkNation

from models.serverConfiguration import ServerConfiguration

from utils.grabObjects import GrabObjects

from Paginator import CreatePaginator

import countryflag

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
        if await checkNation.check_nation(target):
            await ServerConfiguration.update_or_create(server_name=inter.guild.name, server_id=inter.guild.id, defaults={"default_nation": target})
            server_config = await ServerConfiguration.get(server_name=inter.guild.name, server_id=inter.guild.id)
            server_config.player_updates_tracking.append(target)
            server_config.town_updates_tracking.append(target)
            await server_config.save()
            await inter.response.send_message(f"Set your default nation to **{target}**")
        else:
            await inter.response.send_message(f"**{target}** is not a real nation")

    @configure.sub_command(name="settings", description="See your server's configuration settings")
    @commands.has_guild_permissions(manage_guild=True)
    async def settings(self, inter : disnake.GuildCommandInteraction):
        server_data = await ServerConfiguration.get_or_none(server_name=inter.guild.name, server_id=inter.guild.id)
        guild_object = await GrabObjects.get_guild(self, inter.guild.id)

        # Notifications
        player_notification_status = status_string(server_data.player_updates_status)
        player_notification_channel = mention_or_none(await GrabObjects.get_channel(self, server_data.player_updates_channel))
        town_notification_status = status_string(server_data.town_updates_status)
        town_notification_channel = mention_or_none(await GrabObjects.get_channel(self, server_data.town_updates_channel))

        # Roles
        citizen_role = mention_or_none(await GrabObjects.get_role(guild_object, server_data.citizen_role))
        foreign_role = mention_or_none(await GrabObjects.get_role(guild_object, server_data.foreigner_role))

        # Online Embed
        embed_active = status_string(await GrabObjects.get_channel(self, server_data.online_embed_channel))
        embed_channel = mention_or_none(await GrabObjects.get_channel(self, server_data.online_embed_channel))

        # Verifications
        verified_checkup = status_string(server_data.verified_checkup)
        give_verified_role = status_string(server_data.give_verified_role)
        online_verify_check = status_string(server_data.online_verify_check)
        nickname_verified = status_string(server_data.nickname_verified)

        # Tracked Nations
        tracked_player_nations = server_data.player_updates_tracking
        if not isinstance(tracked_player_nations, list):
            tracked_player_nations = []
        tracked_player_nations_str = (
            f"```{"\n".join(f"- {nation}" for nation in tracked_player_nations)}```"
            if tracked_player_nations else "```None```"
        )

        tracked_town_nations = server_data.town_updates_tracking
        if not isinstance(tracked_town_nations, list):
            tracked_town_nations = []
        tracked_town_nations_str = (
            f"```{"\n".join(f"- {nation}" for nation in tracked_town_nations)}```"
            if tracked_town_nations else "```None```"
        )

        try:
            flag = countryflag.get_flag([server_data.default_nation])
        except:
            flag = None

        embed_one = disnake.Embed(
            title=f'"{inter.guild.name}" Configuration Settings PG. 1 | ⚙️',
            description="",
            color=0xffffff
        )

        embed_one.add_field(
            name="Nation",
            value=f"You have chosen: **{server_data.default_nation}** {flag if flag else ''}\n",
            inline=False
        )

        embed_one.add_field(
            name="Roles",
            value=f"Citizen Role: **{citizen_role}**\n"
                  f"Foreigner Role: **{foreign_role}**",
            inline=False
        )
        embed_one.add_field(
            name="Online Embed",
            value=f"Embed Active: **{embed_active}**\n"
                  f"Embed Channel: **{embed_channel}**",
            inline=False
        )
        embed_one.add_field(
            name="Verifications",
            value=f"Verified Checkup: **{verified_checkup}**\n"
                  f"Give Verified Role: **{give_verified_role}**\n"
                  f"Online Verify Check: **{online_verify_check}**\n"
                  f"Nickname Verified: **{nickname_verified}**",
            inline=False
        )

        embed_one.set_footer(
            text="v3.0 Programmed by CreVolve",
            icon_url="https://i.imgur.com/jdxtHVd.jpeg"
        )

        embed_two = disnake.Embed(
            title=f'"{inter.guild.name}" Configuration Settings PG. 2 | ⚙️',
            description="",
            color=0xffffff
        )

        embed_two.add_field(
            name="Player Notifications",
            value=f"Status: **{player_notification_status}**\n"
                  f"Channel: **{player_notification_channel}**\n",
            inline=False
        )

        embed_two.add_field(
            name="Tracked Nations for Player Notifications",
            value=tracked_player_nations_str,
        )

        embed_two.add_field(
            name="Town Notifications",
            value=f"Status: **{town_notification_status}**\n"
                  f"Channel: **{town_notification_channel}**\n",
            inline=False
        )

        embed_two.add_field(
            name="Tracked Nations for Town Notifications",
            value=tracked_town_nations_str,
        )

        embed_two.set_footer(
            text="v3.0 Programmed by CreVolve",
            icon_url="https://i.imgur.com/jdxtHVd.jpeg"
        )

        embeds=[
            embed_one,
            embed_two
        ]

        timeout = 60.0
        await inter.response.send_message(embed=embeds[0], view=CreatePaginator(embeds, inter.author.id, timeout))

def setup(bot):
    bot.add_cog(Configurations(bot))