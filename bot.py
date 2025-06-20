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
        
        self.load_tokens()
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
            with open("config.json", "r", encoding="utf-8") as f:
                config = json.load(f)
        except Exception:
            log.exception("Failed to load config from 'config.json'.")
        
        self.max_reminders_per_user = config.get("MAX_REMINDERS_PER_USER", 3)
        self.max_reminder_seconds = config.get("MAX_REMINDER_SECONDS", 43200)
        self.radio_volume = config.get("RADIO_VOLUME", 0.03)
        self.radio_streams = config.get("RADIO_STREAMS", {})
        self.infos = config.get("INFOS", {})
        self.radio_volume_transformer = None
        self.messages_filename = config.get("MESSAGES_FILE", "messages_pt_br.yaml")
        
        try:
            with open(self.messages_filename, encoding="utf-8") as f:
                self.messages = yaml.safe_load(f)
        except Exception:
            log.exception(f"Failed to load messages file at '{self.messages_filename}'.")
        
    def load_tokens(self):
        self.token : str = os.getenv("DISCORD_BOT_TOKEN", "")
        self.welcome_channel_id : int = int(os.getenv("WELCOME_CHANNEL_ID", 0))
        self.allowed_command_channel_ids : list[int] = os.getenv("ALLOWED_COMMAND_CHANNEL_IDS", [])
        
    def init_discord_bot(self):
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.members = True
            self.discord_bot = commands.Bot(command_prefix="!", intents=intents)
        except Exception:
            log.exception("Failed to initialize Automaton Bot.")
            
    def save_config(self):
        try:
            config = {
                "MAX_REMINDERS_PER_USER": self.max_reminders_per_user,
                "MAX_REMINDER_SECONDS": self.max_reminder_seconds,
                "RADIO_VOLUME": self.radio_volume,
                "RADIO_STREAMS": self.radio_streams,
                "INFOS": self.infos
            }
            with open("config.json", "w", encoding="utf-8") as f:
                json.dump(config, f, ensure_ascii=True, indent=4)
                
            log.info("Config saved.")
        except Exception:
            log.exception("Failed to save new config to 'config.json'.")
        
bot = AutomatonBot()