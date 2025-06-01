import disnake
from disnake.ext import commands

import os
import constants
import json
import utils.postAPI as postAPI
import utils.checkNation as checkNation

import utils.updateConfigurations as updateConfigurations

class Notifications(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="notifications", description="Commands related to the notifications feature", default_member_permissions=disnake.Permissions(manage_guild=True))
    async def notifications(self, inter : disnake.GuildCommandInteraction):
        pass

    @notifications.sub_command(name="channel", description="Set the notifications channel for updated info on your nation")
    async def notifications_channel(self, inter : disnake.GuildCommandInteraction, channel: disnake.TextChannel):
        updateConfigurations.update_configuration(context=inter, notifications_channel=channel.id)
        await inter.response.send_message(f"Updated notifications channel to **{channel.mention}**")
        print(f"Guild {inter.guild.id} has updated notifications channel to {channel.mention}")

    @notifications.sub_command(name="status", description="Turn on or off notifications for updated info on your nation")
    async def notifications_status(self, inter : disnake.GuildCommandInteraction, status : bool):
        updateConfigurations.update_configuration(context=inter, notifications_status=status)
        await inter.response.send_message(f"Set notifications to **{status}**")
        print(f"Guild {inter.guild.id} has updated notifications status {status}")

    @notifications.sub_command(name="add", description="Add another nation to add to your notifications")
    async def add_target(self, inter : disnake.GuildCommandInteraction, target : str = None):
        if target is None:
            target = updateConfigurations.load_server_config(inter.guild.id).get("default_nation") if updateConfigurations.load_server_config(inter.guild.id).get("default_nation") else None
            if target is None:
                await inter.response.send_message("Provide a nation name or set your default nation with /configure nation")

        if checkNation.check_nation(target):
            path = os.path.join(constants.GROUP_STORAGE_DATA, f"{target}.json")

            if os.path.exists(path):
                with open(path, "r+") as file:
                    data = json.load(file)
                    if inter.guild.id in data["audience"]:
                        await inter.response.send_message(f"You have already added **{target}** to your notifications")
                    data["audience"].append(inter.guild.id)
                    file.seek(0)
                    json.dump(data, file, indent=4)
                    file.truncate()

            else:
                target_data = postAPI.post_api_data('/nations', target)[0]
                residents = [r['name'] for r in target_data['residents']]
                data = {
                    "target": target,
                    "residents": residents,
                    "audience": [inter.guild.id],
                    "embed_audience": []
                }
                with open(path, "w") as f:
                    json.dump(data, f, indent=4)

            await inter.response.send_message(f"Added **{target}** to your notifications")
            updateConfigurations.update_configuration(context=inter, tracked_nations=target)
        else:
            await inter.response.send_message(f"**{target}** is not a real nation")

    @notifications.sub_command(name="remove", description="Remove a nation from your notifications")
    async def remove_target(self, inter : disnake.GuildCommandInteraction, target: str = "default"):
        path = os.path.join(constants.GROUP_STORAGE_DATA, f"{target}.json")
        if target == "default":
            target = updateConfigurations.load_server_config(inter.guild.id).get("default_nation") if updateConfigurations.load_server_config(inter.guild.id).get("default_nation") else "default"
            if target == "default":
                await inter.response.send_message("Provide a nation name or set your default nation with /configure nation")

        if not os.path.exists(path):
            return False
        with open(path, "r+") as file:
            data = json.load(file)
            if inter.guild.id not in data["audience"]:
                await inter.response.send_message(f"You are not currently tracking **{target}**")
            data["audience"].remove(inter.guild.id)
            if not data["audience"] and not data["embed_audience"]:
                file.close()
                os.remove(path)
            else:
                file.seek(0)
                json.dump(data, file, indent=4)
                file.truncate()

        updateConfigurations.remove_configuration(context=inter, tracked_nations=target)
        await inter.response.send_message(f"Removed **{target}** from your notifications")

def setup(bot):
    bot.add_cog(Notifications(bot))