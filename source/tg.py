import telebot
import json
from telebot import types
from telegram_bot.utils import config, get_languages, sqlast_hope, music_api, osu_api


TE = 'Error: text of this message not found in current language pack'
bot = telebot.TeleBot(token=config.TOKEN)
languages, lang_names = get_languages.get()


@bot.message_handler(commands=['start'])
def start(message):
    bot.delete_message(message_id=message.id, chat_id=message.chat.id)
    markup = types.InlineKeyboardMarkup()
    for elem in languages.keys():
        markup.row(types.InlineKeyboardButton(lang_names[elem],
                                              callback_data=json.dumps({'handler': 'language', 'data': elem})))
    mid = bot.send_message(message.chat.id, text='Hello and welcome!<3. Please, choose preferred language to continue:',
                           reply_markup=markup).id
    if not sqlast_hope.user(message.chat.id)[0]:
        sqlast_hope.create_user(chat_id=message.chat.id, message_id=mid)
    else:
        user, session = sqlast_hope.user(message.chat.id)
        try:
            bot.delete_message(chat_id=message.chat.id, message_id=user.message_id)
            bot.delete_message(chat_id=message.chat.id, message_id=user.player_id)
        except telebot.apihelper.ApiTelegramException:
            pass
        user.message_id = mid
        session.commit()
        session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'language')
def language_handler(call):
    language = json.loads(call.data)['data']
    user, session = sqlast_hope.user(call.message.chat.id)
    user.language = language
    session.commit()
    markup = types.InlineKeyboardMarkup()
    b_home = types.InlineKeyboardButton(languages[language].get('home', TE),
                                        callback_data='{"handler": "home"}')
    markup.row(b_home)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=languages[language].get('welcome', TE), reply_markup=markup)
    try:
        mk, caption = generate_player(user)
        bot.edit_message_caption(caption=caption, message_id=user.player_id, chat_id=user.chat_id, reply_markup=mk)
    except telebot.apihelper.ApiTelegramException:
        pass
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'home')
def main_menu(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    user, session = sqlast_hope.user(call.message.chat.id)
    markup.row(types.InlineKeyboardButton(languages[user.language].get('music', TE),
                                          callback_data='{"handler": "music"}'))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('osu', TE),
                                          callback_data='{"handler": "osu"}'))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('settings', TE),
                                          callback_data='{"handler": "settings"}'))
    bot.edit_message_text(chat_id=user.chat_id, message_id=call.message.id,
                          text=languages[user.language].get('home_text', TE), reply_markup=markup)
    user.script = 'home'
    session.commit()
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'settings')
def settings(call):
    user, session = sqlast_hope.user(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(languages[user.language].get('language', TE),
                                          callback_data='{"handler": "set_lang"}'))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('del_ac_b', TE),
                                          callback_data='{"handler": "conf", "data": {"handler": "del_ac"}}'))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=languages[user.language].get('settings_text', TE), reply_markup=markup)
    user.script = 'settings'
    session.commit()
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'osu')
def osu_main(call):
    user, session = sqlast_hope.user(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(languages[user.language].get('osu_parse', TE),
                                          callback_data='{"handler": "osu_parser"}'))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=languages[user.language].get('osu_text', TE), reply_markup=markup)
    user.script = 'osu'
    session.commit()
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'osu_parser')
def osu_parser_main(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    user, session = sqlast_hope.user(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(languages[user.language].get('osu_parse_link', TE),
                                          callback_data='{"handler": "osu_parse_link"}'))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('osu_parse_pl', TE),
                                          callback_data='{"handler": "osu_parse_pl"}'))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE), callback_data='{"handler": "osu"}'),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=languages[user.language].get('osu_parser_text', TE), reply_markup=markup)
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'osu_parse_link')
def osu_to_link(call):
    user, session = sqlast_hope.user(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "osu_parser"}'),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=markup,
                          text=languages[user.language].get('osu_link_text', TE))
    bot.register_next_step_handler(callback=osu_link_searcher, message=call.message)
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'osu_parse_pl')
def osu_playlist_view(call):
    user, session = sqlast_hope.user(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    u = False
    if user.liked != '[]':
        u = True
        markup.row(types.InlineKeyboardButton(languages[user.language].get('liked', TE),
                                              callback_data='{"handler": "osu_start", "data": "--liked"}'))
    for key, value in json.loads(user.playlist_names).items():
        u = True
        markup.row(types.InlineKeyboardButton(value,
                                              callback_data=json.dumps({'handler': 'osu_start', 'data': key})))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "osu_parser"}'),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=markup,
                          text=languages[user.language].get('osu_pl_text' if u else 'empty_playlists', TE))
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'osu_start')
def osu_call_searcher(call):
    user, session = sqlast_hope.user(call.message.chat.id)
    playlist = json.loads(call.data)['data']
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=languages[user.language].get('osu_wait', TE))
    raw = json.loads(user.playlists)[playlist] if playlist != '--liked' else json.loads(user.liked)
    data = [music_api.get_metadata(elem) for elem in raw]
    results = osu_api.get_res(raw=data)
    if not results:
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                              callback_data='{"handler": "osu_parser"}'),
                   types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                              callback_data='{"handler": "home"}'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=markup,
                              text=languages[user.language].get('empty_response', TE))
        return
    markup = types.InlineKeyboardMarkup()
    for key, re in results.items():
        markup.row(types.InlineKeyboardButton(f'{key} - {re["ccd"]}', url=re['url']))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "osu_parser"}'),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=markup,
                          text=languages[user.language].get('search_response_text', TE))
    session.close()


