from checks import cooldown_for_non_admins
from discord import app_commands, Interaction
from discord.ext import commands
import logging
from bot import bot


log = logging.getLogger("discord.automaton.commands")

@app_commands.command(
    name="ping",
    description=bot.messages["command_description_ping"]
)
@app_commands.checks.dynamic_cooldown(cooldown_for_non_admins)
async def ping(interaction: Interaction) -> None:
    await interaction.response.send_message(
        bot.messages["ping_response"],
        ephemeral=True
    )
    
async def setup(bot: commands.Bot):
    bot.tree.add_command(ping)
