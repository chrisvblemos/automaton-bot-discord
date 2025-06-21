from bot import bot
from checks import cooldown_for_non_admins
from discord import app_commands, Interaction, Embed, Color
from discord.ext import commands
import logging

log = logging.getLogger("discord.automaton.commands.Info")

class Info(commands.Cog):
    def __init__(self, bot): 
        self.bot = bot

    @app_commands.command(
        name="ping",
        description=bot.descriptions["command_description_ping"]
        )
    @app_commands.checks.dynamic_cooldown(cooldown_for_non_admins)
    async def ping(self, interaction: Interaction) -> None:
        await interaction.response.send_message(
            bot.messages["ping_response"],
            ephemeral=True
        )

    @app_commands.command(
        name="help", 
        description=bot.descriptions["command_description_info"]
        )
    @app_commands.describe(
        topic=bot.descriptions["command_describe_info_topic"]
        )
    @app_commands.checks.dynamic_cooldown(
        cooldown_for_non_admins
        )
    async def help(self, interaction: Interaction, topic: str = None):
        infos = bot.infos

        if topic is None:
            if not infos:
                await interaction.response.send_message(
                    bot.messages["info_no_topics"],
                    ephemeral=True
                )
                return

            embed = Embed(
                title=bot.messages["info_available_title"],
                description=bot.descriptions["info_available_description"],
                color=Color.blue()
            )

            for key in infos.keys():
                embed.add_field(
                    name=key,
                    value=bot.messages["info_field_value"].format(topic=key),
                    inline=False
                )

            await interaction.response.send_message(embed=embed, ephemeral=True)
            return

        topic = topic.lower()
        response = bot.infos.get(topic)
        if response:
            await interaction.response.send_message(
                bot.messages["info_response"].format(response=response),
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                bot.messages["info_not_found"].format(topic=topic),
                ephemeral=True
            )

    @help.autocomplete("topic")
    async def info_topic_autocomplete(
        self,
        interaction: Interaction,
        current: str
    ) -> list[app_commands.Choice[str]]:
        topics = bot.infos.keys()
        return [
            app_commands.Choice(name=topic, value=topic)
            for topic in topics
            if current.lower() in topic.lower()
        ][:25]  # discord allows max 25 suggestions

async def setup(bot: commands.Bot):
    await bot.add_cog(Info(bot))