"""Роутер для проверки здоровья сервиса."""
from fastapi import APIRouter
from app.models.schemas import HealthResponse
from app.services.opensearch_service import opensearch_service
from app.config import settings

router = APIRouter(prefix="/health", tags=["health"])


@router.get("", response_model=HealthResponse, summary="Проверка здоровья сервиса")
async def health_check() -> HealthResponse:
    """
    Проверяет состояние сервиса и подключение к OpenSearch.
    """
    index_exists = opensearch_service.index_exists()
    document_count = opensearch_service.get_document_count() if index_exists else None
    
    status = "healthy" if index_exists else "unhealthy"
    
    return HealthResponse(
        status=status,
        index_name=settings.INDEX_NAME,
        index_exists=index_exists,
        document_count=document_count,
    )

