from typing import Text
import config
import telebot
import time
import logging
from telebot import types
from functions import TranslateLetters, CheckStateNumberBool, GetInfoAboutUpdates, GetHelpString, GetSubscriptions, GetInfoAboutCar, CheckIsUpdateTime

logger = logging.getLogger("bot.py")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("logging_data.log", 'a', 'utf-16')
logFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(logFormat)
fh.setFormatter(formatter)
logger.addHandler(fh)

unknownVehicleText = '👍🏻На щастя, ТЗ з таким номером не знайдено👍🏻'
bot = telebot.TeleBot(config.TOKEN)
mydb = config.mydb
vehicleNumber = ""
numberType = 1

def YesNoButtons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    item1 = types.KeyboardButton("✅ Так ✅")
    item2 = types.KeyboardButton("❌ Ні ❌")
    markup.add(item1, item2)
    return markup

def MainMenuButtons():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    item1 = types.KeyboardButton("🇺🇦Пошук за державним номером ТЗ🇺🇦")
    item2 = types.KeyboardButton("🚗Пошук за номером кузова ТЗ🚗")
    item3 = types.KeyboardButton("⚙️Пошук за номером двигуна ТЗ⚙️")
    item4 = types.KeyboardButton("📖Підписки📖")
    item5 = types.KeyboardButton("👤Допомога👤")
    markup.add(item1, item2, item3, item4, item5)
    return markup

def MainMenu(message):
    markup = MainMenuButtons()
    bot.send_message(message.chat.id, "Оберіть дію:", reply_markup=markup)
    bot.register_next_step_handler(message, GetMainAnswerFromUser)

def Help(message):
    bot.send_message(message.chat.id, "Вітаю, {0.first_name}!\nЯ - <b>{1.first_name}</b> - бот, що надасть інформацію про транспортні засоби, які перебувають в розшуку"
    .format(message.from_user, bot.get_me()), parse_mode='html')
    helpString = GetHelpString()
    bot.send_message(message.chat.id, helpString, parse_mode='html')
    query = "SELECT * FROM updates ORDER BY id DESC LIMIT 10"
    strOut = GetInfoAboutUpdates(query)
    bot.send_message(message.chat.id, strOut) 
    bot.register_next_step_handler(message, GetMainAnswerFromUser)

@bot.message_handler(commands=['start'])
def StartMenu(message):
    global mydb
    updateState = CheckIsUpdateTime(time.strftime("%H:%M"))
    if(updateState == True):
        logText = "Try to start bot by user = " + str(message.chat.id)
        logger.info(logText)
        bot.send_message(message.chat.id, "Вибачте, наразі інформація в базі даних оновлюється. Будь ласка, повторіть спробу через 5 хвилин.")
        mydb.disconnect()
    else:
        logText = "Bot started by user = " + str(message.chat.id)
        logger.info(logText)
        mydb.connect()
        markup = MainMenuButtons()
        bot.send_message(message.chat.id, "Вітаю, {0.first_name}!\nЯ - <b>{1.first_name}</b> - бот, що надасть інформацію про транспортні засоби, які перебувають в розшуку"
        .format(message.from_user, bot.get_me()), parse_mode='html')
        bot.send_message(message.chat.id, "Для початку роботи оберіть дію:", reply_markup=markup)
        bot.register_next_step_handler(message, GetMainAnswerFromUser)
   
