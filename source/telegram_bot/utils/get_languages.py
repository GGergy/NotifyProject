import json
import os


def get():
    response = {}
    names = {}
    for file in list(os.walk('telegram_bot/assets/languages'))[0][2]:
        with open(f'telegram_bot/assets/languages/{file}', encoding='utf-8') as json_file:
            data = json.load(json_file)
            response[data['meta']['id']] = data['data']
            names[data['meta']['id']] = data['meta']['name']
    return response, names