def osu_link_searcher(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    user, session = sqlast_hope.user(message.chat.id)
    bot.edit_message_text(chat_id=message.chat.id, message_id=user.message_id,
                          text=languages[user.language].get('osu_wait', TE))
    results = osu_api.get_res(url=message.text)
    if not results:
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                              callback_data='{"handler": "osu_parser"}'),
                   types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                              callback_data='{"handler": "home"}'))
        bot.edit_message_text(chat_id=message.chat.id, message_id=user.message_id, reply_markup=markup,
                              text=languages[user.language].get('empty_response', TE))
        return
    markup = types.InlineKeyboardMarkup()
    for key, re in results.items():
        markup.row(types.InlineKeyboardButton(f'{key} - {re["ccd"]}', url=re['url']))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "osu_parser"}'),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=message.chat.id, message_id=user.message_id, reply_markup=markup,
                          text=languages[user.language].get('search_response_text', TE))
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'set_lang')
def set_language(call):
    user, session = sqlast_hope.user(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    for elem in languages.keys():
        markup.row(types.InlineKeyboardButton(lang_names[elem],
                                              callback_data=json.dumps({"handler": "language", "data": elem})))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "settings"}'),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=languages[user.language].get('set_lang_text', TE), reply_markup=markup)
    user.script = 'lang'
    session.commit()
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'music')
def music(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    user, session = sqlast_hope.user(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(languages[user.language].get('search', TE),
                                          callback_data='{"handler": "search"}'))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('liked', TE),
                                          callback_data='{"handler": "liked"}'))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('playlists', TE),
                                          callback_data='{"handler": "playlists"}'))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                          text=languages[user.language].get('music_main_text', TE), reply_markup=markup)
    user.script = 'music'
    session.commit()
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'playlists')
def playlists_view(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    user, session = sqlast_hope.user(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    u = False
    if '--lsr' in json.loads(user.playlists):
        u = True
        markup.row(types.InlineKeyboardButton(languages[user.language].get('lsr', TE) + '🎶',
                                              callback_data='{"handler": "playlist", "data": "--lsr"}'))
    for key, elem in json.loads(user.playlist_names).items():
        markup.row(types.InlineKeyboardButton(elem + '🎶',
                                              callback_data=json.dumps({"handler": "playlist", "data": key})))
        u = True
    markup.row(types.InlineKeyboardButton(languages[user.language].get('new_pl', TE),
                                          callback_data='{"handler": "new_pl"}'))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "music"}'),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=markup,
                          text=languages[user.language].get('playlists_text' if u else 'empty_playlists', TE))
    user.script = 'playlists'
    session.commit()
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'playlist')
def playlist_view(call):
    user, session = sqlast_hope.user(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    pl_id = json.loads(call.data)['data']
    buttons = []
    if pl_id != '--lsr':
        buttons.append(types.InlineKeyboardButton(languages[user.language].get('pl_edit', TE),
                                                  callback_data=json.dumps({"handler": "edit_pl", "data": pl_id})))
    tracks = json.loads(user.playlists)[pl_id]
    if tracks and pl_id != '--lsr':
        buttons.append(types.InlineKeyboardButton(languages[user.language].get('share_pl', TE),
                                                  callback_data=json.dumps({'handler': "share_pl", 'data': pl_id})))
    if buttons:
        markup.row(*buttons)
    u = False
    for track in tracks:
        u = True
        like_b = types.InlineKeyboardButton('❤️' if track in json.loads(user.liked) else '🤍',
                                            callback_data=json.dumps({"handler": "like", "data": track}))
        markup.row(types.InlineKeyboardButton(music_api.get_metadata(track),
                                              callback_data=json.dumps({"handler": "play", "track": track,
                                                                        "playlist": pl_id})),
                   like_b)
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "playlists"}'),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    text = json.loads(user.playlist_names)[pl_id] if pl_id != '--lsr' else languages[user.language].get("lsr", TE)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=markup,
                          text=(languages[user.language].get("playlist_text", TE) + text) if u else
                          languages[user.language].get("empty_playlist", TE))
    user.script = f'playlist_view::{pl_id}::s'
    session.commit()
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'liked')
def liked_view(call):
    user, session = sqlast_hope.user(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    tracks = json.loads(user.liked)
    if tracks:
        markup.row(types.InlineKeyboardButton(languages[user.language].get('share_pl', TE),
                                              callback_data='{"handler": "share_pl", "data": "--liked"}'))
    u = False
    for elem in tracks:
        like_b = types.InlineKeyboardButton('❤️', callback_data=json.dumps({"handler": 'like', 'data': elem}))
        markup.row(types.InlineKeyboardButton(music_api.get_metadata(elem),
                                              callback_data=json.dumps({"handler": "play",
                                                                        "track": elem, "playlist": "--liked"})), like_b)
        u = True
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "music"}'),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=markup,
                          text=languages[user.language].get('liked_text' if u else 'empty_liked', TE))
    user.script = 'liked'
    session.commit()
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'search')
def search(call):
    user, session = sqlast_hope.user(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "music"}'),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=markup,
                          text=languages[user.language].get('search_text', TE))
    bot.register_next_step_handler(message=call.message, callback=handle_search)
    user.script = 'search'
    session.commit()
    session.close()


