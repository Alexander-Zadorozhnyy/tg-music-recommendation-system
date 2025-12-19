# app/lyrics_api.py
import os
from dotenv import load_dotenv

import lyricsgenius

load_dotenv()

def _get_token() -> str | None:
    return os.getenv("GENIUS_ACCESS_TOKEN") or os.getenv("GENIUS_TOKEN")

# Создаём клиент один раз (на модуль)
_TOKEN = _get_token()
_genius = None
if _TOKEN:
    _genius = lyricsgenius.Genius(
        _TOKEN,
        timeout=8,                 # таймаут запросов
        retries=2,                 # авто-ретраи
        remove_section_headers=True,
        skip_non_songs=True,
        excluded_terms=["(Remix)", "(Live)"],
    )

def fetch_lyrics_from_api(artist: str, track: str) -> str:
    """
    Возвращает текст песни или строку-ошибку вида:
    [Error fetching lyrics]: ...
    """
    if not artist or not track:
        return "[Error fetching lyrics]: Empty artist/track"

    if _genius is None:
        return "[Error fetching lyrics]: GENIUS_ACCESS_TOKEN is not set"

    try:
        song = _genius.search_song(title=track, artist=artist)
        if not song or not getattr(song, "lyrics", None):
            return "[Error fetching lyrics]: Not found on Genius"
        return song.lyrics
    except Exception as e:
        return f"[Error fetching lyrics]: {e}"

