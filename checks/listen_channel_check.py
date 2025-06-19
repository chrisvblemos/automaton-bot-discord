from bot import bot
from config import bot_config
from discord.ext import commands

@bot.check
async def only_in_command_channel(ctx: commands.Context):
    listen_channel_id = bot_config.listen_channel_id
    if (listen_channel_id > 0):
        return ctx.channel.id == bot_config.listen_channel_id
    else:
        return True