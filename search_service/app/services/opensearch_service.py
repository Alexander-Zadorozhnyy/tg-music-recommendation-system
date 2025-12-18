"""Сервис для работы с OpenSearch."""
from typing import Dict, Any, Optional
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests.auth import HTTPBasicAuth

from config import settings


class OpenSearchService:
    """Сервис для работы с OpenSearch."""

    def __init__(self):
        """Инициализация клиента OpenSearch."""
        self.client = self._create_client()
        self.index_name = settings.INDEX_NAME

    def _create_client(self) -> OpenSearch:
        """Создаёт клиент OpenSearch."""
        auth = HTTPBasicAuth(
            settings.OPENSEARCH_USER, settings.OPENSEARCH_INITIAL_ADMIN_PASSWORD
        )
        client = OpenSearch(
            hosts=[settings.OPENSEARCH_URL],
            http_compress=True,
            http_auth=auth,
            use_ssl=settings.OPENSEARCH_URL.startswith("https://"),
            verify_certs=False,
            connection_class=RequestsHttpConnection,
            timeout=60,
            max_retries=3,
            retry_on_timeout=True,
        )
        return client

    def index_exists(self) -> bool:
        """Проверяет существование индекса."""
        return self.client.indices.exists(index=self.index_name)

    def get_document_count(self) -> Optional[int]:
        """Получает количество документов в индексе."""
        try:
            if not self.index_exists():
                return None
            response = self.client.count(index=self.index_name)
            return response.get("count", 0)
        except Exception:
            return None

    def search(
        self,
        query: str,
        size: int = 10,
        search_fields: Optional[list] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Выполняет поиск по индексу.

        Args:
            query: Поисковый запрос
            size: Количество результатов
            search_fields: Поля для поиска
            filters: Фильтры для запроса

        Returns:
            Результаты поиска от OpenSearch
        """
        if search_fields is None:
            search_fields = ["artist_name", "track_name", "lyrics"]

        search_body = self._build_search_query(query, search_fields, filters)
        search_body["size"] = size
        search_body["_source"] = [
            "track_id",
            "artist_name",
            "track_name",
            "genre",
            "release_date",
            "topic",
            "lyrics",
            "danceability",
            "energy",
            "valence",
            "acousticness",
            "instrumentalness",
            "loudness",
        ]

        response = self.client.search(index=self.index_name, body=search_body)
        return response

    def _build_search_query(
        self,
        query: str,
        search_fields: list,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Строит поисковый запрос."""
        text_query = {
            "multi_match": {
                "query": query,
                "fields": [f"{field}^2" for field in search_fields]
                + [f"{field}.ngram" for field in search_fields],
                "type": "best_fields",
                "fuzziness": "AUTO",
            }
        }

        field_queries = []
        for field in search_fields:
            boost = 3.0 if field == "lyrics" else 2.0
            field_queries.append(
                {
                    "match": {
                        field: {
                            "query": query,
                            "boost": boost,
                        }
                    }
                }
            )

        should_clauses = [text_query] + field_queries

        must_clauses = []
        if filters:
            must_clauses.extend(self._build_filters(filters))

        query_dict = {
            "bool": {
                "should": should_clauses,
                "minimum_should_match": 1,
            }
        }

        if must_clauses:
            query_dict["bool"]["must"] = must_clauses

        return {"query": query_dict}

    def _build_filters(self, filters: Dict[str, Any]) -> list:
        """Строит фильтры для запроса."""
        filter_clauses = []

        for field, value in filters.items():
            if field == "genre":
                filter_clauses.append({"term": {"genre": value}})
            elif field == "topic":
                filter_clauses.append({"term": {"topic": value}})
            elif field == "release_date":
                if isinstance(value, dict):
                    filter_clauses.append({"range": {"release_date": value}})
                else:
                    filter_clauses.append({"term": {"release_date": value}})
            elif field in ["danceability", "energy", "valence", "acousticness"]:
                if isinstance(value, dict):
                    filter_clauses.append({"range": {field: value}})
                else:
                    filter_clauses.append({"term": {field: value}})

        return filter_clauses

    def get_track_by_id(self, track_id: str) -> Optional[Dict[str, Any]]:
        """Получает трек по ID."""
        try:
            response = self.client.get(index=self.index_name, id=track_id)
            return response.get("_source")
        except Exception:
            return None


opensearch_service = OpenSearchService()
