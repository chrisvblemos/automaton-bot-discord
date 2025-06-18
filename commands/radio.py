from bot import bot
from config import bot_config
from discord.ext import commands
from discord import VoiceChannel
import json
import discord
import aiohttp

@bot.command(name="tocarradio", aliases=["radio", "playradio", "stream", "music"])
async def play_radio(ctx: commands.Context, source: str = None, radio_channel: str = None) -> None:
    voice_channel: VoiceChannel = ctx.author.voice.channel if ctx.author.voice else None    
    if not voice_channel:
        await ctx.send(f"Você precisa estar em um canal de voz para eu tocar a rádio {ctx.author.mention}.")
        return
    
    estacoes_radio = {}
    with open("./radios.json", "r") as f:
        estacoes_radio = json.load(f)
        print(estacoes_radio)
    
    if source in estacoes_radio and radio_channel is None:
        url = estacoes_radio[source]
        pls_url = f"{url}.pls"
        radio_channel = url.split("/")[-1]
    
    pls_url = f"https://somafm.com/{radio_channel}.pls"
        
    async with aiohttp.ClientSession() as session:
        async with session.get(pls_url) as resp:
            if resp.status != 200:
                await ctx.send(f"Não consegui acessar a rádio: {radio_channel}!")
                return
            pls_text = await resp.text()
            
    stream_url = None
    for line in pls_text.splitlines():
        if line.startswith("File1="):
            stream_url = line.split("=", 1)[1].strip()
            break
        
    if not stream_url:
        await ctx.send(f"Não consegui acessar a rádio: {radio_channel}!")
        return
    
    user_channel = ctx.author.voice.channel
    user_mention = ctx.author.mention
    if not user_channel:
        await ctx.send(f"Você precisa estar em um canal de voz {user_mention} para que eu toque uma estação de rádio.")
    
    vc = ctx.voice_client
    if vc:
        current_channel = vc.channel
        if current_channel and current_channel != user_channel:
            
            roles = [r.name for r in ctx.author.roles]
            if "ADMIN" not in roles and "MODERADORES" not in roles:
                await ctx.send(f"Já estou tocando rádio no canal {current_channel.mention}. Apenas superiores podem forçar a troca de canal.")
                return
            await ctx.send(f"{user_mention} forçou a troca de canal do rádio para {user_channel.mention}.")
            vc.move_to(user_channel)
            return
        if vc.is_playing():
            await ctx.send(f"{user_mention} solicitou a troca da estação de rádio para {radio_channel} no canal {current_channel.mention}")
            vc.stop()
    else:
        vc = await user_channel.connect()
    
    try:
        source = discord.FFmpegPCMAudio(
            stream_url,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn -ar 48000 -ac 2"
        )
        vc.play(discord.PCMVolumeTransformer(source, volume=0.1))
        await ctx.send(f"Tocando estação de rádio **{radio_channel}** do SomaFM no canal {user_channel.mention}!")
    except Exception as e:
        await ctx.send(f"Falha: Não consegui tocar a estação de rádio informada.")
        print(f"Falha ao tocar a estação de rádio {radio_channel}, solicitado pelo {user_mention} no canal {user_channel.mention}.")

@bot.command(name="pararradio", aliases=["stopradio", "stopmusic", "pararmusica"])
async def parar_radio(ctx: commands.Context):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Parando rádio.")
    else:
        await ctx.send("Não estou tocando nenhuma rádio.")