import disnake
from disnake.ext import commands
import asyncio
import os

import utils.checkDirectory as checkDirectory

asyncio.set_event_loop(asyncio.new_event_loop())

BOT_TOKEN = os.getenv('BOT_TOKEN')

intents = disnake.Intents.all()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    print('Bot has signed in successfully and is ready to go!')

@bot.event
async def on_slash_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("That command does not exist.")
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("You don't have permission to do that.")
    else:
        await ctx.send("An unexpected error has occurred. Try again later.")
        print(error)

bot.load_extension("cogs.configurations")
bot.load_extension("cogs.information")
bot.load_extension("cogs.notifications")
bot.load_extension("cogs.roles")
bot.load_extension("cogs.verifications")
bot.load_extension("cogs.embeds")

bot.load_extension("background_tasks.notificationLoop")
bot.load_extension("background_tasks.onlineEmbed")
bot.load_extension("background_tasks.verifyCheckup")

checkDirectory.check_directory("./api_storage")
checkDirectory.check_directory("./server_configurations")

bot.run(BOT_TOKEN)