@bot.message_handler(content_types=['text'])
def GetMainAnswerFromUser(message):
    logText = "Get message by user = " + str(message.chat.id) + " Message text: " + str(message.text)
    logger.info(logText)
    global mydb
    updateState = CheckIsUpdateTime(time.strftime("%H:%M"))
    if(updateState == True):
        bot.send_message(message.chat.id, "Вибачте, наразі інформація в базі даних оновлюється. Будь ласка, повторіть спробу через 5 хвилин.")
        mydb.disconnect() 
    else:
        mydb.connect()
        if message.text != '/start':
            if message.text == '🇺🇦Пошук за державним номером ТЗ🇺🇦' :
                bot.send_message(message.chat.id, 'Введіть державний номер ТЗ:', reply_markup=types.ReplyKeyboardRemove())
                bot.register_next_step_handler(message, GetStateNumberFromUser)      
            elif message.text == '🚗Пошук за номером кузова ТЗ🚗' :
                bot.send_message(message.chat.id, 'Введіть номер кузова ТЗ:', reply_markup=types.ReplyKeyboardRemove())  
                bot.register_next_step_handler(message, GetBodyNumberFromUser)
            elif message.text == '⚙️Пошук за номером двигуна ТЗ⚙️' :
                bot.send_message(message.chat.id, 'Введіть номер двигуна ТЗ:', reply_markup=types.ReplyKeyboardRemove()) 
                bot.register_next_step_handler(message, GetEngineNumberFromUser)
            elif message.text == '👤Допомога👤' :
                Help(message)
            elif message.text == '📖Підписки📖' :
                query = "SELECT t.number_type, s.number_value FROM subscriptions s, number_types t where chat_id = '" + str(message.chat.id) + "' and s.number_type_id = t.id"
                strOut = GetSubscriptions(query)
                bot.send_message(message.chat.id, strOut, reply_markup=types.ReplyKeyboardRemove()) 
                MainMenu(message)
            else:
                bot.send_message(message.chat.id, 'Ви обрали неправильний критерій. Повторіть, будь ласка, спробу.')
                bot.register_next_step_handler(message, GetMainAnswerFromUser)
        else:
            StartMenu(message)
    
@bot.message_handler(content_types=['text'])
def GetStateNumberFromUser(message):
    logText = "Get message by user = " + str(message.chat.id) + " Message text: " + str(message.text)
    logger.info(logText)
    global mydb
    updateState = CheckIsUpdateTime(time.strftime("%H:%M"))
    if(updateState == True):
        bot.send_message(message.chat.id, "Вибачте, наразі інформація в базі даних оновлюється. Будь ласка, повторіть спробу через 5 хвилин.")
        mydb.disconnect()
    else:
        mydb.connect()
        if message.text != '/start':
            global vehicleNumber
            vehicleNumber = TranslateLetters(message.text)
            CheckStateNumber(message)
        else:
            StartMenu(message)

def CheckStateNumber(message):
    global vehicleNumber
    validNumber = CheckStateNumberBool(vehicleNumber)
    if (validNumber == True):
        bot.send_message(message.chat.id, 'Шукаємо за номером ' + vehicleNumber + '...')
        query = "SELECT * FROM main_data where vehiclenumber = '" + vehicleNumber + "'"
        strOut = GetInfoAboutCar(query)
        if (strOut == 'None'):
            strOut = unknownVehicleText
            global numberType
            numberType = 1
            bot.send_message(message.chat.id, strOut)
            markup = YesNoButtons()
            bot.send_message(message.chat.id, "Чи хочете Ви підписатись на цей номер?", reply_markup=markup)
            bot.register_next_step_handler(message,  Subscribe)
        else:
            bot.send_message(message.chat.id, strOut)
            MainMenu(message)
    else:
        markup = YesNoButtons()
        bot.send_message(message.chat.id, "Ви ввели незвичайний номер. Чи дійсно ви хочете його перевірити?", reply_markup=markup)
        bot.register_next_step_handler(message,  GetAnswerAboutValidStateNumber)
    
@bot.message_handler(content_types=['text'])
def GetAnswerAboutValidStateNumber(message):
    logText = "Get message by user = " + str(message.chat.id) + " Message text: " + str(message.text)
    logger.info(logText)
    if (message.text == "✅ Так ✅"):
        global vehicleNumber
        bot.send_message(message.chat.id, 'Шукаємо за номером ' + vehicleNumber + '...')
        query = "SELECT * FROM main_data where vehiclenumber = '" + vehicleNumber + "'"
        strOut = GetInfoAboutCar(query)
        if (strOut == 'None'):
            strOut = unknownVehicleText
            global numberType
            numberType = 1
            bot.send_message(message.chat.id, strOut)
            markup = YesNoButtons()
            bot.send_message(message.chat.id, "Чи хочете Ви підписатись на цей номер?", reply_markup=markup)
            bot.register_next_step_handler(message,  Subscribe)
        else:
            bot.send_message(message.chat.id, strOut)
            MainMenu(message)
    else:
         MainMenu(message)
    
