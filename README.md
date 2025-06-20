
Simple Discord bot with dice rolls, radio streaming, and customizable info.

---

## Commands

### /roll <rule>
Rolls dice with format `NdX[+/-Y]`.  
Examples:  
```
/roll         → 1d20  
/roll 2d10+1  → 2 d10 + 1  
/roll 1d6-2   → 1 d6 - 2  
```

### /info <topic>
Shows predefined info. Topics come from `config.json`.  
Omit to list available ones.

### /ping
Bot replies with pong.

### /playradio \<source>
Plays a radio stream in your voice channel.  
`source` can be a URL or preset name in `config.json`.

### /stopradio
Stops radio and disconnects.

### /increasevolume [value]  
### /decreasevolume [value]  
Change stream volume (default step: 0.01). Range: 0.0–1.0

### /setvolume <value>
Set stream volume directly. Range: 0.0–1.0

### /clear <n>
Deletes last n messages. Requires `Manage Messages`.

### /clearall
Clears all messages in channel. Requires `Administrator`. Prompts for confirmation.

---

## config.json

Example:

```json
{
  "WELCOME_CHANNEL_ID": 0,
  "ALLOWED_COMMAND_CHANNEL_IDS": [],
  "INFOS": {
    "duneawakening": "Atualmente o pessoal está jogando no servidor `Othello - Umbu`. Nossa guilda se chama `Tovarisch`."
  },
  "RADIO_STREAMS": {
    "indie":  "https://ice1.somafm.com/indiepop-128-mp3",
    "ambient": "https://ice1.somafm.com/groovesalad-128-mp3"
  },
  "MESSAGES_FILE": "messages_pt_br.yaml"
}
```

---

## Localization

Edit `messages_pt_br.yaml` and set `MESSAGES_FILE` in `config.json` to customize bot messages.

---

## Environment Variables

Required:
```
DISCORD_BOT_TOKEN=your_token
CONFIG_FILENAME=config.json
```

---

## Running

```bash
pip install -r requirements.txt
python main.py
```

Requires: Python 3.10+, `discord.py >=2.0`, FFmpeg.
