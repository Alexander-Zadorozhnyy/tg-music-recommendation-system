# app/processor.py

from app.models import IncomingMessage, OutgoingMessage, SongText
from app.repo_csv import CsvLyricsRepository
from app.lyrics_api import fetch_lyrics_from_api
from app.text_compressor import extract_keywords


def process_message(msg: IncomingMessage, repo: CsvLyricsRepository) -> OutgoingMessage:
    results: list[SongText] = []

    for credit in msg["song_credits"]:
        artist = credit["artist"]
        song = credit["song"]

        lyrics = repo.find_lyrics(artist, song)
        if not lyrics:
            lyrics = fetch_lyrics_from_api(artist, song)

        keywords = extract_keywords(lyrics)

        results.append(
            {"artist": artist, "song": song, "lyrics": lyrics, "keywords": keywords}
        )

    return {
        "id": msg["id"],
        "user_id": msg["user_id"],
        "query": msg["query"],
        "songs_texts": results,
    }
