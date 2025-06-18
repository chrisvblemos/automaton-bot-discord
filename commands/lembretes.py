import asyncio
from discord import AllowedMentions
from discord.ext import commands
from config import bot_config
from bot import bot

active_reminders: dict[int, list[asyncio.Task]] = {}

@bot.command(name="lembrete", aliases=["remindme", "reminder"])
async def lembrete(ctx : commands.Context, tempo: str = None, *, mensagem: str = None):
    user_id = ctx.author.id
    
    if not tempo or not mensagem:
        await ctx.send("Uso: `!lembrete <tempo> <mensagem>`\nExemplo: `!lembrete 10m Levantar da cadeira`")
        return
    
    unidades = {"s": 1, "m": 60, "h": 3600}
    try:
        segundos = int(tempo[:-1]) * unidades[tempo[-1]]
    except:
        await ctx.send("Formato inválido. Use `10s`, `5m`, ou `1h`, por exemplo.")
        return
    
    if segundos > bot_config.max_reminder_seconds:
        await ctx.send(f"⏰ O tempo máximo permitido para lembretes é {bot_config.max_reminder_seconds}s.")
        return
    
    if user_id not in active_reminders:
        active_reminders[user_id] = []
    if len(active_reminders[user_id]) >= bot_config.max_reminders_per_user:
        await ctx.send(f"🚫 Você já tem {bot_config.max_reminders_per_user} lembretes ativos. Aguarde ou cancele um.")
        return

    await ctx.send(f"🔔 Lembrete agendado para {ctx.author.mention} em {tempo}.")
    
    async def lembrete_task():
        await asyncio.sleep(segundos)
        await ctx.send(
            f"🔔 {ctx.author.mention}, lembrete: {mensagem}",
            allowed_mentions=AllowedMentions(everyone=False, roles=False, users=False)
        )
        active_reminders[user_id].remove(task)
        if not active_reminders[user_id]:
            del active_reminders[user_id]

    task = asyncio.create_task(lembrete_task())
    active_reminders[user_id].append(task)
    
@bot.command(name="meuslembretes", aliases=["myreminders", "reminders", "lembretes"])
async def meus_lembretes(ctx: commands.Context):
    user_id = ctx.author.id
    count = len(active_reminders.get(user_id, []))
    if count == 0:
        await ctx.send("🔕 Você não tem lembretes ativos.")
    else:
        await ctx.send(f"📌 Você tem {count} lembrete(s) ativo(s).")
        
@bot.command(name="cancelarlembretes", aliases=["cancelarlembrete", "clearlembretes", "clearreminders", "deletereminders"])
async def cancelar_lembretes(ctx: commands.Context):
    user_id = ctx.author.id
    reminders = active_reminders.get(user_id, [])

    if not reminders:
        await ctx.send("❌ Você não tem lembretes ativos para cancelar.")
        return

    for task in reminders:
        task.cancel()
    del active_reminders[user_id]

    await ctx.send(f"🗑️ {len(reminders)} lembrete(s) cancelado(s) com sucesso.")