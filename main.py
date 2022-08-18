import os
import logging

from telegram.ext import CommandHandler, MessageHandler, Updater, Filters, ConversationHandler, run_async
from telegram import ReplyKeyboardMarkup, ForceReply, KeyboardButton, Bot
from weather_class import Weather
from dotenv import load_dotenv
from data import db_session
from data.users import User

load_dotenv()


admin = int(os.getenv('ADMIN'))
REQUEST_CITY, NAME_CITY, CHOOSING_MAIN, CHOOSING_WEATHER, CHOOSING_NOTIF, CHOOSING_SETTINGS = 1, 2, 3, 4, 5, 6


def check_users_in_db(id_user):
    global db_session
    db_session.global_init(f'root:{os.getenv("PASSWORD_DATABASE")}@127.0.0.1:3306/weather_bot_db')
    session = db_session.create_session()
    user = session.query(User).filter(User.telegram_id == id_user).first()
    if user:
        session.close()
        return True
    return False


def write_in_db(id_user, city, lon, lat):
    db_session.global_init(f'root:{os.getenv("PASSWORD_DATABASE")}@127.0.0.1:3306/weather_bot_db')
    session = db_session.create_session()
    user = User()
    user.telegram_id = id_user
    user.city = city
    user.lon = lon
    user.lat = lat

    session.add(user)
    session.commit()


def city_name(update, context):
    city = update.message.text
    coord = work_class.check_city(city)
    if not coord:
        update.message.reply_text(text='Ошибка! Такого города нет или он ещё не добавлен! Попробуйте снова!')
    else:
        update.message.reply_text(text='Отлично! Город сохранён, при необходимости его всегда можно поменять '
                                       'в "Настройках" ---> \U00002699')

        write_in_db(update.message.chat.id, city, str(coord["lon"]), str(coord["lat"]))

        keyboard = [['Погода \U000026C5'], ['Уведомления \U0001F514'], ['Настройки \U00002699']]
        markup = ReplyKeyboardMarkup(keyboard)
        update.message.reply_text(text='Что тебя интересует?', reply_markup=markup)
        return CHOOSING_MAIN


def for_get_location_or_city(update, context):
    if update.message.location is None:
        update.message.reply_text(text='Напишите название города:')
        return NAME_CITY
    else:
        print(update.message.location)
        coord = update.message.location
        print(type(coord["longitude"]))
        city = work_class.get_name_city_by_coords(str(coord["longitude"]), str(coord["latitude"]))
        update.message.reply_text(text='Отлично! Координаты сохранены, при необходимости их всегда можно поменять '
                                       'в "Настройках" ---> \U00002699')

        write_in_db(update.message.chat.id, city, str(coord["longitude"]), str(coord["latitude"]))

        keyboard = [['Погода \U000026C5'], ['Уведомления \U0001F514'], ['Настройки \U00002699']]
        markup = ReplyKeyboardMarkup(keyboard)
        update.message.reply_text(text='Что тебя интересует?', reply_markup=markup)
        return CHOOSING_MAIN


def start(update, context):
    global admin
    print(update.message.chat.id)
    if update.message.chat.id == admin:
        if not check_users_in_db(update.message.chat.id):
            keyboard_location = KeyboardButton(text='Отправить местоположение', request_location=True)
            keyboard_ask_city = [[keyboard_location, 'Указать город']]
            markup_ask_city = ReplyKeyboardMarkup(keyboard_ask_city)
            update.message.reply_text(text='Привет! Отправьте своё местоположение или название '
                                           'города, что бы я показывал погоду в правильном месте',
                                      reply_markup=markup_ask_city)
            return REQUEST_CITY
        else:
            keyboard = [['Погода \U000026C5'], ['Уведомления \U0001F514'], ['Настройки \U00002699']]
            markup = ReplyKeyboardMarkup(keyboard)
            update.message.reply_text(text='Что тебя интересует?', reply_markup=markup)
            # update.message.reply_html(text='')
            print(dp.handlers)
            return CHOOSING_MAIN


