from bot import bot
from config import bot_config

import commands
import events
import checks

bot.run(bot_config.token)
