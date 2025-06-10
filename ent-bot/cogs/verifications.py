import disnake
from disnake.ext import commands

import utils.giveRole as giveRole
from utils.grabAPI import GrabAPI
from utils.grabObjects import GrabObjects

from models.serverConfiguration import ServerConfiguration

async def nickname_verified(user : disnake.Member, minecraft_username):
    town = await GrabAPI.post_async('players', minecraft_username)
    nickname = f"{minecraft_username} | {town[0]["town"]["name"]}"
    try:
        await user.edit(nick=nickname)
    except disnake.errors.Forbidden:
        pass

class Verify(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="verify", description="Related to verification")
    async def verify(self, inter : disnake.GuildCommandInteraction):
        pass

    @verify.sub_command(name="give-verified-role", description="Toggle whether members get your citizen role when verified")
    @commands.has_guild_permissions(manage_guild=True)
    async def give_verified_role(self, inter : disnake.GuildCommandInteraction, status : bool):
        await ServerConfiguration.update_or_create(server_name=inter.guild.name, server_id=inter.guild.id, defaults={"give_verified_role": status})
        await inter.response.send_message(f"Updated give_verified_role to **{status}**")

    @verify.sub_command(name="verified-checkup", description="Automatically remove people who have left the server from verifications")
    @commands.has_guild_permissions(manage_guild=True)
    async def verified_checkup(self, inter : disnake.GuildCommandInteraction, status : bool):
        await ServerConfiguration.update_or_create(server_name=inter.guild.name, server_id=inter.guild.id, defaults={"verified_checkup": status})
        await inter.response.send_message(f"Updated verified_checkup to **{status}**")

    @verify.sub_command(name="nickname-verified", description="Toggle whether verified members get their minecraft username as their nickname")
    @commands.has_guild_permissions(manage_guild=True)
    async def nickname_verified(self, inter : disnake.GuildCommandInteraction, status : bool):
        await ServerConfiguration.update_or_create(server_name=inter.guild.name, server_id=inter.guild.id, defaults={"nickname_verified": status})
        await inter.response.send_message(f"Updated nickname_verified to **{status}**")

    @verify.sub_command(name="online-verify-check", description="Check if a user's minecraft username is a citizen of your nation before verifying")
    @commands.has_guild_permissions(manage_guild=True)
    async def online_verify_check(self, inter : disnake.GuildCommandInteraction, status : bool):
        server_data = await ServerConfiguration.get_or_none(server_name=inter.guild.name, server_id=inter.guild.id)
        if server_data is not None and server_data.default_nation is not None:
            await ServerConfiguration.update_or_create(server_name=inter.guild.name, server_id=inter.guild.id, defaults={"online_verify_check": status})
            await inter.response.send_message(f"Updated online_verify_check to **{status}**")
        else:
            await inter.response.send_message("You need to set a default nation first with /configure nation")

    @verify.sub_command(name="add", description="Verify a citizen of your nation")
    @commands.has_guild_permissions(moderate_members=True)
    async def add(self, inter : disnake.GuildCommandInteraction, member: disnake.User, minecraft_username : str):
        object_grabber = GrabObjects(bot=self)
        server_data = await ServerConfiguration.get_or_none(server_name=inter.guild.name, server_id=inter.guild.id)

        possible_upload_data = {"discord": member.id, "minecraft": minecraft_username}
        if server_data is None:
            await ServerConfiguration.create(server_name=inter.guild.name, server_id=inter.guild.id, verified_citizens=[possible_upload_data])
        else:
            for entry in server_data.verified_citizens:
                if member.id == entry["discord"]:
                    return await inter.response.send_message(f"You have already verified the Discord user: **{member.mention}**")
                if minecraft_username == entry["minecraft"]:
                    return await inter.response.send_message(f"You have already verified the Minecraft user: **{minecraft_username}**")

            if server_data.online_verify_check:
                player_data = await GrabAPI.post_async('players', str(minecraft_username.lower()))
                if not player_data:
                    return await inter.response.send_message(f"**{minecraft_username}** is not a real player")
                if player_data[0]["nation"]["name"] == server_data.default_nation:
                    server_data.verified_citizens.append(possible_upload_data)
                    await server_data.save()
                else:
                    return await inter.response.send_message(f"**{minecraft_username}** is not a citizen of your nation")
            else:
                server_data.verified_citizens.append(possible_upload_data)
                await server_data.save()

            try:
                if server_data.give_verified_role:
                    if not await giveRole.give_role(member.id, inter, server_data.citizen_role):
                        server_data.citizen_role = None
                        server_data.give_verified_role = False
                        await server_data.save()
                        return await inter.response.send_message(f"Verified **{member.mention}** with link to **{minecraft_username}** but couldn't find the Citizen Role to add.")
            except KeyError:
                pass

            if server_data.nickname_verified:
                server_object = object_grabber.get_guild(inter.guild.id)
                member_to_update = server_object.get_member(member.id)
                await nickname_verified(member_to_update, minecraft_username)

        await inter.response.send_message(f"Verified **{member.mention}** with link to **{minecraft_username}**")

    @verify.sub_command(name="remove", description="Remove a citizen verification")
    @commands.has_guild_permissions(moderate_members=True)
    async def remove(self, inter : disnake.GuildCommandInteraction, member: disnake.User):
        server_data = await ServerConfiguration.get_or_none(server_name=inter.guild.name, server_id=inter.guild.id)
        if server_data is None:
            return await inter.response.send_message(f"**{member.mention}** was not verified")
        for citizen in server_data.verified_citizens:
            if citizen["discord"] == member.id:
                ServerConfiguration.verified_citizens.remove(citizen)
                await ServerConfiguration.save()
                return await inter.response.send_message(f"Removed **{member.mention}** from verification")

        await inter.response.send_message(f"**{member.mention}** was not verified")

    @verify.sub_command(name="check", description="Check if someone is verified as a citizen")
    async def check(self, inter : disnake.GuildCommandInteraction, member: disnake.User):
        server_data = await ServerConfiguration.get_or_none(server_name=inter.guild.name, server_id=inter.guild.id)
        if server_data is None:
            return await inter.response.send_message(f"**{member.mention}** is not currently verified")

        for citizen in server_data.verified_citizens:
            if member.id == citizen["discord"]:
                return await inter.response.send_message(f"**{member.mention}** is currently verified as **{citizen["minecraft"]}**")

        await inter.response.send_message(f"**{member.mention}** is not currently verified")

def setup(bot):
    bot.add_cog(Verify(bot))