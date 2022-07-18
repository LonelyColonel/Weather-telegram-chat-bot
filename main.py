import os
import logging
import requests
from telegram.ext import CommandHandler, MessageHandler, Updater, Filters, ConversationHandler, run_async
from telegram import ReplyKeyboardMarkup, ForceReply
from dotenv import load_dotenv

load_dotenv()


def start(update, context):
    keyboard = [['Погода \U000026C5'], ['Уведомления \U0001F514'], ['Настройки \U00002699']]
    markup = ReplyKeyboardMarkup(keyboard)
    update.message.reply_text(text='Привет! Что тебя интересует?', reply_markup=markup)


def weather_func(update, context):
    keyboard_weather_func = [['Погода на сегодня', 'Погода на завтра'], ['Погода на 5 дней', 'Погода на 10 дней'],
                             ['Назад']]
    murkup_weather_func = ReplyKeyboardMarkup(keyboard_weather_func)
    update.message.reply_text(text='Выбери что тебе нужно:', reply_markup=murkup_weather_func)


def notifications_func(update, context):
    keyboard_notif_func = [['Каждый час'], ['Каждые 4 часа'], ['Каждые 8 часов'], ['Каждые 24 часа'], ['Назад']]
    murkup_notif_func = ReplyKeyboardMarkup(keyboard_notif_func)
    update.message.reply_text(text='Как часто нужно присылать актуальную информацию о погоде?',
                              reply_markup=murkup_notif_func)


def settings_func(update, context):
    keyboard_settings_func = [['Отключить все уведомления'], ['Сменить язык'], ['Изменить местоположение'],
                              ['Сообщить об ошибке'], ['Назад']]
    murkup_sett_func = ReplyKeyboardMarkup(keyboard_settings_func)
    update.message.reply_text(text='Раздел "Настройки":', reply_markup=murkup_sett_func)


def stop(update, context):
    update.message.reply_text(text='stop')


if __name__ == '__main__':
    updater = Updater(os.getenv('TOKEN'), use_context=True)
    dp = updater.dispatcher
    # conv_handler = ConversationHandler(entry_points=[CommandHandler('start', start)], states={
    #     1: [MessageHandler(Filters.regex('^Погода$') & ~Filters.command, do, pass_user_data=True)],
    #     2: []
    #
    # }, fallbacks=[CommandHandler('stop', stop)])
    # dp.add_handler(conv_handler)
    # print(dp.handlers)
    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(MessageHandler(Filters.regex('^Погода \U000026C5$'), weather_func))
    dp.add_handler(MessageHandler(Filters.regex('^Назад$'), start))
    dp.add_handler(MessageHandler(Filters.regex('^Уведомления \U0001F514$'), notifications_func))
    dp.add_handler(MessageHandler(Filters.regex('^Настройки \U00002699$'), settings_func))
    updater.start_polling(timeout=600)
    updater.idle()
