"""Pydantic модели для запросов и ответов."""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class TrackResult(BaseModel):
    """Результат поиска - один трек."""

    track_id: str
    artist_name: str
    track_name: str
    genre: Optional[str] = None
    release_date: Optional[int] = None
    topic: Optional[str] = None
    lyrics: Optional[str] = None
    score: float = Field(..., description="Релевантность результата")
    danceability: Optional[float] = None
    energy: Optional[float] = None
    valence: Optional[float] = None
    acousticness: Optional[float] = None
    instrumentalness: Optional[float] = None
    loudness: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "track_id": "123",
                "artist_name": "The Beatles",
                "track_name": "Hey Jude",
                "genre": "rock",
                "release_date": 1968,
                "topic": "romantic",
                "score": 12.5,
                "danceability": 0.7,
                "energy": 0.8,
            }
        }


class SearchRequest(BaseModel):
    """Запрос на поиск."""

    query: str = Field(..., description="Поисковый запрос", min_length=1)
    size: int = Field(10, ge=1, le=100, description="Количество результатов")
    search_fields: Optional[List[str]] = Field(
        None, description="Поля для поиска (artist_name, track_name, lyrics)"
    )
    filters: Optional[Dict[str, Any]] = Field(
        None, description="Фильтры (genre, topic, release_date и т.д.)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "love",
                "size": 10,
                "search_fields": ["artist_name", "track_name", "lyrics"],
                "filters": {"genre": "pop", "release_date": {"gte": 2000}},
            }
        }


class SearchResponse(BaseModel):
    """Ответ на поисковый запрос."""

    total: int = Field(..., description="Общее количество найденных результатов")
    results: List[TrackResult] = Field(..., description="Список результатов")
    query: str = Field(..., description="Исходный запрос")
    took: Optional[int] = Field(None, description="Время выполнения запроса в мс")

    class Config:
        json_schema_extra = {
            "example": {"total": 150, "results": [], "query": "love", "took": 25}
        }


class HealthResponse(BaseModel):
    """Ответ на проверку здоровья сервиса."""

    status: str
    index_name: str
    index_exists: bool
    document_count: Optional[int] = None
