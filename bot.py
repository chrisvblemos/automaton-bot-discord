import discord
from discord.ext import commands
from checks import ChannelNotFound
import os
import json
import logging
import yaml

log = logging.getLogger("discord.automaton.bot")

LOCALIZATION_DIR = "localization/"

class MissingDiscordToken(Exception):
    pass

class AutomatonBot(commands.Bot):
    def __init__(self):
        self.pending_vc_disconnect_tasks = {}
        
        self.messages = {}
        self.descriptions = {}
        self.embeds = {}
        self.config = {}
        
        self.load_env()
        self.load_config()
        self.load_localization()
        
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
                self.config = json.load(f)
        except Exception:
            log.exception(f"Failed to load config {self.config_filename}.")
        
        self.welcome_channel_id = int(self.config.get("WELCOME_CHANNEL_ID", 0))
        self.music_channel_id = int(self.config.get("MUSIC_CHANNEL_ID", 0))
        self.infos = self.config.get("INFOS", {})
        
        self.localization_messages_filename = self.config.get("LOCAL_MESSAGES_FILENAME", "bot_messages_template.yaml")
        self.localization_embeds_filename = self.config.get("LOCAL_EMBEDS_FILENAME", "bot_embeds_template.yaml")
        self.localization_descriptions_filename = self.config.get("LOCAL_DESCRIPTIONS_FILENAME", "bot_descriptions_template.yaml")
            
    def load_localization(self):
        dir_descriptions = os.path.join(LOCALIZATION_DIR, self.localization_descriptions_filename)
        dir_messages = os.path.join(LOCALIZATION_DIR, self.localization_messages_filename)
        dir_embeds = os.path.join(LOCALIZATION_DIR, self.localization_embeds_filename)
        
        try:
            with open(dir_descriptions, encoding="utf-8") as f:
                self.descriptions = yaml.safe_load(f)
        except Exception:
            log.exception(f"Failed to load localization file '{dir_descriptions}'.")
        try:
            with open(dir_messages, encoding="utf-8") as f:
                self.messages = yaml.safe_load(f)
        except Exception:
            log.exception(f"Failed to load localization file '{dir_messages}'.")
        try:
            with open(dir_embeds, encoding="utf-8") as f:
                self.embeds = yaml.safe_load(f)
        except Exception:
            log.exception(f"Failed to load localization file '{dir_embeds}'.")
            
        
    def load_env(self):
        self.token : str = os.getenv("DISCORD_BOT_TOKEN")
        if self.token is None:
            raise MissingDiscordToken("Missing DISCORD_BOT_TOKEN environment variable.")
        self.config_filename : str = os.getenv("CONFIG_FILENAME", "config_template.json")
        
    def init_discord_bot(self):
        try:
            intents = discord.Intents.default()
            intents.message_content = True
            intents.members = True
            self.discord_bot = commands.Bot(command_prefix="/", intents=intents)
        except Exception:
            log.exception("Failed to initialize Automaton Bot.")
        
bot = AutomatonBot()