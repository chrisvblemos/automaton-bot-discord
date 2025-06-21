from bot import bot
from discord import Permissions, app_commands, Interaction
from discord.ext import commands
import asyncio
from views.confirm_view import ConfirmView
import logging

log = logging.getLogger("discord.automaton.commands.Admin")

class Admin(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @app_commands.command(
        name="clear",
        description=bot.descriptions["command_description_clear"],
    )
    @app_commands.describe(
        quantidade=bot.descriptions["command_describe_clear_quantity"]
    )
    @app_commands.default_permissions(
        Permissions(manage_messages=True)
        )
    async def clear(self, interaction: Interaction, quantidade: int):
        if quantidade < 1 or quantidade > 100:
            await interaction.response.send_message(
                bot.messages["error_quantity_range"], ephemeral=True
            )
            return

        await interaction.response.defer()
        await interaction.channel.purge(limit=quantidade + 1)

        text = bot.messages["confirm_deleted_messages"].format(
            quantidade=quantidade,
            user=interaction.user.mention
        )
        confirmation = await interaction.followup.send(text)
        await asyncio.sleep(3)
        await confirmation.delete()
        
    @app_commands.command(
        name="clearall",
        description=bot.descriptions["command_description_clear_all"],
    )
    @app_commands.default_permissions(
        Permissions(administrator=True)
        )
    async def clearall(self, interaction: Interaction):
        view = ConfirmView(author_id=interaction.user.id)
        await interaction.response.send_message(
            bot.messages["clear_all_confirmation_prompt"], view=view, ephemeral=True
        )
        
        await view.wait()

        if view.value:
            await interaction.followup.send(bot.messages["cleaning"], ephemeral=True)
            await interaction.channel.purge()
            text = bot.messages["cleared_all_messages"].format(user=interaction.user.mention)
            await interaction.followup.send(text)
            log.warning(
                f"'{interaction.user}' deleted all messages from channel {interaction.channel.name}."
            )
        else:
            log.warning(
                f"'{interaction.user}' tried to delete all messages from channel {interaction.channel.name}."
            )
            await interaction.followup.send(bot.messages["action_cancelled"], ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Admin(bot))
    