import json
from dotenv import load_dotenv
import os

class Config:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load()
        return cls._instance

    def _load(self):
        load_dotenv()
        self.token : str = os.getenv("DISCORD_BOT_TOKEN", "")
        self.welcome_channel_id : int = int(os.getenv("WELCOME_CHANNEL_ID", 0))
        self.listen_channel_id : int = int(os.getenv("LISTEN_CHANNEL_ID", 0))
        
        with open("config.json", "r") as f:
            config = json.load(f)
        
        self.max_reminders_per_user = config.get("MAX_REMINDERS_PER_USER", 3)
        self.max_reminder_seconds = config.get("MAX_REMINDER_SECONDS", 43200)
        self.radio_volume = config.get("RADIO_VOLUME", 0.03)
        
    def __repr__(self):
        return f"<Config token=*** channel={self.welcome_channel_id}>"

bot_config = Config()
