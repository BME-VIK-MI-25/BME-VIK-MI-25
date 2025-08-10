from datetime import datetime
import modules.variables as variables
import disnake

async def log_message(bot: disnake.Client, level: str, message: str):
    channel_id = variables.DEVELOPER_LOG_CHANNEL_ID
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Színezés szint alapján
    levels = {
        "error": "**[ERROR]**",
        "debug": "**[DEBUG]**",
        "info": "**[INFO]**"
    }
    level_tag = levels.get(level.lower(), "**[INFO]**")

    full_message = f"{level_tag} [{timestamp}] {message}"

    # Csatorna lekérése és üzenet küldés
    channel = bot.get_channel(channel_id)
    if channel is None:
        return # Nem létezik a csatorna
    await channel.send(full_message)
