from bot import bot
from checks import cooldown_for_non_admins
from discord import app_commands, Interaction, Embed, Color
from discord.ext import commands
import logging

log = logging.getLogger("discord.automaton.commands")

@app_commands.command(name="info", description=bot.messages["command_description_info"])
@app_commands.describe(topic=bot.messages["command_describe_info_topic"])
@app_commands.checks.dynamic_cooldown(cooldown_for_non_admins)
async def info(interaction: Interaction, topic: str = None):
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
            description=bot.messages["info_available_description"],
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

@info.autocomplete("topic")
async def info_topic_autocomplete(
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
    bot.tree.add_command(info)