from bot import bot
from discord import Interaction, app_commands, InteractionType
from checks import WrongChannel
import discord
import asyncio
import logging

log = logging.getLogger("discord.automaton.events")

@bot.tree.error
async def on_app_command_error(interaction: Interaction, error: app_commands.AppCommandError):
    if isinstance(error, WrongChannel):
        await interaction.response.send_message(
            bot.messages["error_wrong_channel"], 
            ephemeral=True
            )
    elif isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            bot.messages["error_cooldown"].format(delay=error.retry_after),
            ephemeral=True
            )
    else:
        await interaction.response.send_message(bot.messages["error_unknown"], ephemeral=True)
        log.warning(f"Command {interaction.command.name} called by {interaction.user} failed: {error}")
    

@bot.event
async def on_interaction(interaction: Interaction):
    if interaction.type is InteractionType.application_command:
        cmd = interaction.data.get("name")
        log.info(f"/{cmd} executed by {interaction.user} at {interaction.guild}/{interaction.channel}")
        
@bot.event 
async def on_member_join(member: discord.Member) -> None:
    """Handles member joining server."""
    
    channel_id = bot.welcome_channel_id
    
    if channel_id:
        welcome_channel = bot.get_channel(channel_id)
        
        if welcome_channel:
            raw = bot.messages["welcome_embed"]
            embed = discord.Embed(
                title=raw["title"],
                description=raw["description"].replace("{username}", member.mention),
                color=raw["color"]
            )
            embed.set_footer(text=raw["footer"]["text"])
            await welcome_channel.send(embed=embed)
        else:
            log.error(f"Channel ID {channel_id} not found at {member.guild.name}.")
    else:
        log.error("Welcome channel not set in 'config.json'.")
        
@bot.event
async def on_ready() -> None:
    """Handles bot initialization."""
    
    log.info(f"{bot.user} initialized!")

@bot.event
async def on_voice_state_update(member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
    """Handles voice channel status update."""
    
    # handles voice channel becoming empty, so that bot doesn't idle on an empty voice channel
    # basically, when channel becomes empty and bot is connected to voice channel, 
    # it starts waiting 30 seconds before leaving that channel
    if before.channel is not None and before.channel != after.channel:
        voice_channel = before.channel
        voice_client = member.guild.voice_client

        if voice_client and voice_client.channel == voice_channel:
            non_bot_members = [m for m in voice_channel.members if not m.bot]

            if len(non_bot_members) == 0:
                if voice_channel.id in bot:
                    return
                
                async def delayed_disconnect():
                    await asyncio.sleep(30)
                    
                    # check again if voice channel is empty (real humans)
                    if all(m.bot for m in voice_channel.members):
                        await voice_client.disconnect()
                        log.info(f"Left voice channel `{voice_channel.name}` since it is now empty.")
                        
                    bot.pending_vc_disconnect_tasks.pop(voice_channel.id, None)
                    
                task = asyncio.create_task(delayed_disconnect())
                bot.pending_vc_disconnect_tasks[voice_channel.id] = task
