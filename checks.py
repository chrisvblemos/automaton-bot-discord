from discord import Interaction, app_commands
from bot import bot
import logging

log = logging.getLogger("discord.automaton.checks")

class WrongChannel(app_commands.CheckFailure):
    """Raised when a command is used outside allowed channels."""
    pass

def cooldown_for_non_admins(interaction: Interaction):
    if interaction.user.guild_permissions.administrator:
        return None
    return app_commands.Cooldown(1, 5.0)

def is_in_allowed_command_channel():
    """Decorator for checking if command is allowed in given channel."""
    
    def predicate(interaction: Interaction):
        allowed = bot.allowed_command_channel_ids
        if not allowed or len(allowed) == 0:
            return True
        
        if interaction.channel.id not in allowed:
            raise WrongChannel()
        return True
    
    return app_commands.check(predicate)
