import os
import logging
import requests
import json
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters, ConversationHandler, run_async
from telegram import ReplyKeyboardMarkup, ForceReply
from dotenv import load_dotenv

load_dotenv()


def get_usr_coord(user_id: int):
    with open('text_for_tests.txt', 'r', encoding='utf-8') as file:
        users = file.readlines()
        file.close()
    for i in users:
        if str(user_id) in i:
            # name_city = [i.split('----------')[1], i.split('----------')[2]]
            name_city = i.split('----------')[-1]
            print(name_city.rstrip())
            return name_city.rstrip()


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


