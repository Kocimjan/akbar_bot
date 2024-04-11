import telebot
import schedule
import time
import sqlite3
import threading

from telebot import types


TOKEN = "5506364900:AAEFS2ap5AXMz3xCOnzT3jDM0OVTDWmg1pA"
bot = telebot.TeleBot(TOKEN)

doctor_username = '@akbarjon0401'

users_languages = {}

user_answers = {}

user_current_question = {}


def send_survey():
    # Отправка опроса всем пользователям
    for chat_id in users_languages:
        if users_languages[chat_id] == 'Тоҷикӣ':
            tajik_survey(chat_id)
        elif users_languages[chat_id] == 'Русский':
            russian_survey(chat_id)

def schedule_survey():
    # Запланировать отправку опроса в определенное время
    schedule.every().day.at("07:39").do(send_survey)
    schedule.every().day.at("12:00").do(send_survey)
    schedule.every().day.at("20:00").do(send_survey)

    while True:
        schedule.run_pending()
        time.sleep(1)

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    item_tj = types.KeyboardButton("Тоҷикӣ")
    item_ru = types.KeyboardButton("Русский")
    markup.add(item_tj, item_ru)
    
    msg = bot.send_message(message.chat.id, "Выберите язык / Забонро интихоб кунед:", reply_markup=markup)
    bot.register_next_step_handler(msg, language_selection)


def language_selection(message):
    if message.text == "Тоҷикӣ":
        users_languages[message.chat.id] = 'Тоҷикӣ'
        tajik_survey(message.chat.id)
    elif message.text == "Русский":
        users_languages[message.chat.id] = 'Русский'
        russian_survey(message.chat.id)
    else:
        msg = bot.send_message(message.chat.id, "Выберите язык / Забонро интихоб кунед:")
        bot.register_next_step_handler(msg, language_selection)

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
    conn = sqlite3.connect('reports.db')
    sql = conn.cursor()

    sql.execute('''CREATE TABLE IF NOT EXISTS reports
                 (chat_id TEXT, language TEXT, question1 TEXT, question2 TEXT, question3 TEXT, question4 TEXT)''')

    sql.execute("INSERT INTO reports VALUES (?, ?, ?, ?, ?, ?)", (str(chat_id), language, answers[0], answers[1], answers[2], answers[3]))

    conn.commit()
    conn.close()
    
    
def get_doctor_chat_id(username):
    doctor = bot.get_chat(username)
    return doctor.id

notification_thread = threading.Thread(target=schedule_survey)
notification_thread.start()


if __name__ == "__main__":
    # schedule_survey()
    print("bot started")
    bot.polling()

