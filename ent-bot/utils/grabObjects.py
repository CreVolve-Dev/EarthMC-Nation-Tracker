import disnake
import logging

class GrabObjects:
    def __init__(self, bot):
        self.bot = bot

    async def get_channel(self, channel_id: int):
        try:
            return await self.bot.fetch_channel(channel_id)
        except disnake.NotFound:
            logging.error(f"Channel {channel_id} not found.")
            return None
        except disnake.Forbidden:
            logging.error(f"Bot does not have access to channel {channel_id}.")
            return None
        except disnake.HTTPException as e:
            logging.error(f"Error fetching channel {channel_id}: {e}")
            return None

    @staticmethod
    async def get_role(guild: disnake.Guild, role_id: int):
        role = guild.get_role(role_id)
        if role is None:
            logging.error(f"Role {role_id} not found in guild {guild.id}.")
        return role

    @staticmethod
    async def get_message(channel: disnake.TextChannel, message_id: int):
        message = channel.fetch_message(message_id)
        if message is None:
            logging.error(f"Message {message_id} not found in channel {channel.id}.")
        return message

    async def get_guild(self, guild_id: int):
        try:
            return await self.bot.fetch_guild(guild_id)
        except disnake.NotFound:
            logging.error(f"Guild {guild_id} not found.")
            return None
        except disnake.Forbidden:
            logging.error(f"Bot does not have access to guild {guild_id}.")
            return None
        except disnake.HTTPException as e:
            logging.error(f"Error fetching guild {guild_id}: {e}")
            return None

    async def get_user(self, user_id: int):
        try:
            return await self.bot.fetch_user(user_id)
        except disnake.NotFound:
            logging.error(f"User {user_id} not found.")
            return None
        except disnake.Forbidden:
            logging.error(f"Bot does not have access to user {user_id}.")
            return None
        except disnake.HTTPException as e:
            logging.error(f"Error fetching user {user_id}: {e}")
            return None
