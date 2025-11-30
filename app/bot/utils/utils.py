import re


async def smart_parse_tracks_input(text: str) -> list:
    """
    Smart parsing of tracks with different formats
    """
    tracks = []
    lines = text.strip().split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Deleting the numbering (1., 2., etc.)
        line = re.sub(r'^\d+[\.\)]\s*', '', line)
        
        # Try different separators
        separators = [' - ', ' – ', ' — ', ' : ', ' | ']
        
        for sep in separators:
            if sep in line:
                parts = line.split(sep, 1)
                artist = parts[0].strip()
                title = parts[1].strip()
                
                if artist and title:
                    tracks.append(f"{artist} - {title}")
                    break
        else:
            # If the separator is not found, but the string looks like a track
            if len(line) > 3 and any(char.isalpha() for char in line):
                tracks.append(line)
    
    return tracks


def get_response_based_on_similar_tracks(tracks: list, similar_tracks: list):
    if not similar_tracks:
        return '❌ Не удалось найти похожие треки. Попробуйте другие исполнителей или названия.'
    
    response = f'🎵 На основе ваших {len(tracks)} треков:\n\n'
    
    # Показываем введенные треки
    response += '📋 Ваши треки:\n'
    for i, track in enumerate(tracks, 1):
        response += f'{i}. {track}\n'
    
    # Показываем рекомендации
    response += f'\n🎧 Похожие рекомендации ({len(similar_tracks)}):\n'
    for i, track in enumerate(similar_tracks[:15], 1):
        artist, title, similarity = track
        response += f'{i}. {artist} - {title}'
        if similarity:
            response += f' (схожесть: {similarity}%)'
        response += '\n'
    
    return response


def get_response_based_on_free_form_request(user_request: str, recommendations):
    response = f'🎵 Рекомендации по запросу "{user_request}":\n\n'
    for i, track in enumerate(recommendations[:10], 1):
        response += f"{i}. {track}\n"
    
    return response