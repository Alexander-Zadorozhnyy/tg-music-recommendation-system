"""Сервис для поиска по музыкальному индексу."""
from typing import List, Optional, Dict, Any
from app.services.opensearch_service import opensearch_service
from app.models.schemas import TrackResult, SearchResponse


class SearchService:
    """Сервис для поиска."""
    
    def __init__(self):
        """Инициализация сервиса."""
        self.opensearch = opensearch_service
    
    def search(
        self,
        query: str,
        size: int = 10,
        search_fields: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> SearchResponse:
        """
        Выполняет поиск по музыкальному индексу.
        
        Args:
            query: Поисковый запрос
            size: Количество результатов
            search_fields: Поля для поиска
            filters: Фильтры для запроса
            
        Returns:
            Результаты поиска
        """
        response = self.opensearch.search(
            query=query,
            size=size,
            search_fields=search_fields,
            filters=filters,
        )
        
        total = response["hits"]["total"]["value"]
        took = response.get("took")
        hits = response["hits"]["hits"]
        
        results = []
        for hit in hits:
            source = hit["_source"]
            result = TrackResult(
                track_id=source.get("track_id", ""),
                artist_name=source.get("artist_name", ""),
                track_name=source.get("track_name", ""),
                genre=source.get("genre"),
                release_date=source.get("release_date"),
                topic=source.get("topic"),
                lyrics=source.get("lyrics"),
                score=hit.get("_score", 0.0),
                danceability=source.get("danceability"),
                energy=source.get("energy"),
                valence=source.get("valence"),
                acousticness=source.get("acousticness"),
                instrumentalness=source.get("instrumentalness"),
                loudness=source.get("loudness"),
            )
            results.append(result)
        
        return SearchResponse(
            total=total,
            results=results,
            query=query,
            took=took,
        )
    
    def get_track(self, track_id: str) -> Optional[TrackResult]:
        """
        Получает трек по ID.
        
        Args:
            track_id: ID трека
            
        Returns:
            Информация о треке или None
        """
        source = self.opensearch.get_track_by_id(track_id)
        if not source:
            return None
        
        return TrackResult(
            track_id=source.get("track_id", track_id),
            artist_name=source.get("artist_name", ""),
            track_name=source.get("track_name", ""),
            genre=source.get("genre"),
            release_date=source.get("release_date"),
            topic=source.get("topic"),
            lyrics=source.get("lyrics"),
            score=0.0,
            danceability=source.get("danceability"),
            energy=source.get("energy"),
            valence=source.get("valence"),
            acousticness=source.get("acousticness"),
            instrumentalness=source.get("instrumentalness"),
            loudness=source.get("loudness"),
        )


search_service = SearchService()

