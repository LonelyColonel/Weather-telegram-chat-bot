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

    def get_wind_direction(self, degrees):
        if 0 <= degrees <= 25 or 345 <= degrees <= 360:
            return 'Север'
        elif 25 < degrees <= 70:
            return 'Северо-Восток'
        elif 70 < degrees <= 110:
            return 'Восток'
        elif 110 < degrees <= 165:
            return 'Юго-Восток'
        elif 165 < degrees <= 195:
            return 'Юг'
        elif 195 < degrees <= 255:
            return 'Юго-Запад'
        elif 255 < degrees <= 285:
            return 'Запад'
        else:
            return 'Северо-Запад'

    def weather_today(self, update, context):
        user = update.message.chat.id
        name_city = get_usr_coord(user)
        print('-----------')
        print(name_city)
        what_weather = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lang=ru&units=metric&q={name_city}&'
                                    f'appid={os.getenv("API_KEY")}').json()
        print(what_weather)
        sky = what_weather["weather"][0]["description"]
        temp = what_weather["main"]["temp"]
        feels_like = what_weather["main"]["feels_like"]
        visibility = what_weather["visibility"]
        hamidity = what_weather["main"]["humidity"]
        # через API атмосферное давление приходит в гектопаскалях. 1 гектопаскаль = 0.75 мм. рт. столба
        atmosphere = float(what_weather["main"]["pressure"]) * 0.75
        wind_speed = what_weather["wind"]["speed"]
        wind_direction = self.get_wind_direction(what_weather["wind"]["deg"])
        clouds = what_weather["clouds"]["all"]
        date = what_weather["dt"]
        country = what_weather["sys"]["country"]
        text = f'{name_city} {country}\n-------------\nНа улице: {sky}\nТемпература: {temp} \U000000B0C\n' \
               f'Ощущается как: {feels_like}\nВлажность: {hamidity}\nАтмосферное давление: {atmosphere}\n мм.рт.ст.' \
               f'Видимость: {visibility} метров\nСкорость ветра: {wind_speed} м/с\n' \
               f'Направление ветра: {wind_direction}\nОблачность: {clouds} %'

        update.message.reply_text(text=text)

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


