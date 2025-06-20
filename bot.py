import discord
from discord.ext import commands
import os
import json
import logging
import yaml

log = logging.getLogger("discord.automaton.bot")

class AutomatonBot(commands.Bot):
    def __init__(self):
        self.pending_vc_disconnect_tasks = {}
        self.last_used_cmds = {}
        
        self.load_env()
        self.load_config()
        
        super().__init__(command_prefix="!", intents=discord.Intents.all())
        
    async def setup_hook(self):
        for filename in os.listdir("./bot_app_commands"):
            if filename.endswith(".py") and not filename.startswith("_"):
                await self.load_extension(f"bot_app_commands.{filename[:-3]}")
                
        await self.tree.sync()
        log.info("Slash commands synced globally")
        
    def load_config(self):
        try:
            with open(self.config_filename, "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            log.exception("Failed to load config from 'config.json'.")
        
        self.welcome_channel_id = int(config.get("WELCOME_CHANNEL_ID", 0))
        self.radio_streams = config.get("RADIO_STREAMS", {})
        self.infos = config.get("INFOS", {})
        self.radio_volume_transformer = None
        self.messages_filename = config.get("MESSAGES_FILE", "messages_pt_br.yaml")
        
        try:
            with open(self.messages_filename, encoding="utf-8") as f:
                self.messages = yaml.safe_load(f)
        except Exception:
            log.exception(f"Failed to load messages file at '{self.messages_filename}'.")
        
    def load_env(self):
        self.token : str = os.getenv("DISCORD_BOT_TOKEN", "")
        self.config_filename : str = os.getenv("CONFIG_FILENAME", "config.json")
        
    def init_discord_bot(self):
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.members = True
            self.discord_bot = commands.Bot(command_prefix="/", intents=intents)
        except Exception:
            log.exception("Failed to initialize Automaton Bot.")
        
bot = AutomatonBot()