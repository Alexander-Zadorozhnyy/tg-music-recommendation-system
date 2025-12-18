import os
import re
import json
from typing import List, Dict, Any
import pandas as pd

import numpy as np
from tqdm import tqdm
import requests
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

from config import settings

dotenv_path = os.path.join(os.getcwd(), ".env")

if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

try:
    settings.validate()
except ValueError as e:
    import sys

    print(f"ОШИБКА КОНФИГУРАЦИИ: {e}", file=sys.stderr)
    sys.exit(1)

print("✓ Все настройки проверены")
print(f"OpenSearch: {settings.OPENSEARCH_URL}, index: {settings.INDEX_NAME}")
print(f"CSV_FILE: {settings.CSV_FILE}")
print(f"Yandex folder: {settings.YANDEX_FOLDER_ID}")
print(f"Yandex embed model: {settings.YANDEX_EMBED_MODEL}")


def create_client(url: str, user: str, password: str) -> OpenSearch:
    auth = HTTPBasicAuth(user, password) if user and password else None
    client = OpenSearch(
        hosts=[url],
        http_compress=True,
        http_auth=auth,
        use_ssl=url.startswith("https://"),
        verify_certs=False,
        connection_class=RequestsHttpConnection,
        timeout=60,
        max_retries=3,
        retry_on_timeout=True,
    )
    return client


client = create_client(
    settings.OPENSEARCH_URL,
    settings.OPENSEARCH_USER,
    settings.OPENSEARCH_INITIAL_ADMIN_PASSWORD,
)

MODEL_URI = f"emb://{settings.YANDEX_FOLDER_ID}/{settings.YANDEX_EMBED_MODEL}/latest"
print(f"Yandex Model URI: {MODEL_URI}")


def yandex_embed_one(text: str) -> List[float]:
    body = {"modelUri": MODEL_URI, "text": text}
    headers = {
        "Authorization": f"Api-Key {settings.YANDEX_API_KEY}",
        "x-folder-id": settings.YANDEX_FOLDER_ID,
        "Content-Type": "application/json",
    }
    resp = requests.post(
        settings.YANDEX_EMBEDDINGS_URL, headers=headers, json=body, timeout=60
    )
    resp.raise_for_status()
    data = resp.json()
    emb = data.get("embedding") or (data.get("result") or {}).get("embedding")
    if emb is None:
        raise RuntimeError(f"Bad embedding response: {data}")
    return emb