def handle_search(message):
    try:
        bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    except telebot.apihelper.ApiTelegramException:
        pass
    user, session = sqlast_hope.user(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    response = music_api.search(message.text)
    u = False
    for elem in response:
        u = True
        like_b = types.InlineKeyboardButton('❤️' if elem['id'] in json.loads(user.liked) else '🤍',
                                            callback_data=json.dumps({'handler': 'like', 'data': elem['id']}))
        markup.row(types.InlineKeyboardButton(elem['name'],
                                              callback_data=json.dumps({"handler": "play", "track": elem['id'],
                                                                        "playlist": '--lsr'})), like_b)
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "search"}'),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    try:
        bot.edit_message_text(chat_id=message.chat.id, message_id=user.message_id, reply_markup=markup,
                              text=languages[user.language].get('search_response_text' if u else "empty_response", TE))
    except telebot.apihelper.ApiTelegramException:
        pass
    user.script = 'playlist_view::--lsr'
    if u:
        old = json.loads(user.playlists)
        old['--lsr'] = [i['id'] for i in response]
        user.playlists = json.dumps(old)
        if user.playlist == '--lsr' and user.track_id not in json.loads(user.playlists)['--lsr']:
            try:
                mk, caption = generate_player(user)
                bot.edit_message_caption(caption=caption, message_id=user.player_id, chat_id=user.chat_id,
                                         reply_markup=mk)
            except telebot.apihelper.ApiTelegramException:
                pass
    session.commit()
    session.close()


