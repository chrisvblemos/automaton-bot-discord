from bot import bot

@bot.event
async def on_ready() -> None:
    print(f"{bot.user} inicializado com sucesso!")