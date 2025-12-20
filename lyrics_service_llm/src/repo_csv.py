# app/repo_csv.py
import os
import pandas as pd
from typing import Optional


class CsvLyricsRepository:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
        try:
            self.df = pd.read_csv(csv_path)
        except Exception as e:
            print(f"[repo_csv] Can't read {csv_path}: {e}")
            self.df = pd.DataFrame(columns=["artist_name", "track_name", "lyrics"])

        self.df.columns = [c.strip().lower() for c in self.df.columns]
        for col in ("artist_name", "track_name", "lyrics"):
            if col not in self.df.columns:
                self.df[col] = ""
        self.df.fillna("", inplace=True)

    def find_lyrics(self, artist: str, track: str) -> Optional[str]:
        if not artist or not track or self.df.empty:
            return None
        m = (self.df["artist_name"].str.lower() == artist.lower()) & (
            self.df["track_name"].str.lower() == track.lower()
        )
        res = self.df[m]
        if res.empty:
            return None
        val = str(res.iloc[0]["lyrics"]) or ""
        return val if val.strip() else None

    def upsert_lyrics(self, artist: str, track: str, lyrics: str) -> None:
        if not artist or not track or not lyrics or not lyrics.strip():
            return

        m = (self.df["artist_name"].str.lower() == artist.lower()) & (
            self.df["track_name"].str.lower() == track.lower()
        )

        if self.df[m].empty:
            self.df.loc[len(self.df)] = {
                "artist_name": artist,
                "track_name": track,
                "lyrics": lyrics,
            }
        else:
            idx = self.df[m].index[0]
            self.df.at[idx, "lyrics"] = lyrics

        os.makedirs(os.path.dirname(self.csv_path), exist_ok=True)
        self.df.to_csv(self.csv_path, index=False)
