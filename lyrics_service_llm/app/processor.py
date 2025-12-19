# app/processor.py
from app.models import IncomingMessage, OutgoingMessage
from app.repo_csv import CsvLyricsRepository
from app.lyrics_api import fetch_lyrics_from_api
from app.llm_groq import analyze_songs_with_llm


def process_message(msg: IncomingMessage, repo: CsvLyricsRepository) -> OutgoingMessage:
    songs_for_llm = []

    for credit in msg["song_credits"]:
        artist = credit["artist"]
        track = credit["track"]

        lyrics = repo.find_lyrics(artist, track)

        if not lyrics:
            lyrics = fetch_lyrics_from_api(artist, track)
            # если успешно скачали — кладём в CSV
            if lyrics and not str(lyrics).startswith("[Error fetching lyrics]"):
                repo.upsert_lyrics(artist, track, lyrics)

        songs_for_llm.append({
            "artist": artist,
            "track": track,
            "lyrics": lyrics or ""
        })

    # 1 LLM call for everything
    llm_result = analyze_songs_with_llm(songs_for_llm)

    # возвращаем как вариант C (без lyrics)
    return {
        "id": msg["id"],
        "user_id": msg["user_id"],
        "query": llm_result["query"],
        "songs_texts": llm_result["songs_texts"],
    }
