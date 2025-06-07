import disnake
from disnake.ext import commands

import os
import constants
import json
from utils.grabAPI import GrabAPI
import utils.checkNation as checkNation

from models.serverConfiguration import ServerConfiguration
from models.nationData import Nation, Town, Citizen

from bot.models.nationData import Town

notif_types = commands.option_enum({"Citizens": "citizens", "Towns": "towns", "All": "all"})

class Notifications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="notifications", description="Commands related to the notifications feature")
    async def notifications(self, inter : disnake.GuildCommandInteraction):
        pass

    @notifications.sub_command(name="channel", description="Set the notifications channel for updated info on your nation")
    @commands.has_guild_permissions(manage_guild=True)
    async def notifications_channel(self, inter : disnake.GuildCommandInteraction, channel: disnake.TextChannel, types: notif_types = "all"):
        if channel.guild.id != inter.guild.id:
            return await inter.response.send_message("The channel you provided is not in this server")

        if types == "all":
            await ServerConfiguration.update_or_create(server_name=inter.guild.name, server_id=inter.guild.id, defaults={"player_updates_channel": channel.id, "town_updates_channel": channel.id})
        elif types == "citizens":
            await ServerConfiguration.update_or_create(server_name=inter.guild.name, server_id=inter.guild.id, defaults={"player_updates_channel": channel.id})
        elif types == "towns":
            await ServerConfiguration.update_or_create(server_name=inter.guild.name, server_id=inter.guild.id, defaults={"town_updates_channel": channel.id})
        await inter.response.send_message(f"Updated **{types}** notifications channel to **{channel.mention}**")
        print(f"Guild {inter.guild.id} has updated notifications channel to {channel.mention}")

    @notifications.sub_command(name="status", description="Turn on or off notifications for updated info on your nation")
    @commands.has_guild_permissions(manage_guild=True)
    async def notifications_status(self, inter : disnake.GuildCommandInteraction, status : bool, types: notif_types = "all"):
        if types == "all":
            await ServerConfiguration.update_or_create(server_name=inter.guild.name, server_id=inter.guild.id, defaults={"player_updates_status": status, "town_updates_status": status})
        elif types == "citizens":
            await ServerConfiguration.update_or_create(server_name=inter.guild.name, server_id=inter.guild.id, defaults={"player_updates_status": status})
        elif types == "towns":
            await ServerConfiguration.update_or_create(server_name=inter.guild.name, server_id=inter.guild.id, defaults={"town_updates_status": status})
        await inter.response.send_message(f"Set **{types}** notifications to **{status}**")
        print(f"Guild {inter.guild.id} has updated notifications status {status}")

    @notifications.sub_command(name="add", description="Add another nation to your notifications")
    @commands.has_guild_permissions(manage_guild=True)
    async def add_target(self, inter: disnake.GuildCommandInteraction, target: str = None, types: notif_types = "all"):
        if not target:
            config = await ServerConfiguration.get_or_none(server_name=inter.guild.name, server_id=inter.guild.id)
            if not config or not config.default_nation:
                return await inter.response.send_message("Provide a nation name or set your default nation with /configure nation")
            target = config.default_nation

        if not checkNation.check_nation(target):
            return await inter.response.send_message(f"**{target}** is not a real nation")

        nation_data = await Nation.get_or_none(name=target.lower())
        server_configuration, created = await ServerConfiguration.update_or_create(server_name=inter.guild.name, server_id=inter.guild.id)
        if not nation_data:
            nation_api = await GrabAPI.post_async('/nations', target)
            nation_data = await Nation.create(name=target.lower(), player_updates_audience=[inter.guild.id] if types in ("all", "citizens") else [], town_updates_audience=[inter.guild.id] if types in ("all", "towns") else [])
            if types in ("all", "citizens"):
                server_configuration.player_updates_tracking.append(target)
            if types in ("all", "towns"):
                server_configuration.town_updates_tracking.append(target)
            await server_configuration.save()
            await inter.response.send_message(f"Added **{target}** to **{types}** notifications")
            for resident in nation_api[0]["residents"]:
                await Citizen.update_or_create(name=resident["name"], nation=nation_data)
            for town in nation_api[0]["towns"]:
                await Town.update_or_create(name=town["name"], nation=nation_data)
            return
        else:
            if types in ("all", "citizens") and inter.guild.id not in nation_data.player_updates_audience:
                nation_data.player_updates_audience.append(inter.guild.id)
            if types in ("all", "towns") and inter.guild.id not in nation_data.town_updates_audience:
                nation_data.town_updates_audience.append(inter.guild.id)
            await nation_data.save()

        return await inter.response.send_message(f"Added **{target}** to **{types}** notifications")

    @notifications.sub_command(name="remove", description="Remove a nation from your notifications")
    @commands.has_guild_permissions(manage_guild=True)
    async def remove_target(self, inter : disnake.GuildCommandInteraction, target: str = None, types: notif_types = "all"):
        if not target:
            config = await ServerConfiguration.get_or_none(server_name=inter.guild.name, server_id=inter.guild.id)
            if not config or not config.default_nation:
                return await inter.response.send_message("Provide a nation name or set your default nation with /configure nation")
            target = config.default_nation

        server_configuration= await ServerConfiguration.get_or_none(server_name=inter.guild.name, server_id=inter.guild.id)
        nation_data = await Nation.get_or_none(name=target.lower())
        if not nation_data:
            return await inter.response.send_messag(f"You are not tracking **{target}**")

        if not server_configuration:
            return await inter.response.send_message("You are not currently tracking any nations")

        if types in ("all", "citizens"):
            if target not in server_configuration.player_updates_tracking:
                return await inter.response.send_message(f"**{target}** is not in **{types}** notifications")
            server_configuration.player_updates_tracking.remove(target)
            nation_data.player_updates_audience.remove(inter.guild.id)
        if types in ("all", "towns"):
            if target not in server_configuration.town_updates_tracking:
                return await inter.response.send_message(f"**{target}** is not in **{types}** notifications")
            server_configuration.town_updates_tracking.remove(target)
            nation_data.town_updates_audience.remove(inter.guild.id)
        await server_configuration.save()
        await nation_data.save()

        await inter.response.send_message(f"Removed **{target}** from **{types}** notifications")
        return

def setup(bot):
    bot.add_cog(Notifications(bot))