@bot.message_handler(content_types=['text'])
def GetBodyNumberFromUser(message):
    logText = "Get message by user = " + str(message.chat.id) + " Message text: " + str(message.text)
    logger.info(logText)
    global mydb
    updateState = CheckIsUpdateTime(time.strftime("%H:%M"))
    if(updateState == True):
        bot.send_message(message.chat.id, "Вибачте, наразі інформація в базі даних оновлюється. Будь ласка, повторіть спробу через 5 хвилин.")
        mydb.disconnect()
    else:
        mydb.connect()
        if message.text != '/start':
            bot.send_message(message.chat.id, 'Шукаємо за номером ' + message.text + '...')
            query = "SELECT * FROM main_data where bodynumber = '" + message.text + "'"
            strOut = GetInfoAboutCar(query)
            if (strOut == 'None'):
                strOut = unknownVehicleText
                global vehicleNumber
                global numberType
                vehicleNumber = message.text
                numberType = 2
                bot.send_message(message.chat.id, strOut)
                markup = YesNoButtons()
                bot.send_message(message.chat.id, "Чи хочете Ви підписатись на цей номер?", reply_markup=markup)
                bot.register_next_step_handler(message,  Subscribe)
            else:    
                bot.send_message(message.chat.id, strOut)
                MainMenu(message)
        else:
            StartMenu(message)

@bot.message_handler(content_types=['text'])
def GetEngineNumberFromUser(message):
    logText = "Get message by user = " + str(message.chat.id) + " Message text: " + str(message.text)
    logger.info(logText)
    global mydb
    updateState = CheckIsUpdateTime(time.strftime("%H:%M"))
    if(updateState == True):
        bot.send_message(message.chat.id, "Вибачте, наразі інформація в базі даних оновлюється. Будь ласка, повторіть спробу через 5 хвилин.")
        mydb.disconnect()
    else:
        mydb.connect()
        if message.text != '/start':
            bot.send_message(message.chat.id, 'Шукаємо за номером ' + message.text + '...')
            query = "SELECT * FROM main_data where enginenumber = '" + message.text + "'"
            strOut = GetInfoAboutCar(query)
            if (strOut == 'None'):
                strOut = unknownVehicleText
                global vehicleNumber
                global numberType
                vehicleNumber = message.text
                numberType = 3
                bot.send_message(message.chat.id, strOut)
                markup = YesNoButtons()
                bot.send_message(message.chat.id, "Чи хочете Ви підписатись на цей номер?", reply_markup=markup)
                bot.register_next_step_handler(message,  Subscribe)
            else:
                bot.send_message(message.chat.id, strOut)
                MainMenu(message)
        else:
            StartMenu(message)

@bot.message_handler(content_types=['text'])
def Subscribe(message):
    logText = "Get message by user = " + str(message.chat.id) + " Message text: " + str(message.text)
    logger.info(logText)
    if (message.text == "✅ Так ✅"):
        global vehicleNumber
        global numberType
        global mydb
        mycursor = mydb.cursor()
        bot.send_message(message.chat.id, 'Здійснюємо підписку за номером ' + vehicleNumber + '...')
        sql = "insert into subscriptions(number_value, number_type_id, chat_id) values (%s, %s, %s)"
        val = (vehicleNumber, numberType, message.chat.id)
        mycursor.execute(sql, val) 
        mydb.commit()
        bot.send_message(message.chat.id, 'Підписка здійснена успішно.')
        MainMenu(message)
    else:
        MainMenu(message)

bot.polling(none_stop=True)