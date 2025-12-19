# app/models.py
from typing import TypedDict, List, NotRequired


class SongCredit(TypedDict):
    artist: str
    track: str


class IncomingMessage(TypedDict):
    id: str
    user_id: str
    song_credits: List[SongCredit]
    query: str


class SongText(TypedDict):
    artist: str
    track: str
    summary: NotRequired[str]
    keywords: NotRequired[List[str]]


class OutgoingMessage(TypedDict):
    id: str
    user_id: str
    query: str
    songs_texts: List[SongText]