INDEX_BODY: Dict[str, Any] = {
    "settings": {
        "index": {
            "number_of_shards": 1,
            "number_of_replicas": 0,
            "max_ngram_diff": 8,  # Разрешаем разницу между max_gram (10) и min_gram (2)
            "similarity": {
                "custom_similarity": {
                    "type": "BM25",
                    "k1": 1.2,
                    "b": 0.75,
                    "discount_overlaps": "true",
                }
            },
            "analysis": {
                "filter": {
                    "russian_stemmer": {"type": "stemmer", "language": "russian"},
                    "unique_pos": {"type": "unique", "only_on_same_position": False},
                    "my_multiplexer": {
                        "type": "multiplexer",
                        "filters": [
                            "keyword_repeat",
                            "russian_stemmer",
                            "remove_duplicates",
                        ],
                    },
                    "ngram_filter": {
                        "type": "ngram",
                        "min_gram": 2,
                        "max_gram": 10,
                        "token_chars": ["letter", "digit"],
                    },
                },
                "analyzer": {
                    "search_text_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "my_multiplexer", "unique_pos"],
                        "char_filter": ["e_mapping"],
                    },
                    "ru_international_translit_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "russian_stemmer",
                        ],
                        "char_filter": ["transliteration_filter", "e_mapping"],
                    },
                    "text_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": [
                            "lowercase",
                            "russian_stemmer",
                        ],
                        "char_filter": ["e_mapping"],
                    },
                    "exact_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase"],
                        "char_filter": ["e_mapping"],
                    },
                    "ngram_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "ngram_filter"],
                    },
                    "ngram_search_analyzer": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase", "ngram_filter"],
                    },
                    "text_standard": {"type": "standard"},
                    "text_whitespace": {"type": "whitespace"},
                    "text_lowercase": {
                        "type": "custom",
                        "tokenizer": "standard",
                        "filter": ["lowercase"],
                    },
                },
                "char_filter": {
                    "transliteration_filter": {
                        "type": "mapping",
                        "mappings": [
                            "a => а",
                            "b => б",
                            "v => в",
                            "g => г",
                            "d => д",
                            "e => е",
                            "ye => ё",
                            "zh => ж",
                            "z => з",
                            "i => и",
                            "j => й",
                            "k => к",
                            "l => л",
                            "m => м",
                            "n => н",
                            "o => о",
                            "p => п",
                        ],
                    },
                    "e_mapping": {"type": "mapping", "mappings": ["e => ё"]},
                },
            },
        }
    },
    "mappings": {
        "properties": {
            "artist_name": {
                "type": "text",
                "analyzer": "text_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"},
                    "ngram": {
                        "type": "text",
                        "analyzer": "ngram_analyzer",
                        "search_analyzer": "ngram_search_analyzer",
                    },
                },
            },
            "track_name": {
                "type": "text",
                "analyzer": "text_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"},
                    "ngram": {
                        "type": "text",
                        "analyzer": "ngram_analyzer",
                        "search_analyzer": "ngram_search_analyzer",
                    },
                },
            },
            "lyrics": {
                "type": "text",
                "analyzer": "text_analyzer",
                "similarity": "BM25",
                "fields": {
                    "ngram": {
                        "type": "text",
                        "analyzer": "ngram_analyzer",
                        "search_analyzer": "ngram_search_analyzer",
                    },
                },
            },
            "genre": {"type": "keyword"},
            "release_date": {"type": "integer"},
            "topic": {"type": "keyword"},
            "age": {"type": "float"},
            "danceability": {"type": "float"},
            "energy": {"type": "float"},
            "valence": {"type": "float"},
            "acousticness": {"type": "float"},
            "instrumentalness": {"type": "float"},
            "loudness": {"type": "float"},
            "len": {"type": "integer"},
            "dating": {"type": "float"},
            "violence": {"type": "float"},
            "world_life": {"type": "float"},
            "night_time": {"type": "float"},
            "shake_the_audience": {"type": "float"},
            "family_gospel": {"type": "float"},
            "romantic": {"type": "float"},
            "communication": {"type": "float"},
            "obscene": {"type": "float"},
            "music": {"type": "float"},
            "movement_places": {"type": "float"},
            "light_visual_perceptions": {"type": "float"},
            "family_spiritual": {"type": "float"},
            "like_girls": {"type": "float"},
            "sadness": {"type": "float"},
            "feelings": {"type": "float"},
            "track_id": {"type": "keyword"},
        }
    },
}

if client.indices.exists(index=settings.INDEX_NAME):
    print(f"Index {settings.INDEX_NAME} exists. Deleting...")
    client.indices.delete(index=settings.INDEX_NAME)

print(f"Creating index {settings.INDEX_NAME}...")
client.indices.create(index=settings.INDEX_NAME, body=INDEX_BODY)
print("Index created")


