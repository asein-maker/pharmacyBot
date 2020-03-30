
import sys
import telebot
from telebot import types
import mysql.connector
from mysql.connector import errorcode



bot = telebot.TeleBot('1116987096:AAHXSqubtymMxyyfchZCLMojYAdOc-0Fxes')

try:
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='1',
        port='3306',
        database='test'
    )
except mysql.connector.Error as err:
    if err.errno == errorcode.ER_BAD_DB_ERROR:
        print('DataBase does not exists')
        sys.exit()
    else:
        print(err)
        sys.exit()

# print(db)
cursor = db.cursor()
# cursor.execute('CREATE DATABASE test')
# cursor.execute("CREATE TABLE users (name VARCHAR(255), address VARCHAR(255), masks VARCHAR(255), region VARCHAR(255))")

# cursor.execute("SHOW TABLES")

# for x in cursor:
#   print(x)

# cursor.execute("ALTER TABLE users ADD COLUMN (id INT AUTO_INCREMENT PRIMARY KEY, chat_id INT UNIQUE, address INT UNIQUE)")
#Пример как добавить пользователя

# sql = "INSERT INTO users (name, address, masks, region) VALUES (%s, %s, %s, %s)"
# val = ("Vlad" , "Бишкек", 1, 'Октябрьский')
# cursor.execute(sql, val)
# db.commit()

# sql = "INSERT INTO users (name, address, masks, region) VALUES (%s, %s, %s, %s)"
# val = [
#   ('Peter', 'Lowstreet 4', 2, 'd'),
#   ('Amy', 'Apple st 652', 3, 'sfb'),
#   ('Hannah', 'Mountain 21', 4, 'sfb'),
# ]

# cursor.executemany(sql, val)
# db.commit()

# print(cursor.rowcount, "запись добавлена.")

#                       НАХОДИМ ПО РАЙОНУ
"""cursor.execute("SELECT * FROM users WHERE region = 'Октябрьский' ")
users = cursor.fetchall()
for user in users:
    print(user)"""

#                        Изменить количество масок по адресу
"""cursor.execute("UPDATE users SET masks = '4' WHERE address = 'Apple st 652'")
db.commit()
print('DOne')"""
#                      Изменить количество масок по инпуту
"""sql = ("UPDATE users SET masks = '%s' WHERE address = '%s'")
val = (masks, address)
db.commit()
print('DOne')"""



user_data = {}

class User:
    def __init__(self, region):
        self.name_pharmacy = None
        self.region = region
        self.address = None
        self.masks = None
    

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    msg = bot.send_message(message.chat.id , "Привет, я помогу тебе найти маски!")
    choose_answer = telebot.types.ReplyKeyboardMarkup(True , True)
    item1 = telebot.types.KeyboardButton('Да')
    item2 = telebot.types.KeyboardButton('Нет')
    choose_answer.add(item1 , item2)
    msg2 = bot.send_message(message.chat.id ,f'{message.from_user.first_name}, Хочешь узнать побольше?' , reply_markup=choose_answer)

@bot.message_handler(func=lambda message: True)
def answer_2(message):
    if message.text == "Да":
        choose_answer2 = telebot.types.ReplyKeyboardMarkup(True, True)
        item3 = telebot.types.KeyboardButton("Покупатель")
        item4 = telebot.types.KeyboardButton("Продавец")
        choose_answer2.add(item3 , item4)
        msg3 = bot.send_message(message.chat.id , "Вы Продавец или Покупатель?" , reply_markup=choose_answer2)
        bot.register_next_step_handler(msg3, seller_customer)
    elif message.text == "Нет":
        msg4 = bot.send_message(message.chat.id, "Жаль, надеюсь мы еще увидимся", send_welcome)




def seller_customer(message):
    chat_id = message.chat.id

    markup_inline_regions = telebot.types.ReplyKeyboardMarkup(True, True)
    btn_region1 = telebot.types.KeyboardButton('Октябрьский')
    btn_region2 = telebot.types.KeyboardButton('Свердловский')
    btn_region3 = telebot.types.KeyboardButton('Первомайский')
    btn_region4 = telebot.types.KeyboardButton('Ленинский')
    btn_region5 = telebot.types.KeyboardButton('Назад')
    markup_inline_regions.add(btn_region1,btn_region2, btn_region3, btn_region4, btn_region5)

    markup_inline_choose = telebot.types.ReplyKeyboardMarkup(True, True)
    btn_choose1 = telebot.types.KeyboardButton('Аптеки в районах Бишкека')
    btn_choose2 = telebot.types.KeyboardButton('Поиск масок по адресу')
    btn_choose3 = telebot.types.KeyboardButton('Выйти')
    markup_inline_choose.add(btn_choose1,btn_choose2, btn_choose3)

    if message.text == 'Продавец':
        bot.reply_to(message, 'Выберите район', reply_markup=markup_inline_regions)
        bot.register_next_step_handler(message, process_regions_step)
    elif message.text == 'Покупатель':
        bot.reply_to(message, 'Выберите опцию', reply_markup=markup_inline_choose)
        bot.register_next_step_handler(message, pharmacy_find)


