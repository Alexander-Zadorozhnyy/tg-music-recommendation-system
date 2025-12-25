from collections import Counter
from typing import List
from src.models import SongText


def extract_aggregates(songs_texts: List[dict]):
    genres = [s.get("genre") for s in songs_texts if s.get("genre")]
    years = [s.get("release_date") for s in songs_texts if s.get("release_date")]
    all_topics = [s.get("topic") for s in songs_texts if s.get("topic")]

    top_genre = Counter(genres).most_common(1)[0][0] if genres else "разная музыка"
    decade = f"{(min(years) // 10) * 10}-х" if years else "разных лет"
    top_themes = ", ".join(all_topics)

    return top_genre, decade, top_themes


def build_recommendation_prompt(songs_texts: List[dict]) -> str:
    top_genre, decade, top_themes = extract_aggregates(songs_texts)

    tracks_list = "\n".join(
        f"- {s['artist_name']} — {s['track_name']} ({s.get('genre', 'жанр неизвестен')}, {s.get('release_date', '?')})"
        for s in songs_texts[:5]
    )

    prompt = f"""На основе следующих треков пользователю были подобраны рекомендации:

    {tracks_list}

    Общие темы: {top_themes or 'не определены'}.

    Сформируй дружелюбную, краткую и персонализированную рекомендацию в стиле:
    "Похоже, вам нравится {top_genre} музыка про {top_themes}. Тогда вам обязательно понравятся эти хиты {decade}:
    1) {songs_texts[0]['artist_name']} — {songs_texts[0]['track_name']}: [описание]
    2) {songs_texts[1]['artist_name']} — {songs_texts[1]['track_name']}: [описание]
    3) {songs_texts[2]['artist_name']} — {songs_texts[2]['track_name']}: [описание]
    4) {songs_texts[3]['artist_name']} — {songs_texts[3]['track_name']}: [описание]
    5) {songs_texts[4]['artist_name']} — {songs_texts[4]['track_name']}: [описание]
    ...

    Не выдумывай новые треки — используй только те, что в списке.
    Ответ должен содержать только текст рекомендации, без пояснений."""

    return prompt