def load_music_data(csv_path: str) -> List[Dict[str, Any]]:
    """Загружает данные из CSV и создаёт документы для индексации."""
    df = pd.read_csv(csv_path)

    docs: List[Dict[str, Any]] = []

    print(f"Loading {len(df)} tracks from CSV...")

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing tracks"):
        # Создаём эмбеддинг для текста песни
        lyrics_text = str(row.get("lyrics", "")).strip()
        if not lyrics_text or lyrics_text == "nan":
            lyrics_text = ""

        # Подготавливаем документ
        doc = {
            "track_id": str(row.get("Unnamed: 0", idx)),
            "artist_name": str(row.get("artist_name", "")),
            "track_name": str(row.get("track_name", "")),
            "lyrics": lyrics_text,
            "genre": str(row.get("genre", "")),
            "release_date": int(row.get("release_date", 0))
            if pd.notna(row.get("release_date"))
            else None,
            "topic": str(row.get("topic", "")),
            "age": float(row.get("age", 0)) if pd.notna(row.get("age")) else None,
            "danceability": float(row.get("danceability", 0))
            if pd.notna(row.get("danceability"))
            else None,
            "energy": float(row.get("energy", 0))
            if pd.notna(row.get("energy"))
            else None,
            "valence": float(row.get("valence", 0))
            if pd.notna(row.get("valence"))
            else None,
            "acousticness": float(row.get("acousticness", 0))
            if pd.notna(row.get("acousticness"))
            else None,
            "instrumentalness": float(row.get("instrumentalness", 0))
            if pd.notna(row.get("instrumentalness"))
            else None,
            "loudness": float(row.get("loudness", 0))
            if pd.notna(row.get("loudness"))
            else None,
            "len": int(row.get("len", 0)) if pd.notna(row.get("len")) else None,
            "dating": float(row.get("dating", 0))
            if pd.notna(row.get("dating"))
            else None,
            "violence": float(row.get("violence", 0))
            if pd.notna(row.get("violence"))
            else None,
            "world_life": float(row.get("world/life", 0))
            if pd.notna(row.get("world/life"))
            else None,
            "night_time": float(row.get("night/time", 0))
            if pd.notna(row.get("night/time"))
            else None,
            "shake_the_audience": float(row.get("shake the audience", 0))
            if pd.notna(row.get("shake the audience"))
            else None,
            "family_gospel": float(row.get("family/gospel", 0))
            if pd.notna(row.get("family/gospel"))
            else None,
            "romantic": float(row.get("romantic", 0))
            if pd.notna(row.get("romantic"))
            else None,
            "communication": float(row.get("communication", 0))
            if pd.notna(row.get("communication"))
            else None,
            "obscene": float(row.get("obscene", 0))
            if pd.notna(row.get("obscene"))
            else None,
            "music": float(row.get("music", 0)) if pd.notna(row.get("music")) else None,
            "movement_places": float(row.get("movement/places", 0))
            if pd.notna(row.get("movement/places"))
            else None,
            "light_visual_perceptions": float(row.get("light/visual perceptions", 0))
            if pd.notna(row.get("light/visual perceptions"))
            else None,
            "family_spiritual": float(row.get("family/spiritual", 0))
            if pd.notna(row.get("family/spiritual"))
            else None,
            "like_girls": float(row.get("like/girls", 0))
            if pd.notna(row.get("like/girls"))
            else None,
            "sadness": float(row.get("sadness", 0))
            if pd.notna(row.get("sadness"))
            else None,
            "feelings": float(row.get("feelings", 0))
            if pd.notna(row.get("feelings"))
            else None,
        }

        docs.append(doc)

    return docs


if not os.path.isfile(settings.CSV_FILE):
    raise FileNotFoundError(f"CSV file not found: {settings.CSV_FILE}")

docs = load_music_data(settings.CSV_FILE)
print(f"Total tracks loaded: {len(docs)}")


BULK_ENDPOINT = f"/{settings.INDEX_NAME}/_bulk"
lines: List[str] = []

print(f"Indexing {len(docs)} tracks...")
for i, d in enumerate(tqdm(docs, desc="Preparing bulk")):
    doc_id = d.get("track_id") or f"track-{i}"
    meta = {"index": {"_index": settings.INDEX_NAME, "_id": doc_id}}
    # Удаляем None значения
    src = {k: v for k, v in d.items() if v is not None}
    lines.append(json.dumps(meta, ensure_ascii=False))
    lines.append(json.dumps(src, ensure_ascii=False))

payload = "\n".join(lines) + "\n"
print("Sending bulk request...")
resp = client.transport.perform_request("POST", BULK_ENDPOINT, body=payload)
if isinstance(resp, dict) and resp.get("errors"):
    errs = sum(
        1 for it in resp.get("items", []) if (it.get("index") or {}).get("error")
    )
    print("Bulk completed with errors:", errs)
else:
    print(f"Bulk indexed {len(docs)} tracks into '{settings.INDEX_NAME}'")

# Проверяем количество документов в индексе
count_resp = client.count(index=settings.INDEX_NAME)
print(f"Total documents in index: {count_resp.get('count', 0)}")
