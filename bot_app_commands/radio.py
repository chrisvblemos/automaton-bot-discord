from bot import bot
from checks import cooldown_for_non_admins
from discord import app_commands, Interaction, VoiceChannel
from discord.ext import commands
import discord
import logging

log = logging.getLogger("discord.automaton.commands")

@app_commands.command(
    name="play_radio",
    description=bot.messages["command_description_play_radio"]
)
@app_commands.describe(source=bot.messages["command_describe_play_radio_source"])
@app_commands.checks.dynamic_cooldown(cooldown_for_non_admins)
async def play_radio(interaction: Interaction, source: str = None) -> None:
    """Starts playing radio on voice channel where user is currently connected."""
    user_channel: VoiceChannel = interaction.user.voice.channel if interaction.user.voice else None
    author = interaction.user.mention

    if not user_channel:
        await interaction.response.send_message(
            bot.messages["error_not_in_voice"].format(user=author),
            ephemeral=True
        )
        return

    if source in bot.radio_streams:
        url = bot.radio_streams[source]
    elif interaction.user.guild_permissions.administrator:
        url = source
    else:
        await interaction.response.send_message(
            bot.messages["error_not_authorized_custom"].format(user=author),
            ephemeral=True
        )
        return

    vc = interaction.guild.voice_client
    if vc:
        current = vc.channel
        if current and current != user_channel:
            if not interaction.user.guild_permissions.administrator:
                await interaction.response.send_message(
                    bot.messages["error_cannot_force_channel"].format(channel=current.mention, user=author),
                    ephemeral=True
                )
                return

            log.info(
                f"{interaction.user.name} switched radio to channel {user_channel.name}"
            )
            await vc.move_to(user_channel)
            return

        if vc.is_playing():
            await interaction.response.send_message(
                bot.messages["info_request_change_station"].format(
                    user=author, url=url, channel=current.mention
                )
            )
            vc.stop()
    else:
        vc = await user_channel.connect()

    try:
        source_audio = discord.FFmpegPCMAudio(
            url,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options="-vn -ar 48000 -ac 2"
        )
        bot.radio_volume_transformer = discord.PCMVolumeTransformer(source_audio, volume=0.08)
        vc.play(bot.radio_volume_transformer)

        await interaction.response.send_message(
            bot.messages["play_radio_success"].format(url=url, channel=user_channel.mention)
        )
    except Exception:
        log.exception(f"Failed to switch radio source to {source}, requested by {interaction.user.name}.")
        await interaction.response.send_message(
            bot.messages["error_play_radio"],
            ephemeral=True
        )

@app_commands.command(
    name="stopradio",
    description=bot.messages["command_description_stop_radio"]
)
async def stop_radio(interaction: Interaction):
    """Stops playing radio. Disconnects from voice channel."""
    vc = interaction.guild.voice_client
    if vc:
        await vc.disconnect()
        await interaction.response.send_message(bot.messages["stop_radio_success"])
    else:
        await interaction.response.send_message(
            bot.messages["error_not_playing"],
            ephemeral=True
        )

@app_commands.command(
    name="increasevolume",
    description=bot.messages["command_description_increase_volume"]
)
async def increase_volume(interaction: Interaction, step: float = 0.01):
    """Increases radio output volume."""
    if not getattr(bot, "radio_volume_transformer", None):
        await interaction.response.send_message(
            bot.messages["error_not_playing_volume"],
            ephemeral=True
        )
        return

    new_volume = min(bot.radio_volume_transformer.volume + step, 1.0)
    bot.radio_volume_transformer.volume = new_volume

    await interaction.response.send_message(
        bot.messages["volume_changed"].format(volume=round(new_volume * 100))
    )

@app_commands.command(
    name="decreasevolume",
    description=bot.messages["command_description_decrease_volume"]
)
async def decrease_volume(interaction: Interaction, step: float = 0.01):
    """Decreases radio output volume."""
    if not getattr(bot, "radio_volume_transformer", None):
        await interaction.response.send_message(
            bot.messages["error_not_playing_volume"],
            ephemeral=True
        )
        return

    new_volume = max(bot.radio_volume_transformer.volume - step, 0.0)
    bot.radio_volume_transformer.volume = new_volume

    await interaction.response.send_message(
        bot.messages["volume_changed"].format(volume=round(new_volume * 100))
    )

@app_commands.command(
    name="setvolume",
    description=bot.messages["command_description_set_volume"]
)
async def set_volume(interaction: Interaction, value: float):
    """Sets radio output volume."""
    if not getattr(bot, "radio_volume_transformer", None):
        await interaction.response.send_message(
            bot.messages["error_not_playing_volume"],
            ephemeral=True
        )
        return

    new_volume = round(max(min(value, 1.0), 0.0) * 100)
    bot.radio_volume_transformer.volume = new_volume / 100.0

    await interaction.response.send_message(
        bot.messages["volume_set"].format(volume=new_volume)
    )

@play_radio.autocomplete("source")
async def radio_source_autocomplete(
    interaction: Interaction,
    current: str
) -> list[app_commands.Choice[str]]:
    sources = bot.radio_streams.keys()
    return [
        app_commands.Choice(name=source, value=source)
        for source in sources
        if current.lower() in source.lower()
    ][:25]  # discord allows max 25 suggestions

async def setup(bot: commands.Bot):
    bot.tree.add_command(play_radio)
    bot.tree.add_command(stop_radio)
    bot.tree.add_command(increase_volume)
    bot.tree.add_command(decrease_volume)
    bot.tree.add_command(set_volume)
