import typing
import telebot
import json
import time
import postgreSQL
import os
from datetime import datetime
from telebot import types
from users import Users


with open("token bot.json", 'r', encoding='utf-8') as token_bot:
    TOKEN = json.load(token_bot)['TOKEN Telegram']
bot = telebot.TeleBot(TOKEN)
buffer_user_id = ''
buffer_user_name = ''
buttons = {
        '1': 'Назад',
        '2': 'Добавить терминал в доверенные',
        '3': 'Удалить терминал из доверенных',
        '4': 'Проверить наличие терминала в доверенных',
        '5': 'Получить список доверенных терминалов',
        '6': 'Проверить токен Виалона',
        '7': 'Обновить токен Виалона',
        '8': 'Работа с БД',
        '9': 'Работа с токенами',
        '10': 'Работа с пользователями',
        '11': 'Добавить пользователя',
        '12': 'Удалить пользователя',
        '13': 'Получить список пользователей'
    }


@bot.message_handler(content_types=['text'])
def start(message):
    user_id = message.from_user.id
    logger(user_id, message.text)
    users = Users()
    if not users.check_user_in_list(str(user_id)):
        text = "Вы не зарегистрированы. Пожалуйста, обратитесь к администратору."
        bot.send_message(user_id, text=text)
        return None
    text, keyboard = get_keyboard(user_id, 'start')
    bot.send_message(user_id, text=text, reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    user_id = call.from_user.id
    try:
        logger(user_id, buttons[call.json["data"]])
    except KeyError:
        logger(user_id, call.json["data"])
    global buffer_user_id
    global buffer_user_name
    users = Users()
    if not users.check_user_in_list(str(user_id)):
        text = "Вы не зарегистрированы. Пожалуйста, обратитесь к администратору."
        bot.send_message(user_id, text=text)
        return None
    # Кнопка "Назад"
    if call.data == "1":
        bot.clear_step_handler_by_chat_id(user_id)
        text, keyboard = get_keyboard(user_id, 'start')
        bot.send_message(user_id, text=text, reply_markup=keyboard)
    # Кнопка "Добавить терминал в доверенные"
    elif call.data == "2":
        text = "Введите номер терминала для добавления."
        bot.send_message(user_id, text=text)
        bot.register_next_step_handler(call.message, append_terminal)
    # Кнопка "Удалить терминал из доверенных"
    elif call.data == "3":
        text = "Введите номер терминала для удаления."
        bot.send_message(user_id, text=text)
        bot.register_next_step_handler(call.message, delete_terminal)
    # Кнопка "Проверить наличие терминала в доверенных"
    elif call.data == "4":
        text = "Введите номер терминала для проверки."
        bot.send_message(user_id, text=text)
        bot.register_next_step_handler(call.message, check_terminal)
    # Кнопка "Получить список доверенных терминалов"
    elif call.data == "5":
        filename = postgreSQL.get_trusted_terminals()
        with open(filename, 'rb') as file:
            bot.send_document(call.message.chat.id, file)
        os.remove(filename)
    # Кнопка "Проверить токен Виалона"
    elif call.data == "6":
        token, result = postgreSQL.check_token()
        text, keyboard = get_keyboard(user_id, 'end')
        if result:
            text = 'Токен корректен.'
        else:
            text = 'Токен не работает.'
        bot.send_message(user_id, text=text, reply_markup=keyboard)
    # Кнопка "Обновить токен Виалона"
    elif call.data == "7":
        text = "Введите токен."
        bot.send_message(user_id, text=text)
        bot.register_next_step_handler(call.message, update_token)
    # Кнопка "Работа с БД"
    elif call.data == "8":
        text, keyboard = get_keyboard(user_id, 'Работа с БД')
        bot.send_message(user_id, text=text, reply_markup=keyboard)
    # Кнопка "Работа с токенами"
    elif call.data == "9":
        text, keyboard = get_keyboard(user_id, 'Работа с токенами')
        bot.send_message(user_id, text=text, reply_markup=keyboard)
    # Кнопка "Работа с пользователями"
    elif call.data == "10":
        text, keyboard = get_keyboard(user_id, 'Работа с пользователями')
        bot.send_message(user_id, text=text, reply_markup=keyboard)
    # Кнопка "Добавить пользователя"
    elif call.data == "11":
        text = "Введите ID пользователя."
        bot.send_message(user_id, text=text)
        bot.register_next_step_handler(call.message, get_user_id_and_continue)
    # Кнопка "Удалить пользователя"
    elif call.data == "12":
        text = "Введите ID пользователя."
        bot.send_message(user_id, text=text)
        bot.register_next_step_handler(call.message, delete_user)
    # Кнопка "Получить список пользователей"
    elif call.data == "13":
        text = users.get_users_list()
        bot.send_message(user_id, text=text)
        text, keyboard = get_keyboard(user_id, 'start')
        bot.send_message(user_id, text=text, reply_markup=keyboard)
    # Добавить пользователя с ролью
    elif call.data in users.roles:
        result, reason = users.append_user(buffer_user_id, buffer_user_name, call.data)
        buffer_user_id, buffer_user_name = "", ""
        _, keyboard = get_keyboard(user_id, 'end')
        bot.send_message(user_id, text=reason, reply_markup=keyboard)
    else:
        action_not_found = "Действие не реализовано"
        bot.send_message(call.from_user.id, text=action_not_found)
        text, keyboard = get_keyboard(user_id, 'start')
        bot.send_message(user_id, text=text, reply_markup=keyboard)


def logger(user_id, text):
    users = Users()
    users_json = users.get_users()
    user_name = users_json[str(user_id)]["name"]
    user_role = users_json[str(user_id)]["role"]
    current_time = datetime.fromtimestamp(time.time()).strftime('%d.%m.%Y %H:%M:%S')
    with open(f'{user_id} {user_name} {user_role}.txt', 'a') as log:
        log.write(current_time + ' - ' + text + '\n')
    return ""


def get_keyboard(user_id, menu):
    users = Users()
    role = users.get_role(user_id)
    keyboard = types.InlineKeyboardMarkup()
    text = 'Выбери действие'
    if role is None:
        text = "Вы не зарегистрированы. Пожалуйста, обратитесь к администратору."
        return text, keyboard
    buttons = buttons_collection(role, menu)
    for b in buttons:
        button = types.InlineKeyboardButton(text=b['text'], callback_data=b['id'])
        keyboard.add(button)
    return text, keyboard


def buttons_collection(role, menu):
    buttons_list = []
    if role == 'admin':
        if menu == 'start':
            buttons_list = ['8', '9', '10']
        elif menu == 'Работа с БД':
            buttons_list = ['2', '3', '4', '5', '1']
        elif menu == 'Работа с токенами':
            buttons_list = ['6', '7', '1']
        elif menu == 'end':
            buttons_list = ['1']
        elif menu == 'Работа с пользователями':
            buttons_list = ['11', '12', '13', '1']
        elif menu == 'roles':
            users = Users()
            buttons_list = users.roles
            return [{'id': i, 'text': i} for i in buttons_list]
    if role == 'user':
        if menu == 'start':
            buttons_list = ['8', '9']
        elif menu == 'Работа с БД':
            buttons_list = ['2', '3', '4', '5', '1']
        elif menu == 'Работа с токенами':
            buttons_list = ['6', '7', '1']
        elif menu == 'end':
            buttons_list = ['1']
    return [{'id': i, 'text': buttons[i]} for i in buttons if i in buttons_list]


def append_terminal(message):
    user_id = message.from_user.id
    logger(user_id, message.text)
    result = f'Ошбика добавления!'
    try:
        terminal = int(message.text)
        if len(str(terminal)) == 9:
            res, reason = postgreSQL.append_terminal(terminal)
            if res:
                result = reason
            else:
                result += ' ' + reason
        else:
            result += ' Неправильная длина номера.'
    except ValueError:
        result += ' Номер терминала может содержать только цифры.'
    _, keyboard = get_keyboard(user_id, 'end')
    text = f'{result}\n' \
           f'Продолжай вводить номера терминалов или нажми "Назад"'
    bot.send_message(user_id, text=text, reply_markup=keyboard)
    bot.register_next_step_handler(message, append_terminal)


def delete_terminal(message):
    user_id = message.from_user.id
    logger(user_id, message.text)
    result = f'Ошбика добавления!'
    try:
        terminal = int(message.text)
        if len(str(terminal)) == 9:
            res, reason = postgreSQL.delete_terminal(terminal)
            if res:
                result = reason
            else:
                result += ' ' + reason
        else:
            result += ' Неправильная длина номера.'
    except ValueError:
        result += ' Номер терминала может содержать только цифры.'
    _, keyboard = get_keyboard(user_id, 'end')
    text = f'{result}\n' \
           f'Продолжай вводить номера терминалов или нажми "Назад"'
    bot.send_message(user_id, text=text, reply_markup=keyboard)
    bot.register_next_step_handler(message, append_terminal)


def check_terminal(message):
    user_id = message.from_user.id
    logger(user_id, message.text)
    result = f'Ошбика проверки!'
    try:
        terminal = int(message.text)
        if len(str(terminal)) == 9:
            if not postgreSQL.check_terminal(terminal):
                result = f'{terminal} - нет в БД.'
            else:
                result = f'{terminal} - есть в БД.'
        else:
            result += ' Неправильная длина номера.'
    except ValueError:
        result += ' Номер терминала может содержать только цифры.'
    _, keyboard = get_keyboard(user_id, 'end')
    text = f'{result}\n' \
           f'Продолжай вводить номера терминалов или нажми "Назад"'
    bot.send_message(user_id, text=text, reply_markup=keyboard)
    bot.register_next_step_handler(message, check_terminal)


def delete_user(message):
    users = Users()
    user_id = message.from_user.id
    logger(user_id, message.text)
    result = f'Ошбика!'
    try:
        id_ = int(message.text)
        if not users.check_user_in_list(id_):
            result += f' ID {id_} не был зарегистрирован ранее.'
            _, keyboard = get_keyboard(user_id, 'end')
            text = f'{result}\n' \
                   f'Попробуй еще или нажми "Назад"'
            bot.send_message(user_id, text=text, reply_markup=keyboard)
            bot.register_next_step_handler(message, delete_user)
        else:
            result, reason = users.delete_user(id_)
            _, keyboard = get_keyboard(user_id, 'end')
            bot.send_message(user_id, text=reason, reply_markup=keyboard)
    except ValueError:
        result += ' ID пользователя может содержать только цифры.'
        _, keyboard = get_keyboard(user_id, 'end')
        text = f'{result}\n' \
               f'Попробуй еще или нажми "Назад"'
        bot.send_message(user_id, text=text, reply_markup=keyboard)
        bot.register_next_step_handler(message, delete_user)


def get_user_id_and_continue(message):
    global buffer_user_id
    users = Users()
    user_id = message.from_user.id
    logger(user_id, message.text)
    result = f'Ошбика!'
    try:
        id_ = int(message.text)
        if users.check_user_in_list(id_):
            result += f' ID {id_} зарегистрирован ранее.'
            _, keyboard = get_keyboard(user_id, 'end')
            text = f'{result}\n' \
                   f'Попробуй еще или нажми "Назад"'
            bot.send_message(user_id, text=text, reply_markup=keyboard)
            bot.register_next_step_handler(message, get_user_id_and_continue)
        else:
            buffer_user_id = id_
            text = "Введите имя пользователя."
            bot.send_message(user_id, text=text)
            bot.register_next_step_handler(message, get_user_name)
    except ValueError:
        result += ' ID пользователя может содержать только цифры.'
        _, keyboard = get_keyboard(user_id, 'end')
        text = f'{result}\n' \
               f'Попробуй еще или нажми "Назад"'
        bot.send_message(user_id, text=text, reply_markup=keyboard)
        bot.register_next_step_handler(message, get_user_id_and_continue)


def get_user_name(message):
    global buffer_user_name
    user_id = message.from_user.id
    logger(user_id, message.text)
    buffer_user_name = message.text
    text = "Выберите роль."
    _, keyboard = get_keyboard(user_id, 'roles')
    bot.send_message(user_id, text=text, reply_markup=keyboard)


def update_token(message):
    user_id = message.from_user.id
    logger(user_id, message.text)
    result = f'Ошбика!'
    res, reason = postgreSQL.update_token(message.text)
    if res:
        result = reason
    else:
        result += reason
    _, keyboard = get_keyboard(user_id, 'end')
    bot.send_message(user_id, text=result, reply_markup=keyboard)


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=0)
    # print(buttons_collection('', ''))
    # print(check_role('123', ''))
    # print(buttons_collection('admin', 'start'))
    # print(buttons_collection('admin', 'Работа с БД'))
    # print(buttons_collection('admin', 'Работа с токенами'))