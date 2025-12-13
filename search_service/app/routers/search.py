"""Роутер для поиска."""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List, Dict, Any

from app.models.schemas import SearchRequest, SearchResponse, TrackResult
from app.services.search_service import search_service
from app.services.opensearch_service import opensearch_service

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse, summary="Поиск по музыкальному индексу")
async def search(request: SearchRequest) -> SearchResponse:
    """
    Выполняет поиск по музыкальному индексу.

    Поддерживает:
    - Текстовый поиск по артистам, названиям треков и текстам песен
    - Фильтрацию по жанру, теме, году выпуска и другим параметрам
    - Ngram поиск для частичных совпадений
    """
    try:
        return search_service.search(
            query=request.query,
            size=request.size,
            search_fields=request.search_fields,
            filters=request.filters,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")


@router.get("", response_model=SearchResponse, summary="Поиск через GET запрос")
async def search_get(
    q: str = Query(..., description="Поисковый запрос", min_length=1),
    size: int = Query(10, ge=1, le=100, description="Количество результатов"),
    genre: Optional[str] = Query(None, description="Фильтр по жанру"),
    topic: Optional[str] = Query(None, description="Фильтр по теме"),
    year_from: Optional[int] = Query(None, description="Год выпуска от"),
    year_to: Optional[int] = Query(None, description="Год выпуска до"),
) -> SearchResponse:
    """
    Выполняет поиск через GET запрос (удобно для тестирования).
    """
    filters = {}
    if genre:
        filters["genre"] = genre
    if topic:
        filters["topic"] = topic
    if year_from or year_to:
        release_date_filter = {}
        if year_from:
            release_date_filter["gte"] = year_from
        if year_to:
            release_date_filter["lte"] = year_to
        filters["release_date"] = release_date_filter

    try:
        return search_service.search(
            query=q,
            size=size,
            filters=filters if filters else None,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка поиска: {str(e)}")


@router.get(
    "/track/{track_id}", response_model=TrackResult, summary="Получить трек по ID"
)
async def get_track(track_id: str) -> TrackResult:
    """
    Получает информацию о треке по его ID.
    """
    track = search_service.get_track(track_id)
    if not track:
        raise HTTPException(status_code=404, detail=f"Трек с ID {track_id} не найден")
    return track
