import json
from bot.bot import Bot
from bot.handler import MessageHandler, BotButtonCommandHandler


def message_cb(bot, event):
    print(event.text)
    text = "Выбери действие:\n" \
           "1 - Добавить терминалы в доверенные\n" \
           "2 - Удалить терминалы из доверенных\n" \
           "3 - Проверить наличие терминала в доверенных\n" \
           "4 - Получить список доверенных терминалов\n" \
           "5 - Проверить токен Виалона\n" \
           "6 - Обновить токен Виалона\n"
    get_start_buttons(bot, event, text)


# Стартовые кнопки
def get_start_buttons(bot, event, text=''):
    bot.send_text(chat_id=event.from_chat,
                  text=text,
                  inline_keyboard_markup="{}".format(json.dumps([[
                      {"text": "1", "callbackData": "call_back_id_1", "style": "primary"},
                      {"text": "2", "callbackData": "call_back_id_2", "style": "primary"},
                      {"text": "3", "callbackData": "call_back_id_3", "style": "primary"},
                      {"text": "4", "callbackData": "call_back_id_4", "style": "primary"},
                      {"text": "5", "callbackData": "call_back_id_5", "style": "primary"},
                      {"text": "6", "callbackData": "call_back_id_6", "style": "primary"},
                  ]])))


#Действия кнопок
def buttons_answer_cb(bot, event):
    # Добавить терминалы в доверенные - не умеет
    if event.data['callbackData'] == "call_back_id_1":
        bot.send_text(
            chat_id=event.from_chat,
            text='Падажжи'
        )
        get_start_buttons(bot, event)
    # Удалить терминалы из доверенных - не умеет
    elif event.data['callbackData'] == "call_back_id_2":
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="Падажжи",
            show_alert=False
        )
    # Проверить наличие терминала в доверенных - не умеет
    elif event.data['callbackData'] == "call_back_id_3":
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="Падажжи",
            show_alert=False
        )
    # Получить список доверенных терминалов - не умеет
    elif event.data['callbackData'] == "call_back_id_4":
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="Падажжи",
            show_alert=False
        )
    # Проверить токен Виалона - не умеет
    elif event.data['callbackData'] == "call_back_id_5":
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="Падажжи",
            show_alert=False
        )
    # Обновить токен Виалона - не умеет
    elif event.data['callbackData'] == "call_back_id_6":
        bot.answer_callback_query(
            query_id=event.data['queryId'],
            text="Падажжи",
            show_alert=False
        )


def main():
    with open("token bot.json", 'r') as token_bot:
        TOKEN = json.load(token_bot)['TOKEN VKteams']
    bot = Bot(token=TOKEN)
    bot.dispatcher.add_handler(MessageHandler(callback=message_cb))
    bot.dispatcher.add_handler(BotButtonCommandHandler(callback=buttons_answer_cb))
    bot.start_polling()
    bot.idle()


if __name__ == '__main__':
    main()