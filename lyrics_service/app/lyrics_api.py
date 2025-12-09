import os
import lyricsgenius

GENIUS_TOKEN = os.getenv("GENIUS_API_TOKEN")
genius = lyricsgenius.Genius(
    GENIUS_TOKEN, skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"]
)


def fetch_lyrics_from_api(artist: str, song: str) -> str:
    try:
        song = genius.search_song(song, artist)
        if song and song.lyrics:
            return song.lyrics
        return f"Lyrics not found for {artist} - {song}"
    except Exception as e:
        return f"[Error fetching lyrics]: {str(e)}"
