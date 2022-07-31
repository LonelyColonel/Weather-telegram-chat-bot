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
            user_coords = [i.split('----------')[1], i.split('----------')[2]]
            print(user_coords)
            return user_coords


class Weather:
    def __init__(self, dp):
        self.dp = dp

    def weather_today(self, update, context):
        user = update.message.chat.id
        user_coords = get_usr_coord(user)
        update.message.reply_text(text=self.get_today_weather(user_coords[0], user_coords[1]))

    def weather_tomorrow(self, update, context):
        user = update.message.chat.id
        user_coords = get_usr_coord(user)
        weather = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?'
                               f'lat={user_coords[0]}&lon={user_coords[1]}&appid={os.getenv("API_KEY")}').json()
        with open('test_json.json', 'a', encoding='utf-8') as file:
            json.dump(weather, file)
        print(weather)
        update.message.reply_text(text='ok')

    def check_city(self, name_city):
        checking = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={name_city}&'
                                f'lang=ru&appid={os.getenv("API_KEY")}').json()
        try:
            coord = checking['coord']
            return coord
        except KeyError:
            return False

    def get_today_weather(self, lon, lat):
        what_weather = requests.get(f'https://api.openweathermap.org/data/2.5/weather?lon={lon}&lat={lat}&'
                                    f'lang=ru&appid={os.getenv("API_KEY")}').text
        return what_weather