def generate_player(user):
    markup = types.InlineKeyboardMarkup()
    if not user.track_id:
        return markup, ""
    lang = languages[user.language]
    user_pl = json.loads(user.playlists).get(user.playlist, False) if\
        user.playlist != '--liked' else json.loads(user.liked)
    like = types.InlineKeyboardButton('❤️' if user.track_id in json.loads(user.liked) else '🤍',
                                      callback_data=json.dumps({'handler': 'like', 'data': user.track_id}))
    markup.row(types.InlineKeyboardButton('⏮️', callback_data='{"handler": "prew"}'),
               types.InlineKeyboardButton('➕', callback_data='{"handler": "to_pl"}'), like,
               types.InlineKeyboardButton('⏭️', callback_data='{"handler": "next"}'))
    markup.row(types.InlineKeyboardButton("📃", callback_data='{"handler": "text"}'),
               types.InlineKeyboardButton("❌", callback_data='{"handler": "del"}'),
               types.InlineKeyboardButton("🔗", callback_data='{"handler": "share"}'))
    if not user_pl and user_pl != []:
        caption = lang.get('suc_rem', TE)
    else:
        pl_name = json.loads(user.playlist_names)[user.playlist] \
            if '--' not in user.playlist else languages[user.language].get(user.playlist[2:], TE)
        if user.track_id not in user_pl:
            caption = f"{lang.get('from_pl', TE)}{pl_name}\n{lang.get('rem_from_pl', TE)}"
        else:
            index = f'{user_pl.index(user.track_id) + 1}/{len(user_pl)}'
            caption = f"{lang.get('from_pl', TE)}{pl_name}\n{index}"
    return markup, f"{music_api.get_metadata(user.track_id)}\n{caption}"


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'play')
def play(call):
    data = json.loads(call.data)
    track_id, playlist = data['track'], data['playlist']
    link = music_api.get_link(track_id)
    user, session = sqlast_hope.user(call.message.chat.id)
    user.track_id = track_id
    user.playlist = playlist
    session.commit()
    try:
        bot.delete_message(chat_id=call.message.chat.id, message_id=user.player_id)
    except telebot.apihelper.ApiTelegramException:
        pass
    finally:
        markup, caption = generate_player(user)
        pid = bot.send_audio(audio=link, chat_id=call.message.chat.id, reply_markup=markup,
                             caption=caption).id
        user.player_id = pid
        bot.answer_callback_query(callback_query_id=call.id, text=languages[user.language].get('downloaded', TE))
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] in ['next', 'prew'])
def switch_track(call):
    user, session = sqlast_hope.user(call.message.chat.id)
    if not user.playlist:
        bot.answer_callback_query(callback_query_id=call.id, text=languages[user.language].get('raise_end', TE))
        return
    playlist = json.loads(user.liked) if user.playlist == '--liked' else json.loads(user.playlists)[user.playlist]
    index = playlist.index(user.track_id) if user.track_id in playlist else -1
    if json.loads(call.data)['handler'] == 'next':
        if index == -1:
            if not playlist:
                bot.answer_callback_query(callback_query_id=call.id, text=languages[user.language].get('raise_end', TE))
                return
            new_track = playlist[0]
        elif index >= len(playlist) - 1:
            bot.answer_callback_query(callback_query_id=call.id, text=languages[user.language].get('raise_end', TE))
            return
        else:
            new_track = playlist[index + 1]
    else:
        if index == -1:
            if not playlist:
                bot.answer_callback_query(callback_query_id=call.id, text=languages[user.language].get('raise_end', TE))
                return
            new_track = playlist[-1]
        elif index < 1:
            bot.answer_callback_query(callback_query_id=call.id, text=languages[user.language].get('raise_end', TE))
            return
        else:
            new_track = playlist[index - 1]
    markup = call.message.reply_markup
    markup.keyboard[0][2] = types.InlineKeyboardButton(
        '❤️' if new_track in json.loads(user.liked) else '🤍',
        callback_data=json.dumps({'handler': 'like', 'data': new_track}))
    index = f'{playlist.index(new_track) + 1}/{len(playlist)}'
    try:
        bot.delete_message(chat_id=call.message.chat.id, message_id=user.player_id)
    except telebot.apihelper.ApiTelegramException:
        pass
    finally:
        pl_name = json.loads(user.playlist_names)[user.playlist]\
            if '--' not in user.playlist else languages[user.language].get(user.playlist[2:], TE)
        pid = bot.send_audio(audio=music_api.get_link(new_track), chat_id=user.chat_id, reply_markup=markup,
                             caption=f"{music_api.get_metadata(new_track)}\n"
                                     f"{languages[user.language].get('from_pl', TE)}{pl_name}\n{index}").id
        user.player_id = pid
        user.track_id = new_track
        session.commit()
    if user.script == 'track_text':
        text = music_api.get_text(user.track_id)
        if not text:
            bot.answer_callback_query(callback_query_id=call.id, text=languages[user.language].get('fail_text', TE))
            return
        bot.answer_callback_query(callback_query_id=call.id, text="")
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                              callback_data='{"handler": "home"}'))
        bot.edit_message_text(chat_id=user.chat_id, message_id=user.message_id,
                              text=f'{languages[user.language].get("song_text", TE)}'
                                   f' {music_api.get_metadata(user.track_id)}\n{text}', reply_markup=markup)
    session.close()


