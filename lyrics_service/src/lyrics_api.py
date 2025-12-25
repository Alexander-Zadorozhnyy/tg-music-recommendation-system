import lyricsgenius


class GiniusInteractor:
    def __init__(self, token: str):
        self._genius = lyricsgenius.Genius(
            token,
            timeout=8,  # таймаут запросов
            retries=2,  # авто-ретраи
            remove_section_headers=True,
            skip_non_songs=True,
            excluded_terms=["(Remix)", "(Live)"],
        )

    def fetch_lyrics_from_api(self, artist: str, song: str) -> str:
        """
        Возвращает текст песни или строку-ошибку вида:
        [Error fetching lyrics]: ...
        """
        if not artist or not song:
            return "[Error fetching lyrics]: Empty artist/song"

        try:
            song = self._genius.search_song(title=song, artist=artist)
            if not song or not getattr(song, "lyrics", None):
                return "[Error fetching lyrics]: Not found on Genius"
            return song.lyrics
        except Exception as e:
            return f"[Error fetching lyrics]: {e}"
