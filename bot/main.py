import disnake
from disnake.ext import commands
import asyncio
import os
import aiofiles
from tortoise import Tortoise
import logging
import json
from aiofiles.os import listdir
from aiohttp.client_exceptions import ClientError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("Error: BOT_TOKEN environment variable is not set.")

intents = disnake.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)


async def load_database_config():
    async with aiofiles.open("databaseConfig.json", mode="r") as f:
        return json.loads(await f.read())


async def load_extensions(bot):
    for folder in ["cogs", "background_tasks"]:
        try:
            files = await listdir(folder)  # Asynchronous replacement for os.listdir
        except Exception as e:
            logger.error(f"Could not access folder '{folder}': {e}")
            continue

        for file in files:
            if file.endswith(".py") and not file.startswith("__init__"):
                try:
                    bot.load_extension(f"{folder}.{file[:-3]}")  # Synchronous call!
                    logger.info(f"Loaded extension {folder}.{file[:-3]} successfully.")
                except Exception as e:
                    logger.error(f"Failed to load extension {file}: {e}")


async def initialize_database(database_config):
    retries = 3
    for attempt in range(retries):
        try:
            await Tortoise.init(config=database_config)
            await Tortoise.generate_schemas(safe=True)
            logger.info("Database connected successfully!")
            break
        except (ClientError, Exception) as e:
            logger.error(f"Failed to connect to database: {e}")
            if attempt < retries - 1:
                logger.info(f"Retrying database initialization ({attempt + 1}/{retries})...")
                await asyncio.sleep(2)  # Wait before retrying
            else:
                raise RuntimeError("Database initialization failed after retries.")

@bot.event
async def on_ready():
    logger.info("Bot has signed in successfully and is ready to go!")
    print("Bot is online and ready!")


@bot.event
async def on_slash_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("That command does not exist.")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to do that.")
    else:
        try:
            await ctx.send("An unexpected error has occurred. Try again later.")
        except Exception as send_error:
            logger.error(f"Failed to send error message: {send_error}")
        finally:
            logger.error("Error occurred during slash command: %s", error)

async def main():
    loop = asyncio.get_event_loop()  # Get existing loop
    bot.loop = loop  # Explicitly set bot's event loop

    database_config = await load_database_config()
    await initialize_database(database_config)
    await load_extensions(bot)

    await bot.start(BOT_TOKEN)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down gracefully...")