@bot.message_handler(content_types=['text', 'audio', 'photo', 'video', 'media', 'file', 'voice', 'video_note'])
def deleter(message):
    bot.delete_message(message.chat.id, message.id)
    if not message.text.startswith("notify.prj/"):
        return
    user, session = sqlast_hope.user(message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    if message.text.startswith("notify.prj/share"):
        if len(json.loads(user.liked)) >= 50:
            bot.edit_message_text(chat_id=user.chat_id, message_id=user.message_id, reply_markup=markup,
                                  text=languages[user.language].get('max_track', TE))
            return
        track_id = int(message.text.split('/')[2])
        liked_tracks = json.loads(user.liked)
        if track_id in liked_tracks:
            bot.edit_message_text(chat_id=user.chat_id, message_id=user.message_id, reply_markup=markup,
                                  text=f"{music_api.get_metadata(track_id)}: "
                                       f"{languages[user.language].get('share_already', TE)}")
            return
        liked_tracks.append(track_id)
        user.liked = json.dumps(liked_tracks)
        session.commit()
        try:
            mk, caption = generate_player(user)
            bot.edit_message_caption(chat_id=user.chat_id, message_id=user.player_id, caption=caption, reply_markup=mk)
        except telebot.apihelper.ApiTelegramException:
            pass
        bot.edit_message_text(chat_id=user.chat_id, message_id=user.message_id, reply_markup=markup,
                              text=f"{music_api.get_metadata(track_id)}: "
                                   f"{languages[user.language].get('share_added', TE)}")
    elif message.text.startswith("notify.prj/playlist"):
        if len(json.loads(user.playlist_names).keys()) >= 25:
            bot.edit_message_text(message_id=user.message_id, chat_id=user.chat_id, reply_markup=markup,
                                  text=languages[user.language].get("max_pl"))
            return
        user_id, playlist_id = message.text.split('/')[2:]
        share_user, share_session = sqlast_hope.user(int(user_id))
        data = json.loads(share_user.playlists).get(playlist_id, []) if\
            playlist_id != '--liked' else json.loads(share_user.liked)
        if not data:
            bot.edit_message_text(chat_id=user.chat_id, message_id=user.message_id, reply_markup=markup,
                                  text=languages[user.language].get('empty_share', TE))
            return
        old = json.loads(user.playlists)
        pl_id = str(old.keys()[-1] + 1) if old.keys() else '1'
        old[pl_id] = data
        pl_names = json.loads(user.playlist_names)
        pl_names[pl_id] = "playlist " + bot.get_chat_member(int(user_id), int(user_id)).user.first_name
        user.playlists = json.dumps(old)
        user.playlist_names = json.dumps(pl_names)
        session.commit()
        share_session.close()
        bot.edit_message_text(chat_id=user.chat_id, message_id=user.message_id, reply_markup=markup,
                              text=languages[user.language].get('share_pl_added', TE))
    user.script = 'api'
    session.commit()
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'del')
def del_player(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'like')
def like_track(call):
    user, session = sqlast_hope.user(call.message.chat.id)
    track_id = json.loads(call.data)['data']
    liked_tracks = json.loads(user.liked)
    if track_id in liked_tracks:
        liked_tracks.remove(track_id)
        user.liked = json.dumps(liked_tracks)
    else:
        if len(liked_tracks) >= 50:
            bot.answer_callback_query(callback_query_id=call.id, text=languages[user.language].get('max_track', TE))
            return
        liked_tracks.append(track_id)
        user.liked = json.dumps(liked_tracks)
    session.commit()
    try:
        mk, caption = generate_player(user)
        bot.edit_message_caption(message_id=user.player_id, chat_id=user.chat_id,
                                 caption=caption, reply_markup=mk)
    except telebot.apihelper.ApiTelegramException:
        pass
    if user.script.startswith('playlist_view') and track_id in json.loads(user.playlists)[user.script.split('::')[1]]:
        markup = types.InlineKeyboardMarkup()
        pl = user.script.split('::')[1]
        buttons = []
        if pl != '--lsr':
            buttons.append(types.InlineKeyboardButton(languages[user.language].get('pl_edit', TE),
                                                      callback_data=json.dumps({"handler": "edit_pl", "data": pl})))
        tracks = json.loads(user.playlists)[pl]
        if tracks and pl != '--lsr':
            buttons.append(types.InlineKeyboardButton(languages[user.language].get('share_pl', TE),
                                                      callback_data=json.dumps({'handler': "share_pl", 'data': pl})))
        if buttons:
            markup.row(*buttons)
        u = False
        for track in tracks:
            u = True
            like_b = types.InlineKeyboardButton('❤️' if track in liked_tracks else '🤍',
                                                callback_data=json.dumps({"handler": "like", "data": track}))
            markup.row(types.InlineKeyboardButton(music_api.get_metadata(track),
                                                  callback_data=json.dumps({"handler": "play", "track": track,
                                                                            "playlist": pl})),
                       like_b)
        markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                              callback_data='{"handler": "playlists"}' if
                                              len(user.script.split('::')) == 3 else '{"handler": "search"}'),
                   types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                              callback_data='{"handler": "home"}'))
        text = json.loads(user.playlist_names)[pl] if pl != '--lsr'\
            else languages[user.language].get("lsr", TE)
        texts = ['search_response_text', 'empty_response', ""] if len(user.script.split('::')) == 2 else \
            ['playlist_text', 'empty_playlist', text]
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=user.message_id, reply_markup=markup,
                                  text=(languages[user.language].get(texts[0], TE) + texts[2]) if u else
                                  languages[user.language].get(texts[1], TE))
        except telebot.apihelper.ApiTelegramException:
            pass
    elif user.script == 'liked':
        markup = types.InlineKeyboardMarkup()
        markup.row(types.InlineKeyboardButton(languages[user.language].get('share_pl', TE),
                                              callback_data='{"handler": "share_pl", "data": "--liked"}'))
        tracks = json.loads(user.liked)
        if tracks:
            markup.row(types.InlineKeyboardButton(languages[user.language].get('share_pl', TE),
                                                  callback_data='{"handler": "share_pl", "data": "--liked"}'))
        u = False
        for elem in tracks:
            like_b = types.InlineKeyboardButton('❤️', callback_data=json.dumps({"handler": 'like', 'data': elem}))
            markup.row(types.InlineKeyboardButton(music_api.get_metadata(elem),
                                                  callback_data=json.dumps({"handler": "play",
                                                                            "track": elem, "playlist": "--liked"})),
                       like_b)
            u = True
        markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                              callback_data='{"handler": "music"}'),
                   types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                              callback_data='{"handler": "home"}'))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=user.message_id, reply_markup=markup,
                              text=languages[user.language].get('liked_text' if u else 'empty_liked', TE))
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'new_pl')
def create_playlist(call):
    bot.clear_step_handler_by_chat_id(call.message.chat.id)
    user, session = sqlast_hope.user(call.message.chat.id)
    if len(json.loads(user.playlist_names).keys()) >= 25:
        bot.answer_callback_query(callback_query_id=call.id, text=languages[user.language].get("max_pl"))
        return
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "playlists"}'),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, reply_markup=markup,
                          text=languages[user.language].get('new_pl_text', TE))
    bot.register_next_step_handler(call.message, pl_name_handler)
    session.close()


