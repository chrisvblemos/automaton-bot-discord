from bot import bot
from config import bot_config
from discord.ext import commands

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure):
        await ctx.send(f"Comandos só podem ser usados em <#{bot_config.listen_channel_id}>.")