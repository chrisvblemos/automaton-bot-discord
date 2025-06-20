from discord import app_commands, Interaction, Permissions, ButtonStyle
from discord.ui import View, button, Button
from discord.ext import commands
from bot import bot
import asyncio
import logging

log = logging.getLogger("discord.automaton.commands")

class ConfirmView(View):
    def __init__(self, *, author_id: int, timeout: float = 15.0):
        super().__init__(timeout=timeout)
        self.author_id = author_id
        self.value: bool | None = None

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user.id != self.author_id:
            await interaction.response.send_message(
                bot.messages["interaction_denied"], ephemeral=True
            )
            return False
        return True

    @button(label=bot.messages["command_button_clear_ok"], style=ButtonStyle.green)
    async def confirm(self, interaction: Interaction, button: Button):
        self.value = True
        self.stop()
        await interaction.response.defer()

    @button(label=bot.messages["command_button_clear_cancel"], style=ButtonStyle.red)
    async def cancel(self, interaction: Interaction, button: Button):
        self.value = False
        self.stop()
        await interaction.response.defer()

@app_commands.command(
    name="clear",
    description=bot.messages["command_description_clear"],
)
@app_commands.describe(
    quantidade=bot.messages["command_describe_clear_quantity"]
)
@app_commands.default_permissions(Permissions(administrator=True))
async def clear(interaction: Interaction, quantidade: int):
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
    description=bot.messages["command_description_clear_all"],
)
@app_commands.default_permissions(Permissions(administrator=True))
async def clearall(interaction: Interaction):
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
    bot.tree.add_command(clear)
    bot.tree.add_command(clearall)
