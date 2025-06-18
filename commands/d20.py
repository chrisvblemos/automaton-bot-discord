from bot import bot
from discord.ext import commands
import random

@bot.command(name="d20")
async def roll_d20(ctx: commands.Context) -> None:
    result = random.randint(1,20)
    
    if result == 20:
        await ctx.send(f"{ctx.author.mention} rolou **20**! Nice!")
    elif result == 1:
        await ctx.send(f"{ctx.author.mention} rolou **1**, sinto muito.")
    else:
        await ctx.send(f"{ctx.author.mention} rolou **{result}**!")