import os
import logging
import requests
import json
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters, ConversationHandler, run_async
from telegram import ReplyKeyboardMarkup, ForceReply
from data import db_session
from data.users import User
from dotenv import load_dotenv

load_dotenv()


def get_usr_coord(user_id: int):
    db_session.global_init(f'root:{os.getenv("PASSWORD_DATABASE")}@127.0.0.1:3306/weather_bot_db')
    session = db_session.create_session()
    spisok = []
    for user in session.query(User).filter(User.telegram_id == user_id):
        spisok.append(str(user))
    print(spisok)
    return ''.join(spisok).split('=')[2]


class Weather:
    def __init__(self, dp):
        self.dp = dp

    def weather_today(self, update, context):
        user = update.message.chat.id
        name_city = get_usr_coord(user)
        print('-----------')
        print(name_city)
        what_weather = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={name_city}&'
                                    f'appid={os.getenv("API_KEY")}').text

        update.message.reply_text(text=what_weather)

    def weather_tomorrow(self, update, context):
        user = update.message.chat.id
        name_city = get_usr_coord(user)
        weather = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={name_city}&'
                               f'cnt=3&appid={os.getenv("API_KEY")}').json()
        with open('test_json.json', 'a', encoding='utf-8') as file:
            json.dump(weather, file)
        # print(weather)
        update.message.reply_text(text='ok')

    def check_city(self, name_city: str):
        checking = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={name_city}&'
                                f'limit=1&appid={os.getenv("API_KEY")}').json()
        coords = {}
        if checking:
            coords['lon'] = checking[0]['lon']
            coords['lat'] = checking[0]['lat']
            return coords
        else:
            return False

    def get_name_city_by_coords(self, lon, lat):
        print(str(lat))
        print(str(lon))
        request = requests.get(f'http://api.openweathermap.org/geo/1.0/reverse?lat={str(lat)}&lon={str(lon)}&'
                               f'limit=1&appid={os.getenv("API_KEY")}')
        return request.json()[0]['name']


