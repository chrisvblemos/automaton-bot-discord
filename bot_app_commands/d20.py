from discord import app_commands, Interaction
from checks import cooldown_for_non_admins
from discord.ext import commands
from bot import bot
import random
import discord
import re
import logging

log = logging.getLogger("discord.automaton.commands")
pattern = r"(?P<n>\d+)[dD](?P<faces>\d+)(?P<operator>[+-])?(?P<offset>\d+)?"

@app_commands.command(name="roll", description=bot.messages["command_description_roll"])
@app_commands.describe(rule=bot.messages["command_roll_rule"])
@app_commands.checks.dynamic_cooldown(cooldown_for_non_admins)
async def roll(interaction: Interaction, rule: str = "1d20") -> None:
    """Rolls a dice.
        rule: rule to use

        !roll 1d20+2"""

    match = re.fullmatch(pattern, rule)
    if match:
        n = max(int(match.group("n")), 0)
        faces = max(int(match.group("faces")), 0)
        operator = match.group("operator") or ""
        offset = match.group("offset") or ""
    else:
        await interaction.response.send_message(
            bot.messages["error_invalid_rule"],
            ephemeral=True
        )
        return

    if faces <= 1:
        await interaction.response.send_message(
            bot.messages["error_min_faces"],
            ephemeral=True
        )
        return

    if faces > 20:
        await interaction.response.send_message(
            bot.messages["error_max_faces"],
            ephemeral=True
        )
        return

    if n > 5:
        await interaction.response.send_message(
            bot.messages["error_max_dice"],
            ephemeral=True
        )
        return

    rolls = [random.randint(1, faces) for _ in range(n)]
    result = sum(rolls)

    if operator == "+":
        result += int(offset)
    elif operator == "-":
        result -= int(offset)

    result = max(result, 1)
    author = interaction.user.mention

    title = bot.messages["roll_embed_title"].format(rule=f"{n}d{faces}{operator}{offset}")
    description = bot.messages["roll_embed_description"].format(
        author=author,
        result=result
    )
    color = discord.Color.default()

    if result >= faces:
        description += bot.messages["roll_critical_suffix"]
        color = discord.Color.green()
    elif result == 1:
        description += bot.messages["roll_fail_suffix"]
        color = discord.Color.red()

    embed = discord.Embed(
        title=title,
        description=description,
        color=color
    )

    await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    bot.tree.add_command(roll)