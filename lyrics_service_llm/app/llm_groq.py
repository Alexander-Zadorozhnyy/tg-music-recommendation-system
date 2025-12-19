# app/llm_groq.py
import os
import json
import requests
from typing import Any, Dict, List

from dotenv import load_dotenv

load_dotenv()  # важно: чтобы локальный запуск тоже видел .env


class GroqError(RuntimeError):
    pass


def _get_cfg():
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    model = os.getenv("GROQ_MODEL", "llama-3.1-70b-versatile").strip()
    base_url = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1").strip()
    return api_key, model, base_url


def _clean_lyrics_for_llm(text: str, limit: int = 1800) -> str:
    if not text:
        return ""
    t = text.replace("\r", "\n")
    t = "\n".join([ln.strip() for ln in t.splitlines() if ln.strip()])
    return t[:limit]


def _neutral_result(songs: List[Dict[str, str]], query: str = "") -> Dict[str, Any]:
    # чтобы воркер никогда не "молчал" из-за исключения
    out = []
    for s in songs:
        out.append({
            "artist": s.get("artist", ""),
            "track": s.get("track", ""),
            "summary": "Insufficient text was available to infer detailed themes confidently.",
            "keywords": ["unclear", "missing text", "fragmented", "neutral", "unknown"]
        })
    return {"query": query or "mixed emotions and unresolved tension across fragmented, incomplete lyrical snapshots", "songs_texts": out}


def analyze_songs_with_llm(songs: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    songs: [{artist, track, lyrics}]
    returns строго:
    {
      "query": "...",
      "songs_texts": [{"artist","track","summary","keywords":[...]}]
    }
    """
    api_key, model, base_url = _get_cfg()
    if not api_key:
        # НЕ падаем — иначе воркер умирает и ты "не получаешь ответа"
        return _neutral_result(songs, query="unable to analyze themes because LLM API key is missing")

    compact = [{
        "artist": s.get("artist", ""),
        "track": s.get("track", ""),
        "lyrics": _clean_lyrics_for_llm(s.get("lyrics", "")),
    } for s in songs]

    system = (
        "You are a music-lyrics analyst. Output MUST be valid JSON only. "
        "No markdown. No explanations. No extra keys. English only.\n"
        "Rules:\n"
        "1) query: 12–15 words, a natural sentence about emotions/themes. "
        "No leading words like 'Analyzing', 'Analysis', 'Themes', 'Keywords'.\n"
        "2) For each song: summary is 2–3 sentences, 25–40 words total. "
        "Include emotional tone + situation/conflict + one vivid detail. "
        "Do NOT mention 'lyrics' or 'song'.\n"
        "3) keywords: exactly 3 items; lowercase; 1–2 words each; meaningful.\n"
        "4) If lyrics are empty or error-like, keep summary neutral and keywords generic.\n"
        "JSON schema:\n"
        "{\"query\":\"...\",\"songs_texts\":[{\"artist\":\"\",\"track\":\"\",\"summary\":\"\",\"keywords\":[\"\"]}]}"
    )

    payload = {
        "model": model,
        "temperature": 0.2,
        "max_tokens": 350,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": json.dumps({"songs": compact}, ensure_ascii=False)},
        ],
        # response_format иногда у Groq работает не везде; лучше не ломать весь воркер из-за этого
    }

    url = f"{base_url}/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}

    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        if r.status_code >= 400:
            return _neutral_result(songs, query=f"LLM request failed with HTTP {r.status_code}")
        data = r.json()
        content = data["choices"][0]["message"]["content"]
        obj = json.loads(content)

        if not isinstance(obj, dict) or "query" not in obj or "songs_texts" not in obj:
            return _neutral_result(songs, query="LLM returned invalid JSON schema")

        return obj

    except Exception:
        return _neutral_result(songs, query="LLM analysis timed out or failed unexpectedly")
