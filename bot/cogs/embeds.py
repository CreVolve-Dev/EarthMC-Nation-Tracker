import disnake
from disnake.ext import commands

import json
import constants
import os

import utils.postAPI as postAPI
import utils.updateConfigurations as updateConfigurations
import utils.checkNation as checkNation

class Embeds(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="embed", description="commands related to embeds", default_member_permissions=disnake.Permissions(manage_guild=True))
    async def embed(self, inter : disnake.GuildCommandInteraction):
        pass

    @embed.sub_command(name="add", description="Creates a new online embed")
    async def add(self, inter : disnake.GuildCommandInteraction, target : str = "default"):
        if target == "default":
            target = updateConfigurations.load_server_config(inter.guild.id).get("default_nation") if updateConfigurations.load_server_config(inter.guild.id).get("default_nation") else "default"
            if target == "default":
                await inter.response.send_message("Provide a nation name or set your default nation with /configure nation")

        if checkNation.check_nation(target):
            for filename in os.listdir(constants.GROUP_STORAGE_DATA):
                path = os.path.join(constants.GROUP_STORAGE_DATA, filename)
                with open(path, "r+") as f:
                    data = json.load(f)
                    if inter.guild.id in data.get("embed_audience", []):
                        data["embed_audience"].remove(inter.guild.id)
                        f.seek(0)
                        json.dump(data, f, indent=4)
                        f.truncate()

            path = os.path.join(constants.GROUP_STORAGE_DATA, f"{target}.json")
            if os.path.exists(path):
                with open(path, "r+") as f:
                    data = json.load(f)
                    if inter.guild.id in data.get("embed_audience", []):
                        await inter.response.send_message(f"Your online embed is already set to **{target}**")
                    data["embed_audience"].append(inter.guild.id)
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()
            else:
                target_data = postAPI.post_api_data('/nations', target)[0]
                residents = [r['name'] for r in target_data['residents']]
                data = {
                    "target": target,
                    "residents": residents,
                    "audience": [],
                    "embed_audience": [inter.guild.id]
                }
                with open(path, "w") as f:
                    json.dump(data, f, indent=4)

            await inter.response.send_message(f"Online embed set to **{target}**. A temporary message has been made that will become the embed.", ephemeral=True)
            set_message = await inter.followup.send("This is a placeholder until an online embed is ready...")
            updateConfigurations.update_configuration(inter, embed_message=set_message.id, embed_channel=set_message.channel.id)
        else:
            await inter.response.send_message(f"**{target}** is not a real nation")

    @embed.sub_command(name="remove", description="Removes your current online embed")
    async def remove(self, inter : disnake.GuildCommandInteraction):
        for filename in os.listdir(constants.GROUP_STORAGE_DATA):
            path = os.path.join(constants.GROUP_STORAGE_DATA, filename)
            with open(path, "r+") as f:
                data = json.load(f)
                if inter.guild.id in data.get("embed_audience", []):
                    data["embed_audience"].remove(inter.guild.id)
                    f.seek(0)
                    json.dump(data, f, indent=4)
                    f.truncate()

                    updateConfigurations.update_configuration(inter, embed_message=None, embed_channel=None)
                    await inter.response.send_message(f"Removed your online embed")

                else:
                    await inter.response.send_message(f"You don't have an online embed")

def setup(bot):
    bot.add_cog(Embeds(bot))