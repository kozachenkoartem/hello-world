import asyncio
import logging
import os
import re
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import yt_dlp
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    raise RuntimeError("BOT_TOKEN environment variable is not set")

bot = Bot(token=TOKEN)
dp = Dispatcher()

TEMP_DIR = Path(tempfile.gettempdir()) / "mp3_loader_bot"
TEMP_DIR.mkdir(exist_ok=True)

executor = ThreadPoolExecutor(max_workers=2)
MAX_FILE_SIZE = 50 * 1024 * 1024

YOUTUBE_PATTERNS = [
    re.compile(r"^https?://(?:www\.)?youtube\.com/watch\?v=[\w-]+"),
    re.compile(r"^https?://(?:www\.)?youtu\.be/[\w-]+"),
    re.compile(r"^https?://(?:www\.)?youtube\.com/shorts/[\w-]+"),
]

WELCOME_MSG = (
    "Привет! Я MP3 Loader Bot.\n\n"
    "Отправь ссылку на YouTube видео — я скачаю аудио.\n"
    "Если в видео есть русская дорожка — пришлю её!\n"
    "Если нет — напишу, какие языки доступны."
)

HELP_MSG = (
    "Доступные команды:\n\n"
    "/start — приветствие\n"
    "/help  — эта справка\n\n"
    "Просто отправь ссылку на YouTube видео."
)


def is_youtube_url(text: str) -> bool:
    return any(p.match(text.strip()) for p in YOUTUBE_PATTERNS)


def _inspect_formats(url: str) -> dict:
    """Extract video metadata and audio language info."""
    with yt_dlp.YoutubeDL({"quiet": True, "no_warnings": True}) as ydl:
        info = ydl.extract_info(url, download=False)

    langs = set()
    ru_fmt_id = None
    for f in info.get("formats", []):
        a = f.get("acodec") or ""
        v = f.get("vcodec") or ""
        if a and a != "none" and (v == "none" or not v):
            lang = f.get("language") or "und"
            langs.add(lang)
            if lang.startswith("ru"):
                ru_fmt_id = f["format_id"]

    return {
        "video_id": info["id"],
        "title": info.get("title", "Unknown"),
        "duration": info.get("duration", 0),
        "languages": sorted(langs),
        "ru_format_id": ru_fmt_id,
    }


def _download_audio_sync(url: str) -> tuple[str, str, int, dict]:
    """Download audio, preferring Russian track. Returns (path, title, duration, info)."""
    TEMP_DIR.mkdir(exist_ok=True)

    meta = _inspect_formats(url)
    video_id = meta["video_id"]
    title = meta["title"]
    duration = meta["duration"]
    langs = meta["languages"]
    ru_fmt_id = meta["ru_format_id"]
    has_ru = ru_fmt_id is not None

    if has_ru:
        fmt_spec = ru_fmt_id
        logger.info("Russian track found: format %s. Langs: %s", ru_fmt_id, langs)
    else:
        fmt_spec = "bestaudio/best"
        logger.info("No Russian track. Available: %s. Using default.", langs)

    ydl_opts = {
        "format": fmt_spec,
        "outtmpl": str(TEMP_DIR / "%(id)s.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    mp3_path = TEMP_DIR / f"{video_id}.mp3"
    if not mp3_path.exists():
        candidates = sorted(TEMP_DIR.glob(f"{video_id}*.mp3"))
        if candidates:
            mp3_path = candidates[0]

    if not mp3_path.exists():
        raise FileNotFoundError(f"MP3 not found for {video_id}")

    file_size = mp3_path.stat().st_size
    if file_size == 0:
        os.unlink(mp3_path)
        raise ValueError("Downloaded file is empty")

    lang_label = "🇷🇺 Русский" if has_ru else "🌐 Оригинал"
    logger.info("Done: %s (%s), size=%d, langs=%s", title, lang_label, file_size, langs)

    return str(mp3_path), title, duration, {
        "has_ru": has_ru,
        "lang_label": lang_label,
        "languages": langs,
    }


async def download_audio(url: str) -> tuple[str, str, int, dict]:
    return await asyncio.get_event_loop().run_in_executor(
        executor, _download_audio_sync, url
    )


def format_duration(seconds: int) -> str:
    h, remainder = divmod(seconds, 3600)
    m, s = divmod(remainder, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def sanitize_filename(name: str) -> str:
    safe = re.sub(r'[^\w\s\-.,()\[\]{}]', '', name)
    return safe.strip() or "audio"


# ─── Handlers ──────────────────────────────────────────────────────


@dp.message(Command("start"))
async def cmd_start(message: types.Message) -> None:
    await message.answer(WELCOME_MSG)


@dp.message(Command("help"))
async def cmd_help(message: types.Message) -> None:
    await message.answer(HELP_MSG)


@dp.message()
async def handle_message(message: types.Message) -> None:
    if not message.text:
        return
    text = message.text.strip()
    if is_youtube_url(text):
        await handle_youtube_download(message, text)
    else:
        await message.answer(text)


async def handle_youtube_download(message: types.Message, url: str) -> None:
    status = await message.answer("⏳ Получаю информацию о видео...")
    try:
        await status.edit_text("⏳ Скачиваю...")
        filepath, title, duration, meta = await download_audio(url)

        file_size = os.path.getsize(filepath)
        if file_size > MAX_FILE_SIZE:
            raise ValueError(f"Файл слишком большой ({file_size // 1024 // 1024} MB).")

        dur_str = format_duration(duration)
        safe_title = sanitize_filename(title)

        # Build caption
        caption = f"🎵 {title}\n⏱ {dur_str}  |  🎤 {meta['lang_label']}"

        if not meta["has_ru"]:
            langs_str = ", ".join(meta["languages"])
            caption += f"\n\n💡 Доступные языки: {langs_str}"
            caption += "\nРусской дорожки нет — только автодубляж YouTube (не скачивается)."

        await status.edit_text(f"📤 Отправляю ({meta['lang_label']})...")

        doc = types.FSInputFile(filepath, filename=f"{safe_title}.mp3")
        await message.answer_document(document=doc, caption=caption)

        os.unlink(filepath)
        await status.delete()

    except yt_dlp.utils.DownloadError as e:
        logger.error("Download error: %s", e)
        await status.edit_text("❌ Не удалось скачать видео. Проверь ссылку.")
    except Exception as e:
        logger.error("Unexpected error: %s", e)
        try:
            await status.edit_text(f"❌ Ошибка: {str(e)[:200]}")
        except Exception:
            pass


# ─── Main ─────────────────────────────────────────────────────────


async def main() -> None:
    logger.info("Starting MP3 Loader Bot...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
