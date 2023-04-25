import ossapi
import requests
import difflib
from ossapi import Ossapi
from bs4 import BeautifulSoup
from . import config


client = Ossapi(21022, client_secret=config.OSU_TOKEN)
COEFF = 0.85


def parse_link(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        names = [elem.text.strip() for elem in soup.findAll(lambda tag: tag.get('class') == ['d-track__name'])]
        artists = [elem.text.strip() for elem in soup.findAll(lambda tag: tag.get('class') == ['d-track__artists'])]
        return [f'{names[i]} - {artists[i]}' for i in range(len(names))]
    except Exception as e:
        print('link parse failed', e)
        return []


def get_osu(data):
    total_response = {}
    for request in data:
        response = client.search_beatmapsets(query=request, category=ossapi.BeatmapsetSearchCategory.ANY).beatmapsets[0]
        name = f'{response.title} - {response.artist}'
        ratio = difflib.SequenceMatcher(None, request.lower(), name.strip().lower()).ratio()
        if ratio >= COEFF:
            total_response[request] = {"url": f'https://osu.ppy.sh/beatmapsets/{response.id}',
                                       "ccd": f'{round(ratio * 100, 2)}%'}
    return total_response


def get_res(raw=None, url=None):
    if url:
        raw = parse_link(url)
    res = get_osu(raw)
    return res
