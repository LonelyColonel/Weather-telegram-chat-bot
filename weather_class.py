import os
import logging
import requests
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters, ConversationHandler, run_async
from telegram import ReplyKeyboardMarkup, ForceReply
from dotenv import load_dotenv


load_dotenv()


class Weather:
    def __init__(self, dp):
        self.dp = dp

    def weather_today(self, update, context):
        update.message.reply_text(text='weather_class')

    def check_city(self, name_city):
        checking = requests.get(f'https://api.openweathermap.org/data/2.5/weather?q={name_city}&'
                                f'lang=ru&appid={os.getenv("API_KEY")}').json()
        try:
            coord = checking['coord']
            return coord
        except KeyError:
            return False

