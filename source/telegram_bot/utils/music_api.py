import requests
import yandex_music
from bs4 import BeautifulSoup
from . import config
from .hope_dict import HopeDict


conn = yandex_music.Client(token=config.MUSIC_TOKEN)
conn.init()
title_cache = HopeDict()
link_cache = HopeDict()


def search(query):
    tracks_id = parse_link(query)
    if tracks_id:
        return [{"id": track_id, "name": get_metadata(track_id)} for track_id in tracks_id]
    response = []
    answer = conn.search(text=query, type_='all')
    if not answer.tracks:
        return []
    for item in answer.tracks.results[:10]:
        if isinstance(item.id, int):
            response.append({"id": item.id, "name": f'{item.title} - {", ".join([i.name for i in item.artists])}'})
    return response


def get_link(track_id):
    if link_cache[track_id]:
        return link_cache[track_id]
    link = conn.tracks_download_info(track_id=track_id, get_direct_links=True)[0].direct_link
    link_cache[track_id] = link
    return link


def get_metadata(track_id):
    if title_cache[track_id]:
        return title_cache[track_id]
    track = conn.tracks([track_id])[0]
    name = f'{track.title} - {", ".join([i.name for i in track.artists])}'
    title_cache[track_id] = name
    return name


def parse_link(link):
    if not link.startswith('https://music.yandex.ru/'):
        return False
    if link.startswith('https://music.yandex.ru/album/') and 'track' in link:
        try:
            re = link.split('/')[6]
            return [int(re[:re.index('?')])]
        except Exception:
            pass
    try:
        response = requests.get(link)
        soup = BeautifulSoup(response.content, 'html.parser')
        ids = soup.find_all(lambda tag: tag.get('class') and 'd-track' in tag.get('class'))
        return [int(item.get('data-item-id')) for item in ids][:40]
    except Exception as e:
        print('link parse failed', e)
        return False


def get_text(track_id):
    name = get_metadata(track_id)
    try:
        response = requests.get("https://genius.com/api/search/song", params={"q": name}).json()
        url = response['response']['sections'][0]['hits'][0]['result']['url']
        response = requests.get(url).content
        soup = BeautifulSoup(response, 'html.parser')
        texts = soup.find_all(lambda tag: tag.get('class') == ['Lyrics__Container-sc-1ynbvzw-5', 'Dzxov'])
        data = [item.get_text() for txt in texts for item in txt if item.get_text()]
        return '\n'.join(data)[:4000]
    except:
        return False
