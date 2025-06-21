from discord import Interaction, ButtonStyle
from discord.ui import View, button, Button
from bot import bot

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

    @button(label=bot.descriptions["command_button_clear_ok"], style=ButtonStyle.green)
    async def confirm(self, interaction: Interaction, button: Button):
        self.value = True
        self.stop()
        await interaction.response.defer()

    @button(label=bot.descriptions["command_button_clear_cancel"], style=ButtonStyle.red)
    async def cancel(self, interaction: Interaction, button: Button):
        self.value = False
        self.stop()
        await interaction.response.defer()