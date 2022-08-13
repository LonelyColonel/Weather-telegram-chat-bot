import os
import logging

from telegram.ext import CommandHandler, MessageHandler, Updater, Filters, ConversationHandler, run_async
from telegram import ReplyKeyboardMarkup, ForceReply, KeyboardButton, Bot
from weather_class import Weather
from dotenv import load_dotenv

load_dotenv()


admin = int(os.getenv('ADMIN'))
REQUEST_CITY, TEST1, CHOOSING_MAIN, CHOOSING_WEATHER, CHOOSING_NOTIF, CHOOSING_SETTINGS = 1, 2, 3, 4, 5, 6


def check_users_in_db(id_user):
    with open('text_for_tests.txt', 'r', encoding='utf-8') as file:
        users = file.readlines()
    for user in users:
        if str(id_user) in user:
            return True
    return False


def city_name(update, context):
    # dp.handlers[1].clear()
    city = update.message.text
    coord = work_class.check_city(city)
    if not coord:
        update.message.reply_text(text='Ошибка! Такого города нет или он ещё не добавлен! Попробуйте снова!')
    else:
        update.message.reply_text(text='Отлично! Город сохранён, при необходимости его всегда можно поменять '
                                       'в "Настройках" ---> \U00002699')
        with open('text_for_tests.txt', 'a', encoding='utf-8') as file:
            file.write(f'{update.message.chat.id}----------{coord["lon"]}----------{coord["lat"]}----------{city}\n')
        file.close()
        keyboard = [['Погода \U000026C5'], ['Уведомления \U0001F514'], ['Настройки \U00002699']]
        markup = ReplyKeyboardMarkup(keyboard)
        update.message.reply_text(text='Что тебя интересует?', reply_markup=markup)
        return CHOOSING_MAIN


# TODO: переименовать функцию
def test_2(update, context):
    if update.message.location is None:
        update.message.reply_text(text='Напишите название города:')
        return TEST1
    else:
        print(update.message.location)
        coord = update.message.location
        print(type(coord["longitude"]))
        city = work_class.get_name_city_by_coords(str(coord["longitude"]), str(coord["latitude"]))
        update.message.reply_text(text='Отлично! Координаты сохранены, при необходимости их всегда можно поменять '
                                       'в "Настройках" ---> \U00002699')

        # TODO: вынести это в отдельную функцию
        with open('text_for_tests.txt', 'a', encoding='utf-8') as file:
            file.write(f'{update.message.chat.id}----------{coord["longitude"]}----------{coord["latitude"]}----------{city}\n')
        file.close()
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
            # dp.add_handler(MessageHandler(Filters.location | Filters.regex('^Указать город$'),
            #                               test_2), group=1)
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


def test(update, context):
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
        CHOOSING_NOTIF: [MessageHandler(Filters.regex('^Каждый час$') & ~Filters.command, test,
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
                                           test,
                                           pass_user_data=True)]
    }, fallbacks=[MessageHandler(Filters.regex('^Назад$') & ~Filters.command, start,
                                 pass_user_data=True)],
       map_to_parent={
            CHOOSING_MAIN: CHOOSING_MAIN
       })

    conv_handler = ConversationHandler(entry_points=[CommandHandler('start', start)], states={
        REQUEST_CITY: [MessageHandler(Filters.location | Filters.regex('^Указать город$'), test_2)],
        TEST1: [MessageHandler(Filters.text, city_name)],
        CHOOSING_MAIN: [conv_handler_1,
                        conv_handler_2,
                        conv_handler_3
                        ]
    }, fallbacks=[CommandHandler('stop', stop)], allow_reentry=True)

    dp.add_handler(conv_handler)
    # print(dp.handlers)
    # dp.add_handler(CommandHandler('start', start))
    # dp.add_handler(MessageHandler(Filters.regex('^Погода \U000026C5$'), weather_func))
    # dp.add_handler(MessageHandler(Filters.regex('^Назад$'), start))
    # dp.add_handler(MessageHandler(Filters.regex('^Уведомления \U0001F514$'), notifications_func))
    # dp.add_handler(MessageHandler(Filters.regex('^Настройки \U00002699$'), settings_func))
    updater.start_polling(timeout=600)
    updater.idle()