def pl_name_handler(message):
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    user, session = sqlast_hope.user(message.chat.id)
    playlists = json.loads(user.playlists)
    pl_names = json.loads(user.playlist_names)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "playlists"}'),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    name = message.text
    if len(name) > 10 or '--' in name or name in pl_names.values():
        bot.register_next_step_handler(message, pl_name_handler)
        try:
            bot.edit_message_text(chat_id=message.chat.id, message_id=user.message_id, reply_markup=markup,
                                  text=languages[user.language].get('incorr_pl_name', TE))
        except telebot.apihelper.ApiTelegramException:
            pass
        return
    pl_id = str(playlists.keys()[-1] + 1) if playlists.keys() else '1'
    playlists[pl_id] = []
    pl_names[pl_id] = name
    user.playlists = json.dumps(playlists)
    user.playlist_names = json.dumps(pl_names)
    session.commit()
    bot.edit_message_text(chat_id=message.chat.id, message_id=user.message_id, reply_markup=markup,
                          text=languages[user.language].get('created_pl_text', TE))
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'to_pl')
def add_to_playlist_view(call):
    user, session = sqlast_hope.user(call.message.chat.id)
    track_id = user.track_id
    markup = types.InlineKeyboardMarkup()
    playlists = json.loads(user.playlists)
    names = json.loads(user.playlist_names)
    u = False
    for key, elem in playlists.items():
        bot.answer_callback_query(callback_query_id=call.id, text='')
        if track_id in elem or key == '--lsr':
            continue
        u = True
        markup.row(types.InlineKeyboardButton(names[key], callback_data=json.dumps({'handler': 'add',
                                                                                    'track_id': track_id, 'pl': key})))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "playlists"}'),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    try:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=user.message_id, reply_markup=markup,
                              text=languages[user.language].get('pl_adding_text' if u else 'all_added', TE))
    except telebot.apihelper.ApiTelegramException:
        pass
    user.script = 'adding'
    session.commit()
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'add')
def add_to_pl(call):
    data = json.loads(call.data)
    track_id, playlist = data['track_id'], data['pl']
    user, session = sqlast_hope.user(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "playlists"}'),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    playlists = json.loads(user.playlists)
    if len(playlists[playlist]) == 50:
        bot.answer_callback_query(callback_query_id=call.id, text=languages[user.language].get('max_track'))
        return
    playlists[playlist].append(track_id)
    user.playlists = json.dumps(playlists)
    session.commit()
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=user.message_id,
                          text=languages[user.language].get('suc_add', TE), reply_markup=markup)
    if user.playlist == playlist:
        try:
            mk, caption = generate_player(user)
            bot.edit_message_caption(caption=caption, message_id=user.player_id, chat_id=user.chat_id, reply_markup=mk)
        except telebot.apihelper.ApiTelegramException:
            pass
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'edit_pl')
def edit_pl_main(call):
    pl_name = json.loads(call.data)['data']
    user, session = sqlast_hope.user(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    rem_b = types.InlineKeyboardButton(languages[user.language].get('rem_pl', TE),
                                       callback_data=json.dumps({"handler": "conf",
                                                                 "data": {"handler": "rem_pl", "data": pl_name}}))
    rename_b = types.InlineKeyboardButton(languages[user.language].get('rename_pl', TE),
                                          callback_data=json.dumps({"handler": "rename_pl", "data": pl_name}))
    markup.row(rem_b, rename_b)
    for track in json.loads(user.playlists)[pl_name]:
        markup.row(types.InlineKeyboardButton(music_api.get_metadata(track) + '   |   ❌',
                                              callback_data=json.dumps({"handler": "rem_track", "playlist": pl_name,
                                                                        'track': track})))
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data=json.dumps({'handler': 'playlist', 'data': pl_name})),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=user.chat_id, message_id=call.message.id,
                          text=languages[user.language].get('pl_edit_text', TE), reply_markup=markup)
    user.script = 'pl_edit'
    session.commit()
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'conf')
def conf_action(call):
    callback = json.loads(call.data)['data']
    user, session = sqlast_hope.user(call.message.chat.id)
    lang = languages[user.language]
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(lang.get('conf_action', TE),
                                          callback_data=json.dumps(callback)))
    markup.row(types.InlineKeyboardButton(lang.get('cancel_action', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(message_id=call.message.id, chat_id=call.message.chat.id, text=lang.get('conf_text', TE),
                          reply_markup=markup)
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'rem_track')
def rem_track_from_pl(call):
    data = json.loads(call.data)
    pl, track = data['playlist'], data['track']
    user, session = sqlast_hope.user(call.message.chat.id)
    all_playlists = json.loads(user.playlists)
    old_pl = all_playlists[pl]
    old_mk = call.message.reply_markup
    del old_mk.keyboard[old_pl.index(track) + 1][0]
    bot.edit_message_reply_markup(chat_id=user.chat_id, reply_markup=old_mk, message_id=user.message_id)
    old_pl.remove(track)
    all_playlists[pl] = old_pl
    user.playlists = json.dumps(all_playlists)
    session.commit()
    if user.playlist == pl and user.track_id == track:
        try:
            mk, caption = generate_player(user)
            bot.edit_message_caption(caption=caption, message_id=user.player_id, chat_id=user.chat_id, reply_markup=mk)
        except telebot.apihelper.ApiTelegramException:
            pass
    session.close()


@bot.callback_query_handler(lambda call: json.loads(call.data)['handler'] == 'rem_pl')
def del_playlist(call):
    pl_name = json.loads(call.data)['data']
    user, session = sqlast_hope.user(call.message.chat.id)
    new = json.loads(user.playlists)
    new.pop(pl_name)
    names = json.loads(user.playlist_names)
    names.pop(pl_name)
    user.playlists = json.dumps(new)
    user.playlist_names = json.dumps(names)
    if pl_name == user.playlist:
        try:
            mk, caption = generate_player(user)
            bot.edit_message_caption(caption=caption, message_id=user.player_id, chat_id=user.chat_id, reply_markup=mk)
        except telebot.apihelper.ApiTelegramException:
            pass
    user.playlist = ''
    session.commit()
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data='{"handler": "playlists"}'),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=user.chat_id, message_id=user.message_id,
                          text=languages[user.language].get('suc_rem', TE), reply_markup=markup)
    session.close()


