from typing import TypedDict, List


class SongText(TypedDict):
    artist: str
    song: str
    lyrics: str
    keywords: List[str]


class IncomingMessage(TypedDict):
    id: str
    user_id: str
    query: str
    songs_texts: List[SongText]


class OutgoingMessage(TypedDict):
    id: str
    user_id: str
    response: str


class ResponseTrack(TypedDict):
    track_id: str
    artist_name: str
    track_name: str
    genre: str
    release_date: int
    topic: str
    lyrics: str
    score: float
    danceability: float
    energy: float
    valence: float
    acousticness: float
    instrumentalness: float
    loudness: float
