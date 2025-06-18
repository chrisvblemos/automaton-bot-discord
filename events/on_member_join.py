import discord
from config import bot_config
from bot import bot

@bot.event 
async def on_member_join(member: discord.Member) -> None:
    channel_id = bot_config.welcome_channel_id
    
    if channel_id:
        welcome_channel = bot.get_channel(channel_id)
        if welcome_channel:
            await welcome_channel.send(f"Bem-vindo, camarada {member.mention}!")
        else:
            print(f"[ERRO] Channel ID {channel_id} não encontrado no servidor {member.guild.name}.")
    else:
        print(f"[ERRO] Canal de boas-vindas não foi setado em config.json.")