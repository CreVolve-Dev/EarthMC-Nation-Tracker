import disnake
from disnake.ext import commands

import utils.updateConfigurations as updateConfigurations
import utils.giveRole as giveRole

true_or_false = commands.option_enum(["True", "False"])

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="verify", description="Related to verification", default_member_permissions=disnake.Permissions(moderate_members=True))
    async def verify(self, inter : disnake.GuildCommandInteraction):
        pass

    @verify.sub_command(name="give-verified-role", description="Toggle whether members get your citizen role when verified")
    async def give_verified_role(self, inter : disnake.GuildCommandInteraction, status: true_or_false):
        updateConfigurations.update_configuration(context=inter, give_verified_role=status)

    @verify.sub_command(name="verified-checkup", description="Automatically remove people who have left the server from verifications")
    async def verified_checkup(self, inter : disnake.GuildCommandInteraction, status: true_or_false):
        updateConfigurations.update_configuration(context=inter, verified_checkup=status)

    @verify.sub_command(name="add", description="Verify a citizen of your nation")
    async def add(self, inter : disnake.GuildCommandInteraction, member: disnake.User, minecraft_username : str):
        server_data = updateConfigurations.load_server_config(inter.guild.id)

        possible_upload_data = {"discord": member.id, "minecraft": minecraft_username}
        if server_data is None:
            updateConfigurations.update_configuration(inter, verified_citizen=possible_upload_data)
        else:
            for entry in server_data["verified_citizens"]:
                if member == entry["discord"]:
                    await inter.response.send_message(f"You have already verified the Discord user: **{member.mention}**")
                    return
                if minecraft_username == entry["minecraft"]:
                    await inter.response.send_message(f"You have already verified the Minecraft user: **{minecraft_username}**")
                    return

            updateConfigurations.update_configuration(inter, verified_citizen=possible_upload_data)

            try:
                if server_data["give_verified_role"] == "True":
                    if not await giveRole.give_role(member, inter, server_data["citizen_role"]):
                        await inter.response.send_message(f"Verified **{member.mention}** with link to **{minecraft_username}** but couldn't find the Citizen Role to add.")

                    await giveRole.give_role(member, inter, server_data["citizen_role"])
            except KeyError:
                pass

        await inter.response.send_message(f"Verified **{member.mention}** with link to **{minecraft_username}**")

    @verify.sub_command(name="remove", description="Remove a citizen verification")
    async def remove(self, inter : disnake.GuildCommandInteraction, member: disnake.User):
        server_data = updateConfigurations.load_server_config(inter.guild.id)

        verified_citizens = server_data["verified_citizens"]
        for i in range(len(verified_citizens)):
            if verified_citizens[i]["discord"] == member.id:
                updateConfigurations.remove_configuration(inter, verified_citizen=verified_citizens[i])
                await inter.response.send_message(f"Removed **{member.mention}** from verification")
                return

        await inter.response.send_message(f"**{member.mention}** was not verified")

    @verify.sub_command(name="check", description="Check if someone is verified as a citizen")
    async def check(self, inter : disnake.GuildCommandInteraction, member: disnake.User):
        server_data = updateConfigurations.load_server_config(inter.guild.id)

        verified_citizens = server_data["verified_citizens"]

        for entry in verified_citizens:
            if member.id == entry["discord"]:
                await inter.response.send_message(f"**{member.mention}** is currently verified as **{entry["minecraft"]}**")

        await inter.response.send_message(f"**{member.mention}** is not currently verified")

def setup(bot):
    bot.add_cog(Verify(bot))