
from newsapi import NewsApiClient
from base import *

from telebot import types
from config import keyNews
from config import keyBot
import telebot

bot = telebot.TeleBot(keyBot, parse_mode=None)
newsapi = NewsApiClient(api_key=keyNews)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    userid = [message.chat.id]
    connect = sqlite3.connect('base.db')
    cursor = connect.cursor()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    itemNews = types.KeyboardButton('Новости')
    itemSub = types.KeyboardButton('Подписки')
    itemCate = types.KeyboardButton('Категории')
    markup.add(itemCate, itemNews, itemSub)
    user = cursor.execute('SELECT * FROM users WHERE tg_id = ?;', (userid) ).fetchall()
    if not user:
        cursor.execute('''INSERT INTO users('tg_id') VALUES(?);''', userid)
        connect.commit()
        bot.reply_to(message, "Вы успешно зарегистрированы ", reply_markup=markup)
    else:
        bot.reply_to(message, "Вы уже зарегистрированы", reply_markup=markup)


@bot.message_handler(content_types=['text'])
def bot_message(message):
    print(message.text)
    if message.chat.type == 'private':
        if message.text == 'Категории':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            connect = sqlite3.connect('base.db')
            cursor = connect.cursor()
            categories = cursor.execute('SELECT * FROM categories ;').fetchall()
            i=0
            while i<len(categories):
                name = types.KeyboardButton("подписаться на " + categories[i][1])
                markup.add(name)
                i=i+1
            back = types.KeyboardButton('Вернуться')
            markup.add(back)
            bot.reply_to(message, "Подпишитесь на интересные вам категории:", reply_markup=markup)
    if message.chat.type == 'private':
        subs = "подписаться"
        if message.text.startswith(subs):
            userid = [message.chat.id]
            connect = sqlite3.connect('base.db')
            cursor = connect.cursor()
            id = cursor.execute('SELECT id FROM users WHERE tg_id=?;', (userid)).fetchone()
            id=str(id[0])
            sub = cursor.execute('SELECT * FROM sub INNER JOIN categories ON categories.id = sub.cate_id WHERE user_id = ?;',(id)).fetchall()
            arrSub = []
            i = 0
            while i <len(sub):
                arrSub.append(sub[i][3])
                i=i+1
            i=0
            count=0
            forWhat = message.text[15:]
            while i<len(arrSub):
                if forWhat == arrSub[i]:
                    count=count+1
                i=i+1
            if count ==0:
                cate_id = cursor.execute('SELECT id FROM categories WHERE name=?;', (forWhat,)).fetchall()
                cursor.execute('''INSERT INTO sub('user_id', 'cate_id') VALUES(?,?);''', (id, cate_id[0][0]))
                connect.commit()
                bot.reply_to(message, "Вы успешно подписаны")
            else:
                bot.reply_to(message, "Вы уже подписаны")
    if message.chat.type == 'private':
        if message.text == 'Подписки':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            userid = [message.chat.id]
            connect = sqlite3.connect('base.db')
            cursor = connect.cursor()
            id = cursor.execute('SELECT id FROM users WHERE tg_id=?;', (userid)).fetchone()
            id = str(id[0])
            sub = cursor.execute('SELECT * FROM sub INNER JOIN categories ON categories.id = sub.cate_id WHERE user_id = ?;',(id)).fetchall()
            arrSub = []
            i = 0
            while i < len(sub):
                arrSub.append(sub[i][3])
                i = i + 1
            i = 0
            while i < len(arrSub):
                name = str(arrSub[i])
                name = types.KeyboardButton("отписаться от " + arrSub[i])
                markup.add(name)
                i = i + 1
            back = types.KeyboardButton('Вернуться')
            markup.add(back)
            bot.reply_to(message, "Ваши подписки:", reply_markup=markup)
    if message.chat.type == 'private':
        subs = "отписаться"
        if message.text.startswith(subs):
            userid = [message.chat.id]
            connect = sqlite3.connect('base.db')
            cursor = connect.cursor()
            id = cursor.execute('SELECT id FROM users WHERE tg_id=?;', (userid)).fetchone()
            id=str(id[0])
            forWhat = message.text[14:]
            cate_id = cursor.execute('SELECT id FROM categories WHERE name=?;', (forWhat,)).fetchall()
            cate_id = cate_id[0][0]
            have = cursor.execute('SELECT * FROM sub WHERE user_id = ? and cate_id = ?;',(id, cate_id)).fetchone()
            if not have:
                bot.reply_to(message, "Вы на нее не подписаны")
            else:
                cursor.execute('DELETE FROM sub WHERE user_id = ? and cate_id = ?;',(id, cate_id))
                connect.commit()
                markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
                sub = cursor.execute(
                    'SELECT * FROM sub INNER JOIN categories ON categories.id = sub.cate_id WHERE user_id = ?;',
                    (id)).fetchall()
                arrSub = []
                i = 0
                while i < len(sub):
                    arrSub.append(sub[i][3])
                    i = i + 1
                i = 0
                while i < len(arrSub):
                    name = str(arrSub[i])
                    name = types.KeyboardButton("отписаться от " + arrSub[i])
                    markup.add(name)
                    i = i + 1
                back = types.KeyboardButton('Вернуться')
                markup.add(back)
                bot.reply_to(message, "Вы успешно отписались", reply_markup=markup)
    if message.chat.type == 'private':
        if message.text == 'Новости':
            userid = [message.chat.id]
            connect = sqlite3.connect('base.db')
            cursor = connect.cursor()
            id = cursor.execute('SELECT id FROM users WHERE tg_id=?;', (userid)).fetchone()
            id = str(id[0])
            sub = cursor.execute('SELECT * FROM sub INNER JOIN categories ON categories.id = sub.cate_id WHERE user_id = ?;',(id)).fetchall()
            i=0
            while i < len(sub):
                top_headlines = newsapi.get_top_headlines(category=f'{sub[i][3]}', language='ru', country='ru', page=1,page_size=1)
                bot.send_message(message.chat.id,f'Категория:{sub[i][3]}\nЗаголовок: {top_headlines["articles"][0]["title"]}\n {top_headlines["articles"][0]["url"]}')
                i = i + 1

    if message.chat.type == 'private':
        if message.text == 'Вернуться':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            itemNews = types.KeyboardButton('Новости')
            itemSub = types.KeyboardButton('Подписки')
            itemCate = types.KeyboardButton('Категории')
            markup.add(itemCate, itemNews, itemSub)
            bot.reply_to(message, "ужас", reply_markup=markup)


bot.polling(none_stop=True)
