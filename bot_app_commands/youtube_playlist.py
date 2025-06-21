import discord
import yt_dlp
import asyncio
import logging

from checks import in_music_channel
from bot import bot
from discord.ext import commands
from discord import app_commands
from urllib.parse import urlparse, parse_qs

log = logging.getLogger("discord.automaton.commands.YoutubePlaylist")

def looks_like_yt_playlist(url: str) -> bool:
    """Quick check: URL has a `list=` query parameter."""
    return "list" in parse_qs(urlparse(url).query)

class MissingMusicChannel(ValueError):
    pass

class YoutubePlaylist(commands.Cog):
    INACTIVITY_TIMEOUT = 300

    def __init__(self, bot):
        self.bot = bot
        self.empty_channel_task: asyncio.Task | None = None
        self.empty_queue_task: asyncio.Task | None = None
        self.queue = asyncio.Queue()
        self.voice_channel: discord.VoiceClient | None = None
        self.music_channel: discord.TextChannel | None = bot.get_channel(bot.music_channel_id)
        self.volume = 1.0

    @app_commands.command(
        name="playlist_play",
        description=bot.descriptions["command_describe_url_yt_playlist_play"]
    )
    @in_music_channel()
    async def playlist_play(self, interaction: discord.Interaction, url: str):
        if not (v := interaction.user.voice):
            return await interaction.response.send_message(
                bot.messages["yt_playlist_not_in_voice_channel"], ephemeral=True
            )
        if not looks_like_yt_playlist(url):
            return await interaction.response.send_message(
                bot.messages["yt_playlist_invalid_link"], ephemeral=True
            )

        if self.voice_channel and self.voice_channel.channel != interaction.user.voice.channel:
            return await interaction.response.send_message(
                bot.messages["yt_playlist_already_playing_elsewhere"], ephemeral=True
            )

        self.music_channel = interaction.channel
        await interaction.response.send_message(
            bot.messages["yt_playlist_loading"], ephemeral=True
        )

        try:
            entries = await self._extract_playlist_entries(url)
        except Exception:
            log.exception("Failed to extract playlist entries")
            return await interaction.followup.send(
                bot.messages["yt_playlist_error"], ephemeral=True
            )

        if not entries:
            return await interaction.followup.send(
                bot.messages["yt_playlist_no_entries"], ephemeral=True
            )

        if self.empty_queue_task:
            self.empty_queue_task.cancel()
            self.empty_queue_task = None

        for vid in entries:
            await self.queue.put(f"https://youtube.com/watch?v={vid}")
        await interaction.followup.send(
            bot.messages["yt_playlist_tracks_added"].format(n=len(entries)), ephemeral=True
        )
        log.info(f"Enqueued {len(entries)} tracks from playlist {url}")

        try:
            if not self.voice_channel:
                self.voice_channel = await v.channel.connect(timeout=15, self_deaf=True)
            if not self.voice_channel.is_playing():
                await self._nxt()
        except Exception:
            log.exception("Voice connection or playback failed")
            return await interaction.followup.send(
                bot.messages["yt_playlist_error"], ephemeral=True
            )

    def _schedule_empty_channel_check(self):
        if not self.voice_channel:
            return
        self.empty_channel_task = asyncio.create_task(self._disconnect_if_empty())

    def _cancel_empty_channel_check(self):
        if self.empty_channel_task:
            self.empty_channel_task.cancel()
            self.empty_channel_task = None

    async def _disconnect_if_empty(self):
        try:
            await asyncio.sleep(self.INACTIVITY_TIMEOUT)
            if not self.voice_channel:
                return
            non_bots = [
                m for m in self.voice_channel.channel.members if not m.bot and m.voice
            ]
            if len(non_bots) == 0:
                log.info("Voice channel is empty. Disconnecting due to inactivity.")
                await self.voice_channel.disconnect()
                self.voice_channel = None
                await self.music_channel.send(bot.messages["yt_playlist_disconnected_inactive"])
        except asyncio.CancelledError:
            pass

    async def _wait_and_disconnect_if_queue_remains_empty(self):
        try:
            await asyncio.sleep(self.INACTIVITY_TIMEOUT)
            if self.queue.empty() and self.voice_channel:
                log.info("No new entries after playlist ended. Disconnecting.")
                await self.voice_channel.disconnect()
                self.voice_channel = None
                await self.music_channel.send(bot.messages["yt_playlist_disconnected_inactive"])
        except asyncio.CancelledError:
            pass

    async def _extract_playlist_entries(self, url: str) -> list[str]:
        ydl_opts = {'quiet': True, 'extract_flat': 'in_playlist'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            data = ydl.extract_info(url, download=False)
        return [e['id'] for e in data.get('entries', []) if 'id' in e]

    async def _extract_audio_url(self, video_url: str) -> tuple[str,str]:
        ydl_opts = {'quiet': True, 'format': 'bestaudio'}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=False)
        return info['title'], info['url']

    async def _nxt(self):
        if self.queue.empty():
            log.info("Playlist finished, waiting for new entries...")
            self.empty_queue_task = asyncio.create_task(self._wait_and_disconnect_if_queue_remains_empty())
            return

        video = await self.queue.get()
        try:
            title, audio_url = await self._extract_audio_url(video)
        except Exception:
            log.exception(f"Failed to extract audio for {video}")
            return await self._nxt()

        log.info(f"Now playing {title}")
        src = discord.FFmpegOpusAudio(
            audio_url,
            before_options=(
                "-reconnect 1 -reconnect_streamed 1 "
                "-reconnect_delay_max 5"
            ),
            options=f'-vn -af "volume={self.volume}"'
        )

        self.voice_channel.play(
            src,
            after=lambda e: asyncio.run_coroutine_threadsafe(self._nxt(), self.bot.loop)
        )

        self._cancel_empty_channel_check()
        self._schedule_empty_channel_check()

        embed_data = bot.embeds["yt_playlist_playing_embed"]
        embed = discord.Embed(
            title=embed_data["title"],
            description=embed_data["description"].format(title=title, url=audio_url),
            color=embed_data["color"]
        )
        embed.set_footer(text=embed_data["footer"]["text"])

        await self.music_channel.send(embed=embed)

    @app_commands.command(
        name="playlist_skip",
        description=bot.descriptions["command_description_yt_playlist_skip"]
    )
    @in_music_channel()
    async def playlist_skip(self, interaction: discord.Interaction):
        if self.voice_channel and self.voice_channel.is_playing():
            self.voice_channel.stop()
            await interaction.response.send_message(
                bot.messages["yt_playlist_skipping"], ephemeral=True
            )
        else:
            await interaction.response.send_message(
                bot.messages["yt_playlist_nothing_to_skip"], ephemeral=True
            )

    @app_commands.command(
        name="playlist_stop",
        description=bot.descriptions["command_description_yt_playlist_stop"]
    )
    @in_music_channel()
    async def playlist_stop(self, interaction: discord.Interaction):
        if not self.voice_channel:
            return await interaction.response.send_message(
                bot.messages["yt_playlist_nothing_to_stop"], ephemeral=True
            )

        await self.voice_channel.disconnect()
        self.voice_channel = None
        self.queue = asyncio.Queue()
        await interaction.followup.send(
            bot.messages["yt_playlist_stopping"], ephemeral=True
        )

async def setup(bot):
    await bot.add_cog(YoutubePlaylist(bot))