@bot.callback_query_handler(lambda call: json.loads(call.data)['handler'] == 'rename_pl')
def rename_playlist(call):
    user, session = sqlast_hope.user(call.message.chat.id)
    playlist = json.loads(call.data)['data']
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data=json.dumps({"handler": "edit_pl", "data": playlist})),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=user.chat_id, message_id=user.message_id,
                          text=languages[user.language].get('new_pl_name', TE), reply_markup=markup)
    bot.register_next_step_handler(call.message, handle_new_pl_name, playlist)
    session.close()


def handle_new_pl_name(message, playlist):
    bot.delete_message(chat_id=message.chat.id, message_id=message.id)
    user, session = sqlast_hope.user(message.chat.id)
    pl_names = json.loads(user.playlist_names)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(languages[user.language].get('back', TE),
                                          callback_data=json.dumps({"handler": "edit_pl", "data": playlist})),
               types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    name = message.text
    if len(name) > 10 or '--' in name or name in pl_names.values():
        bot.register_next_step_handler(message, pl_name_handler)
        try:
            bot.edit_message_text(chat_id=message.chat.id, message_id=user.message_id, reply_markup=markup,
                                  text=languages[user.language].get('incorr_pl_name', TE))
        except telebot.apihelper.ApiTelegramException:
            pass
        return
    pl_names[playlist] = name
    user.playlist_names = json.dumps(pl_names)
    session.commit()
    bot.edit_message_text(chat_id=message.chat.id, message_id=user.message_id, reply_markup=markup,
                          text=languages[user.language].get('changed_name', TE))
    if user.playlist == playlist:
        if user.track_id not in json.loads(user.playlists)[user.playlist]:
            return
        try:
            mk, caption = generate_player(user)
            bot.edit_message_caption(caption=caption, message_id=user.player_id, chat_id=user.chat_id, reply_markup=mk)
        except telebot.apihelper.ApiTelegramException:
            pass
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'del_ac')
def delete_account(call):
    user, session = sqlast_hope.user(call.message.chat.id)
    try:
        bot.delete_message(chat_id=user.chat_id, message_id=user.player_id)
    except telebot.apihelper.ApiTelegramException:
        pass
    lang = languages[user.language]
    session.close()
    sqlast_hope.delete_user(user.chat_id)
    bot.edit_message_text(text=lang.get('del_suc', TE), chat_id=user.chat_id, message_id=user.message_id)


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'text')
def get_text(call):
    user, session = sqlast_hope.user(call.message.chat.id)
    text = music_api.get_text(user.track_id)
    if not text:
        bot.answer_callback_query(callback_query_id=call.id, text=languages[user.language].get('fail_text', TE))
        return
    bot.answer_callback_query(callback_query_id=call.id, text="")
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=user.chat_id, message_id=user.message_id,
                          text=f'{languages[user.language].get("song_text", TE)}'
                               f' {music_api.get_metadata(user.track_id)}\n{text}', reply_markup=markup)
    user.script = 'track_text'
    session.commit()
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'share')
def share_track(call):
    bot.answer_callback_query(callback_query_id=call.id, text="")
    user, session = sqlast_hope.user(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=user.chat_id, message_id=user.message_id, reply_markup=markup, parse_mode='markdown',
                          text=f'{languages[user.language].get("share_text", TE)}\n`notify.prj/share/{user.track_id}`')
    user.script = 'share_track'
    session.commit()
    session.close()


@bot.callback_query_handler(func=lambda call: json.loads(call.data)['handler'] == 'share_pl')
def share_playlist(call):
    playlist_id = json.loads(call.data)['data']
    bot.answer_callback_query(callback_query_id=call.id, text="")
    user, session = sqlast_hope.user(call.message.chat.id)
    markup = types.InlineKeyboardMarkup()
    markup.row(types.InlineKeyboardButton(languages[user.language].get('home', TE),
                                          callback_data='{"handler": "home"}'))
    bot.edit_message_text(chat_id=user.chat_id, message_id=user.message_id, reply_markup=markup, parse_mode='markdown',
                          text=f'{languages[user.language].get("share_text", TE)}\n`notify.prj/playlist/'
                               f'{user.chat_id}/{playlist_id}`')
    user.script = 'share_track'
    session.commit()
    session.close()


if __name__ == '__main__':
    try:
        bot.remove_webhook()
        print('initialize completed')
        bot.infinity_polling()
    except Exception as e:
        print(f'crushed: {e}')
