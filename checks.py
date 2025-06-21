from discord import Interaction, app_commands
import logging

log = logging.getLogger("discord.automaton.checks")

class ChannelNotFound(ValueError):
    pass

class WrongMusicChannel(app_commands.CheckFailure):
    """Raised when a music command is used outside the designated channel."""
    pass

class WrongChannel(app_commands.CheckFailure):
    """Raised when a command is used outside allowed channels."""
    pass

def in_music_channel():
    def predicate(interaction: Interaction) -> bool:
        if interaction.channel.id != interaction.client.music_channel_id:
            raise WrongMusicChannel()
        return True
    return app_commands.check(predicate)

def cooldown_for_non_admins(interaction: Interaction):
    if interaction.user.guild_permissions.administrator:
        return None
    return app_commands.Cooldown(1, 5.0)

def is_in_allowed_command_channel():
    """Decorator for checking if command is allowed in given channel."""
    
    def predicate(interaction: Interaction):
        allowed = interaction.client.allowed_command_channel_ids
        if not allowed or len(allowed) == 0:
            return True
        
        if interaction.channel.id not in allowed:
            raise WrongChannel()
        return True
    
    return app_commands.check(predicate)
