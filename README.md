# Telegram-версия бота
## Бот будет доступен [здесь](https://t.me/notify_music_bot)
### Разрабатывает [главный питонист, адепт решений в одну строку и истинный ценитель мемов с симплом](https://github.com/GGergy)

## Структура проекта

    ├─ source/                      Исходный код приложения
    │  ├─ telegram_bot/             Исходный код для бота Telegram
    |  |  ├─ assets/                Материалы для бота Telegram
    |  |  |  ├─ languages/          Языковые пакеты для бота
    |  |  |  ├─ secure/             Данные, хранщиеся только на сервере
    |  |  ├─ utils/                 Функции для бота Telegram
    |  |  |  ├─ config.py           Работа с данными из assets/secure/config.json
    |  |  |  ├─ connect_creater.py  Создание соединения с базой данных
    |  |  |  ├─ get_languages.py    Загрузка языковых пакетов из assets/languages
    |  |  |  ├─ hope_dict.py        Кэш для api музыки
    |  |  |  ├─ music_api.py        Работа с api Яндекс.Музыки
    |  |  |  ├─ osu_api.py          Работа с api Osu!
    |  |  |  ├─ sqlast_hope.py      Работа с базой данных
    |  |  |  ├─ user.py             Модель пользователя в бызе данных
    └─ tg.py                        Main файл
