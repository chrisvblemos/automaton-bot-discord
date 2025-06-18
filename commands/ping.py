from bot import bot
from discord.ext import commands

@bot.command()
async def ping(ctx: commands.Context) -> None:
    await ctx.send(f"Pong!")