import json


with open('telegram_bot/assets/secure/config.json') as file:
    data = json.load(file)
    TOKEN = data['token']
    MUSIC_TOKEN = data['music_token']
    OSU_TOKEN = data['osu_token']
