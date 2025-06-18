from discord.ext import commands
from bot import bot

@bot.command(name="votacao", aliases=["poll"])
async def votacao(ctx: commands.Context, *, pergunta: str = None):
    if not pergunta:
        await ctx.send("Você precisa escrever a pergunta. Exemplo:\n`!votacao Devemos reiniciar o servidor?`")
        return
    
    msg = await ctx.send(f"📊 **{pergunta}**\nVote com ✅ ou ❌")
    await msg.add_reaction("✅")
    await msg.add_reaction("❌")
    
