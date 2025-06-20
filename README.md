# 🤖 Automaton Bot — Discord Companion

A simple and extensible Discord bot with essential features like dice rolls, radio streaming, and configurable info responses.

---

## 📜 Commands

### `/roll <rule>`
Rolls dice according to a specified rule.  
**Default**: `1d20`  
**Format**: `<n>d<faces><+/-><offset>`

#### Examples:
```
/roll 2d20     → rolls two 20-sided dice and sums the result.
/roll 1d20-4   → rolls one 20-sided die and subtracts 4.
/roll 3d10+2   → rolls three 10-sided dice and adds 2.
```

---

### `/info <topic>`
Displays predefined information on a topic.  
Topics are configured in `config.json`.

- If no topic is provided, the bot will list all available ones.

---

### `/ping`
Checks if the bot is online. Responds with "pong".

---

### `/playradio <source>`
Joins your voice channel and streams a radio station.

- `source` can be a direct stream URL or a named preset defined in `config.json`.
- Autocomplete suggestions are shown for preset stations.

#### Example stream URLs:
```
https://ice1.somafm.com/indiepop-128-mp3
https://ice1.somafm.com/groovesalad-128-mp3
https://ice1.somafm.com/defcon-128-mp3
https://ice1.somafm.com/bossa-128-mp3
https://ice1.somafm.com/insound-128-mp3
https://ice1.somafm.com/thistle-128-mp3
https://ice1.somafm.com/bootliquor-128-mp3
https://kexp.streamguys1.com/kexp160.aac
```

---

### `/stopradio`
Stops the radio stream and disconnects the bot from the voice channel.

---

### `/increasevolume [value]`
Increases the radio volume.  
- `value` is optional (default: `0.01`)  
- Range: `0.0` to `1.0` (0% to 100%)

---

### `/decreasevolume [value]`
Decreases the radio volume.  
- `value` is optional (default: `0.01`)  
- Range: `0.0` to `1.0`

---

### `/setvolume <value>`
Sets the radio volume to a specific level.  
- `value`: between `0.0` and `1.0`

---

## 🔧 Admin Commands

### `/clearall`
> **Permission Required**: Administrator

Deletes **all messages** in the current channel.  
A confirmation prompt will appear before execution.

---

### `/clear <n>`
> **Permission Required**: `Manage Messages`

Deletes the last `n` messages in the current channel.  
**No confirmation** — executes immediately.

---

## 🗺️ Localization

Automaton Bot supports message localization and customization.

To change the bot’s responses:

1. Edit the file `messages_pt_br.yaml` with your custom or translated messages.
2. In your `config.json`, set the key `MESSAGES_FILE` to the path of your YAML file.

This allows you to fully localize or customize user-facing texts such as error messages, confirmations, and command responses.

---

## ⚙️ Configuration (`config.json`)

Here’s an example of a valid `config.json`:

```json
{
  "WELCOME_CHANNEL_ID": 0,
  "ALLOWED_COMMAND_CHANNEL_IDS": [],
  "INFOS": {
    "duneawakening": "Atualmente o pessoal está jogando no servidor `Othello - Umbu`. Nossa guilda se chama `Tovarisch`."
  },
  "RADIO_STREAMS": {
    "indie":  "https://ice1.somafm.com/indiepop-128-mp3",
    "ambient": "https://ice1.somafm.com/groovesalad-128-mp3",
    "hacking": "https://ice1.somafm.com/defcon-128-mp3",
    "bossanova": "https://ice1.somafm.com/bossa-128-mp3",
    "vintage": "https://ice1.somafm.com/insound-128-mp3",
    "celtico": "https://ice1.somafm.com/thistle-128-mp3",
    "country": "https://ice1.somafm.com/bootliquor-128-mp3",
    "kexp": "https://kexp.streamguys1.com/kexp160.aac"
  },
  "MESSAGES_FILE": "messages_pt_br.yaml"
}
```

### Required environment variables:

The following environment variables must be defined to run the bot:

```
DISCORD_BOT_TOKEN=your_token_here
CONFIG_FILENAME=config.json
```

---

## 📌 Notes

- The bot uses [discord.py](https://github.com/Rapptz/discord.py) with `app_commands` and slash command support.
- To add new commands or change functionality, extend the appropriate Python modules inside `bot_commands/`.

---

## 🖥️ Requirements

- Python 3.10+
- `discord.py >=2.0`
- [FFmpeg](https://ffmpeg.org/) (for radio stream playback)

---

## 📦 Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Run the bot
python main.py
```

---

## 🔒 Permissions

Ensure the bot has the following permissions:
- `Send Messages`
- `Connect`
- `Speak`
- `Manage Messages` (for `/clear`)
- `Administrator` (optional, for `/clearall`)
