from bot import bot
from discord.ext import commands
from utils import load_info_commands

@bot.command()
async def info(ctx: commands.Context, topic: str = None):
    info_commands = load_info_commands()
    
    if topic is None:
        available = ", ".join(info_commands.keys())
        await ctx.send(f"Tópicos disponíveis: {available}")
        return
    
    topic = topic.lower()
    response = info_commands.get(topic)
    if response:
        await ctx.send(response)
    else:
        await ctx.send(f"Tópico `{topic}` não encontrado. Use `!info` para ver os tópicos disponíveis.")
    