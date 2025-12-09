from pydantic import BaseModel, field_validator
from typing import List


class TrackItem(BaseModel):
    artist: str
    song: str

    @field_validator("artist", "song")
    @classmethod
    def strip_and_capitalize(cls, v: str) -> str:
        return v.strip().title() if v.strip() else v.strip()


class TrackList(BaseModel):
    tracks: List[TrackItem]
