from bot import bot
from discord.ext import commands
import asyncio

@bot.command(name="limpar", aliases=["clear"])
@commands.has_permissions(manage_messages=True)
async def limpar(ctx: commands.Context, quantidade: int = 10):
    if quantidade < 1 or quantidade > 100:
        await ctx.send("Só é possível apagar entre 1 e 100 mensagens.")
        return

    await ctx.channel.purge(limit=quantidade + 1)  # +1 inclui o próprio comando
    msg = await ctx.send(f"{quantidade} mensagens apagadas por {ctx.author.mention}.")
    await asyncio.sleep(3)
    await msg.delete()
    
@bot.command(name="limpartudo", aliases=["clearall"])
@commands.has_permissions(manage_messages=True)
async def limpar_tudo(ctx: commands.Context):
    confirm_msg = await ctx.send("Você está prestes a apagar todas as mensagens desse canal. Tem certeza?")
    await confirm_msg.add_reaction("✅")
    await confirm_msg.add_reaction("❌")
    
    def check(reaction, user):
        return (
            user == ctx.author and
            str(reaction.emoji) in ["✅", "❌"] and
            reaction.message.id == confirm_msg.id
        )
        
    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=15.0, check=check)
    except asyncio.TimeoutError:
        await confirm_msg.edit(content="Tempo esgotado. Ação cancelada.")
        return
    
    if str(reaction.emoji) == "✅":
        await ctx.channel.purge()
        await ctx.send(f"Canal limpo por {ctx.author.mention}.", delete_after=5)
    else:
        await confirm_msg.edit(content="Ação cancelada.")