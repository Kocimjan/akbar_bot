import sqlite3
import time
import threading
import schedule
import telebot
from telebot import types

TOKEN = ""
bot = telebot.TeleBot(TOKEN)

users_languages = {}
user_answers = {}
users_info = {}
user_current_question = {}
doctor_id = '6221642254'


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

    def close(self):
        self.conn.close()


db = database("diseases_info.db")



@bot.message_handler(commands=['start', 'help'])
def send_language_selection(message):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True, one_time_keyboard=True)
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

@bot.message_handler(commands=['opros'])
def send(message):
    for chat_id in users_languages:
            if users_languages[chat_id] == 'tj':
                tajik_survey(chat_id)
            elif users_languages[chat_id] == 'ru':
                russian_survey(chat_id)


@bot.message_handler(func=lambda message: message.text == "🇷🇺 Русский" or message.text == "🇹🇯 Тоҷикӣ")
def handle_language_selection(message):
    chat_id = message.chat.id
    users_languages[chat_id] = None
    users_info[chat_id] = {}
    users_info[chat_id]["username"] = message.from_user.username
    if message.text == '🇷🇺 Русский':
        bot.send_message(message.chat.id, "👨‍⚕️")
        users_languages[chat_id] = "ru"

    else:
        bot.send_message(message.chat.id, "👨‍⚕️")
        users_languages[chat_id] = "tj"

    main_menu(message, users_languages[chat_id])


@bot.message_handler(func=lambda message: True)
def btn_handler(message):
    chat_id = message.chat.id
    if message.text == 'Найти Болезнь':
        bot.send_message(chat_id, "Напишите название болезни для получения справочной информации")
        bot.register_next_step_handler(message, diagnosis_info, users_languages[chat_id])
    else:
        if users_languages[chat_id] == "ru":
            bot.send_message(message.chat.id, "Пожалуйста, используйте кнопки для навигации.")
        else:
            bot.send_message(message.chat.id, "Лутфан, барои паймоиш тугмаҳоро истифода баред.")


def main_menu(message, language):
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    if language == "ru":
        markup.row("Найти Болезнь", "Уведомления")
        bot.send_message(message.chat.id, "Меню открыто", reply_markup=markup)
    else:
        markup.row("Точикиша хдат пур кун/ :D/ ):)):)")
        bot.send_message(message.chat.id, "Меню кушодааст", reply_markup=markup)
    

def diagnosis_info(message, language):
    disease = message.text.lower()
    querry = "SELECT description, advice, treatment_course, image_url FROM diseases WHERE disease LIKE ? AND language = ?"
    info = db.execute(querry, '%' + disease + '%', language)
    bot.send_message(message.chat.id, "👨‍⚕️")
    time.sleep(2)  
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




def schedule_survey():
    schedule.every().day.at("10:29").do(send_survey)
    schedule.every().day.at("10:32").do(send_survey)
    schedule.every().day.at("10:35").do(send_survey)

    while True:
        schedule.run_pending()
        time.sleep(1)

def send_survey():
    for chat_id in users_languages:
        if users_languages[chat_id] == 'tj':
            tajik_survey(chat_id)
        elif users_languages[chat_id] == 'ru':
            russian_survey(chat_id)



def russian_survey(chat_id):
    questions = ["Как вас зовут?", "Чем болеете?", "Ваш возраст?", "Как ваше самочувствие?"]
    user_current_question[chat_id] = 0
    if chat_id in user_answers:
        user_current_question[chat_id] = 1
    
    ask_question(chat_id, questions, user_current_question)


def tajik_survey(chat_id):
    questions = ["Номи шумо чист?", "Беморӣ кардаанд?", "Соли шумо чанд буд?", "Ахволи шумо чи хел аст?"]
    user_current_question[chat_id] = 0
    if chat_id in user_answers:
        user_current_question[chat_id] = 1
    
    ask_question(chat_id, questions, user_current_question)


def ask_question(chat_id, questions, user_current_question):
    if user_current_question[chat_id] < len(questions):
        msg = bot.send_message(chat_id, questions[user_current_question[chat_id]])
        bot.register_next_step_handler(msg, lambda m: process_answer(chat_id, questions, m.text, user_current_question))
    else:
        save_report(chat_id, users_languages[chat_id], questions, user_answers[chat_id])
        user_answers[chat_id] = user_answers[chat_id][:1]


def process_answer(chat_id, questions, answer, user_current_question):
    if chat_id not in user_answers:
        user_answers[chat_id] = []
    user_answers[chat_id].append(answer)
    user_current_question[chat_id] += 1
    ask_question(chat_id, questions, user_current_question)


def save_report(chat_id, language, questions, answers):
    conn = sqlite3.connect('diseases_info.db')
    sql = conn.cursor()

    sql.execute('''CREATE TABLE IF NOT EXISTS reports
                 (chat_id TEXT, language TEXT, question1 TEXT, question2 TEXT, question3 TEXT, question4 TEXT)''')

    sql.execute("INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?)", (str(chat_id), language, answers[0], answers[1], answers[2], answers[3]))

    conn.commit()
    conn.close()
    msg_text = f"Опрос от @{users_info[chat_id]['username']} \nВопрос: {questions[0]} Ответ: {answers[0]} \nВопрос: {questions[1]} Ответ: {answers[1]} \nВопрос:{questions[2]} Ответ: {answers[2]} \nВопрос:{questions[3]} Ответ: {answers[3]}"
    bot.send_message(chat_id=doctor_id, text=msg_text)
    bot.send_message(chat_id, "Спасибо За Участие в опросе!")
    

notification_thread = threading.Thread(target=schedule_survey)
notification_thread.start()


if __name__ == "__main__":
    print("bot started")
    bot.polling(none_stop=True)



    # type: ignore
