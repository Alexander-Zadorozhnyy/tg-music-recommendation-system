import pandas as pd
from typing import Optional

class CsvLyricsRepository:
    def __init__(self, csv_path: str):
        try:
            self.df = pd.read_csv(csv_path)
        except Exception as e:
            print(f"[repo_csv] Can't read {csv_path}: {e}")
            self.df = pd.DataFrame(columns=["artist_name","track_name","lyrics"])
        self.df.columns = [c.strip().lower() for c in self.df.columns]
        for col in ("artist_name","track_name","lyrics"):
            if col not in self.df.columns:
                self.df[col] = ""
        self.df.fillna("", inplace=True)

    def find_lyrics(self, artist: str, track: str) -> Optional[str]:
        if not artist or not track or self.df.empty:
            return None
        m = (
            (self.df["artist_name"].str.lower() == artist.lower()) &
            (self.df["track_name"].str.lower() == track.lower())
        )
        res = self.df[m]
        if res.empty:
            return None
        return str(res.iloc[0]["lyrics"]) or None
