# app/models.py

from typing import TypedDict, List


class SongCredit(TypedDict):
    artist: str
    song: str


class IncomingMessage(TypedDict):
    id: str
    user_id: str
    song_credits: List[SongCredit]
    query: str


class SongText(TypedDict):
    artist: str
    song: str
    summary: str
    keywords: List[str]


class OutgoingMessage(TypedDict):
    id: str
    user_id: str
    query: str
    songs_texts: List[SongText]