def pharmacy_find(message):
    if message.text == 'Аптеки в районах Бишкека':
        bot.reply_to(message, 'Введите район')
        bot.register_next_step_handler(message, process_find_region)
    elif message.text == 'Поиск масок по адресу':
        bot.reply_to(message, 'Напишите адрес')
        bot.register_next_step_handler(message, process_find_street)


def process_find_region(message):
        region = message.text
        cursor.execute("SELECT * FROM users WHERE region=%s",(region,))
        users = cursor.fetchall()
        for user in users:
            print(user)
        msg = bot.reply_to(message, str(users))


def process_find_street(message):
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        for user in users:
            if user == message.text:
                print(user)
                msg = bot.reply_to(message, 'GOOD')


def process_regions_step(message):
    chat_id = message.chat.id
    region = message.text
    if (region == 'Октябрьский') or (region == 'Свердловский') or (region == 'Первомайский') or (region == 'Ленинский'):
        user_data[chat_id] = User(message.text)
        msg = bot.reply_to(message, 'Введите название вашей аптеки?')
        bot.register_next_step_handler(msg, name_of_pharmacy)
    elif region == 'Назад':
        msg = bot.send_message(message.chat.id, "<--", seller_customer)


def name_of_pharmacy(message):
    chat_id = message.chat.id
    user = user_data[chat_id]
    user.name_pharmacy = message.text
    msg = bot.reply_to(message, 'Введите адрес?')
    bot.register_next_step_handler(msg, process_address_step)


def process_address_step(message):
    chat_id = message.chat.id
    user = user_data[chat_id]
    user.address = message.text
    print(user.address)
    markup = types.ReplyKeyboardMarkup(True, True)
    markup.add('Да', 'Нет')
    msg = bot.reply_to(message, 'Наличие масок?', reply_markup=markup)
    bot.register_next_step_handler(msg, process_mask_step)


def process_mask_step(message):
    chat_id = message.chat.id
    masks = message.text
    if (masks == 'Нет'):
        mask = ''
        user = user_data[chat_id]
        print(mask)
        msg = bot.reply_to(message, 'Сохранить?')
        bot.register_next_step_handler(message, end)

    elif (masks == 'Да'):
        msg = bot.reply_to(message, 'Количество масок:')
        bot.register_next_step_handler(msg, process_masks_step)
    

def process_masks_step(message):
    chat_id = message.chat.id
    user = user_data[chat_id]
    user.masks = message.text
    msg = bot.reply_to(message, 'Сохранить?')    
    bot.register_next_step_handler(message, end)

def end(message):
    try:
        chat_id = message.chat.id
        user = user_data[chat_id]
        
        sql = "INSERT INTO users (name, address, region, masks) VALUES (%s, %s, %s, %s)"
        val = ('Название-'+ user.name_pharmacy , 'Адрес - ' +  user.address, user.region, ' Количество масок - ' + user.masks)
        cursor.execute(sql, val)
        db.commit()
        bot.send_message(chat_id, 'Готово!')
    except Exception as e:
        bot.reply_to(message, 'Ошибка или вы уже внесены в список!')



def process_region_step(message):
    try:
        chat_id = message.chat.id
        region = message.text
        user = user_data[chat_id]
        user.region = message.text
        sql = "INSERT INTO users (name, address, region, masks) VALUES (%s, %s, %s, %s)"
        val = (user.name_pharmacy, user.address, user.region, user.masks)
        cursor.execute(sql, val)
        db.commit()
     
        bot.send_message(chat_id, 'Thats it!')
    except Exception as e:
        bot.reply_to(message, 'An eeror or you are already exist')




# button = types.ReplyKeyboardMarkup()
# button.row('John', 'Raychel')

# @bot.message_handler(content_types=['text'])
# def test_func_2(message):
#     if message.text.isnumeric():
#         bot.send_message(message.chat.id, f'Хэй {message.from_user.username}', reply_markup=button)

# bot.polling()


# Проходим по районам
# cursor.execute('SELECT * FROM users')
# users = cursor.fetchall()
# for user in users:
#     if user == 'Октябрьский':
#         print(user)

bot.enable_save_next_step_handlers(delay=2)

# Load next_step_handlers from save file (default "./.handlers-saves/step.save")
# WARNING It will work only if enable_save_next_step_handlers was called!
bot.load_next_step_handlers()

if __name__ == '__main__':
    bot.polling(none_stop=True)
