from collections import Counter
from typing import List
from src.models import SongText


def extract_aggregates(songs_texts: List[SongText]):
    genres = [s.get("genre") for s in songs_texts if s.get("genre")]
    years = [s.get("year") for s in songs_texts if s.get("year")]
    all_keywords = [kw for s in songs_texts for kw in s.get("keywords", [])]

    top_genre = Counter(genres).most_common(1)[0][0] if genres else "разная музыка"
    decade = f"{(min(years) // 10) * 10}-х" if years else "разных лет"
    top_themes = ", ".join(list(dict.fromkeys(all_keywords))[:5])

    return top_genre, decade, top_themes


def build_recommendation_prompt(songs_texts: List[SongText]) -> str:
    top_genre, decade, top_themes = extract_aggregates(songs_texts)

    tracks_list = "\n".join(
        f"- {s['artist']} — {s['song']} ({s.get('genre', 'жанр неизвестен')}, {s.get('year', '?')})"
        for s in songs_texts[:5]
    )

    prompt = f"""На основе следующих треков пользователю были подобраны рекомендации:

    {tracks_list}

    Общие темы в текстах: {top_themes or 'не определены'}.

    Сформируй дружелюбную, краткую и персонализированную рекомендацию в стиле:
    "Похоже, вам нравится {top_genre} музыка про {top_themes or 'разные темы'}. Тогда вам обязательно понравятся эти хиты {decade}:
    1) ...
    2) ...
    3) ...
    4) ...
    5) ..."

    Не выдумывай конкретные треки — не называй артистов или названия. Просто опиши суть подборки и дай рекомендацию в таком стиле.
    Ответ должен содержать только текст рекомендации, без пояснений или заголовков."""

    return prompt
