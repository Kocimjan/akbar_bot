import sqlite3
import time

import telebot
from telebot import types


class database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name, check_same_thread=False)
        self.sql = self.conn.cursor()

    def execute(self, query, *params):
        if params is None:
            self.sql.execute(query)
            data = self.sql.fetchall()
        else:    
            self.sql.execute(query, params)
            data = self.sql.fetchall()
        if data:
            return data[0]

    def conn_close(self):
        self.conn.close()


db = database("diseases_info.db")

TOKEN = "5506364900:AAEFS2ap5AXMz3xCOnzT3jDM0OVTDWmg1pA"
bot = telebot.TeleBot(TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_language_selection(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item_russian = types.KeyboardButton('🇷🇺 Русский')
    item_tajik = types.KeyboardButton('🇹🇯 Тоҷикӣ')
    markup.add(item_russian, item_tajik)
    bot.send_message(message.chat.id, "👋", reply_markup=markup)
    user_name = message.from_user.first_name
    bot.send_message(message.chat.id,
                     f"Ассалому алейкум!!! 👋 {user_name}!!! Ман бот - вориси 👨‍⚕️ табиби бузург "
                     f"Абӯалӣ ибни сино мебошам барои боман сӯҳбат кардан лутфан забонро интихоб "
                     f"кунед..."

                     f"\n\n Ассаляму алейкум!!! 👋 {user_name}!!! Я приемник 👨‍⚕️ великого "
                     f"врача Абу Али ибн Сино, чтобы общаться со мной пожалуйста выберите "
                     f"язык..."

                     f"\n\n👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇👇", reply_markup=markup)


@bot.message_handler(func=lambda message: True)
def handle_language_selection(message):
    if message.text == '🇷🇺 Русский':
        bot.send_message(message.chat.id, "👨‍⚕️")
        user_name = message.from_user.first_name
        language = "ru"
        bot.send_message(message.chat.id, f"👨‍⚕️ {user_name} Чем вы болеете? Напишите имя болезни",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, diagnosis_info, language)
    elif message.text == '🇹🇯 Тоҷикӣ':
        bot.send_message(message.chat.id, "👨‍⚕️")
        user_name = message.from_user.first_name
        language = "tj"
        bot.send_message(message.chat.id,
                         f"👨‍⚕️ {user_name} Шумо аз чӣ азият мекашед?...Номи бемориро нависед",
                         reply_markup=types.ReplyKeyboardRemove())
        bot.register_next_step_handler(message, diagnosis_info, language)
    else:
        bot.send_message(message.chat.id, "Пожалуйста, используйте кнопки для навигации.")


def diagnosis_info(message, language):
    disease = message.text.lower()
    querry = "SELECT description, advice, treatment_course, image_url FROM diseases WHERE disease LIKE ? AND language = ?"
    info = db.execute(querry, '%' + disease + '%', language)
    bot.send_message(message.chat.id, "👨‍⚕️")
    time.sleep(2)  # Имитируем обработку запроса
    if not info:
        if language == 'ru':
            bot.send_message(message.chat.id, 'Информация о такой болезни не найдено в нашей базе.\nПовторите запрос.')
            bot.register_next_step_handler(message, diagnosis_info, language)
        else:
            bot.send_message(message.chat.id, "Маълумот дар бораи ин беморӣ ҳоло вуҷуд надорад. Базаи мо дар мавриди омӯзиш "
                                              "қарор дорад!!!")
    else:
        if language == 'ru':
            msg_text = f"<b>Описание:</b> {info[0]}\n\n<b>Советы:</b> {info[1]}\n\n<b>Курс лечения:</b> {info[2]}"
            image_url = info[3]
            bot.send_photo(message.chat.id, image_url, caption=msg_text, parse_mode='HTML')
        else:
            msg_text = (f"<b>Тавсифи беморӣ:</b> {info[0]}\n\n<b>Маслиҳат:</b> {info[1]}\n\n<b>Роҳҳои "
                        f"табобат:</b> {info[2]}")
            image_url = info[3]
            bot.send_photo(message.chat.id, image_url, caption=msg_text, parse_mode='HTML')

    bot.register_next_step_handler(message, diagnosis_info, language)


bot.polling(none_stop=True)
 # type: ignore