def weather_func(update, context):
    keyboard_weather_func = [['Погода на сегодня', 'Погода на завтра'], ['Погода на 5 дней'],
                             ['Назад']]
    murkup_weather_func = ReplyKeyboardMarkup(keyboard_weather_func)
    update.message.reply_text(text='Выбери что тебе нужно:', reply_markup=murkup_weather_func)
    return CHOOSING_WEATHER


def notifications_func(update, context):
    keyboard_notif_func = [['Каждый час', 'Каждые 4 часа'], ['Каждые 8 часов', 'Каждые 24 часа'], ['Назад']]
    murkup_notif_func = ReplyKeyboardMarkup(keyboard_notif_func)
    update.message.reply_text(text='Как часто нужно присылать актуальную информацию о погоде?',
                              reply_markup=murkup_notif_func)
    return CHOOSING_NOTIF


def settings_func(update, context):
    keyboard_settings_func = [['Отключить все уведомления', 'Сменить язык'], ['Изменить местоположение',
                                                                              'Сообщить об ошибке'], ['Назад']]
    murkup_sett_func = ReplyKeyboardMarkup(keyboard_settings_func)
    update.message.reply_text(text='Раздел "Настройки":', reply_markup=murkup_sett_func)
    return CHOOSING_SETTINGS


def in_dev(update, context):
    update.message.reply_text(text='Данный раздел пока в разработке.... \U0001F6A7 \U0001F6B7 \U000026A0 \U000026D4')


def stop(update, context):
    update.message.reply_text(text='stop')
    return ConversationHandler.END


if __name__ == '__main__':
    updater = Updater(os.getenv('TOKEN'), use_context=True)
    dp = updater.dispatcher
    work_class = Weather(dp)

    conv_handler_1 = ConversationHandler(entry_points=[MessageHandler(
        Filters.regex('^Погода \U000026C5$') & ~Filters.command, weather_func,
        pass_user_data=True)], states={
        CHOOSING_WEATHER: [MessageHandler(Filters.regex('^Погода на сегодня$') & ~Filters.command,
                                          work_class.weather_today,
                                          pass_user_data=True),
                           MessageHandler(Filters.regex('^Погода на завтра$') & ~Filters.command,
                                          work_class.weather_tomorrow,
                                          pass_user_data=True)
                           ]
    }, fallbacks=[MessageHandler(Filters.regex('^Назад$') & ~Filters.command, start,
                  pass_user_data=True)],
       map_to_parent={
            CHOOSING_MAIN: CHOOSING_MAIN
       })

    conv_handler_2 = ConversationHandler(entry_points=[MessageHandler(
        Filters.regex('^Уведомления \U0001F514$') & ~Filters.command, notifications_func,
        pass_user_data=True)], states={
        CHOOSING_NOTIF: [MessageHandler(Filters.regex('^Каждый час$') & ~Filters.command, in_dev,
                                        pass_user_data=True)]
    }, fallbacks=[MessageHandler(Filters.regex('^Назад$') & ~Filters.command, start,
                                 pass_user_data=True)],
       map_to_parent={
            CHOOSING_MAIN: CHOOSING_MAIN
       })

    conv_handler_3 = ConversationHandler(entry_points=[MessageHandler(
        Filters.regex('^Настройки \U00002699$') & ~Filters.command, settings_func,
        pass_user_data=True)], states={
        CHOOSING_SETTINGS: [MessageHandler(Filters.regex('^Отключить все уведомления$') & ~Filters.command,
                                           in_dev,
                                           pass_user_data=True)]
    }, fallbacks=[MessageHandler(Filters.regex('^Назад$') & ~Filters.command, start,
                                 pass_user_data=True)],
       map_to_parent={
            CHOOSING_MAIN: CHOOSING_MAIN
       })

    conv_handler = ConversationHandler(entry_points=[CommandHandler('start', start)], states={
        REQUEST_CITY: [MessageHandler(Filters.location | Filters.regex('^Указать город$'), for_get_location_or_city)],
        NAME_CITY: [MessageHandler(Filters.text, city_name)],
        CHOOSING_MAIN: [conv_handler_1,
                        conv_handler_2,
                        conv_handler_3
                        ]
    }, fallbacks=[CommandHandler('stop', stop)], allow_reentry=True)

    dp.add_handler(conv_handler)
    updater.start_polling(timeout=600)
    updater.idle()
