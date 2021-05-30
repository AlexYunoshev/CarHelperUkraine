import config
import json
import codecs
import schedule
import time
import pause
import telebot
import requests
import logging
from functions import TranslateLetters, GetInfoAboutCar

mydb = config.mydb
mydb.disconnect()

logger = logging.getLogger("updateDB.py")
logger.setLevel(logging.INFO)
fh = logging.FileHandler("logging_data.log", 'a', 'utf-16')
logFormat = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
formatter = logging.Formatter(logFormat)
fh.setFormatter(formatter)
logger.addHandler(fh)
logger.info("updateDB.py started")

def DownloadFile():
  try:
    url = 'https://data.gov.ua/dataset/9b0e87e0-eaa3-4f14-9547-03d61b70abb6/resource/e43a82da-89e1-4bbb-820c-bd04ab7a0c89/download'
    r = requests.get(url, allow_redirects=True)
    open('carswanted.json', 'wb').write(r.content)
    logger.info("File download completed successfully")
  except:
    logger.exception("File download problems")

def UpdateDataDB():
  DownloadFile()
  global mydb
  mydb.connect()
  logger.info("Connect DB")  
  mycursor = mydb.cursor()
  logger.info("Start DB update")
  mycursor.execute("truncate table main_data")
  logger.info("Truncate DB done")
  pause.seconds(1)
  logger.info("Pause 1 sec start")
  logger.info("Pause 1 sec finish")
  with codecs.open('D:\\Desktop\\bot\\carswanted.json', encoding='utf-8-sig') as json_file:
      data = json.load(json_file)
      count = 0
      for p in data:
          vehicleNumber = TranslateLetters(p['vehiclenumber'])
          sql = "insert into main_data(organunit, brandmodel, cartype, color, vehiclenumber, bodynumber, chassisnumber, enginenumber, illegalseizuredate, insertdate) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
          val = (p['organunit'], p['brandmodel'], p['cartype'], p['color'], vehicleNumber, p['bodynumber'], p['chassisnumber'], p['enginenumber'], p['illegalseizuredate'], p['insertdate'])
          mycursor.execute(sql, val) 
          mydb.commit()
          count += mycursor.rowcount
  insertInfo = str(count) + " record inserted"
  logger.info(insertInfo)
  logger.info("Start insert info about update")
  datetime = time.strftime('%Y-%m-%d %H:%M:%S')
  sql = "insert into updates(update_date, records_count) values (%s, %s)"
  val = (datetime, count)
  mycursor.execute(sql, val) 
  mydb.commit()
  logger.info("Finish update DB")
  logger.info("Start checking subscriptions")
  bot = telebot.TeleBot(config.TOKEN)
  query = "SELECT * FROM subscriptions"
  mycursor = mydb.cursor()
  mycursor.execute(query)
  myresult = mycursor.fetchall()
  if myresult:
    for p in myresult:
      if (p[2] == 1):  # держ номер
        query = "SELECT * FROM main_data where vehiclenumber = '" + p[1] + "'"
        strOut = GetInfoAboutCar(query)
        if (strOut != "None"):
          bot.send_message(int(p[3]), "Повідомляємо, що номер ТЗ, на який Ви підписані, з'явився у базі розшуку:")
          bot.send_message(int(p[3]), strOut)
          sql = "delete from subscriptions where number_value = '" + (p[1]) + "' and number_type_id = 1"
          mycursor.execute(sql)
          mydb.commit()
          logInfo = "SQL = " + sql
          logger.info(logInfo)

      elif(p[2] == 2): # номер кузова
        query = "SELECT * FROM main_data where bodynumber = '" + p[1] + "'"
        strOut = GetInfoAboutCar(query)
        if (strOut != "None"):
          bot.send_message(int(p[3]), "Повідомляємо, що номер ТЗ, на який Ви підписані, з'явився у базі розшуку:")
          bot.send_message(int(p[3]), strOut)
          sql = "delete from subscriptions where number_value = '" + (p[1]) + "' and number_type_id = 2"
          mycursor.execute(sql)
          mydb.commit()
          logInfo = "SQL = " + sql
          logger.info(logInfo)

      elif(p[2] == 3): # номер двигуна
        query = "SELECT * FROM main_data where enginenumber = '" + p[1] + "'"
        strOut = GetInfoAboutCar(query)
        if (strOut != "None"):
          bot.send_message(int(p[3]), "Повідомляємо, що номер ТЗ, на який Ви підписані, з'явився у базі розшуку:")
          bot.send_message(int(p[3]), strOut)
          sql = "delete from subscriptions where number_value = '" + (p[1]) + "' and number_type_id = 3"
          mycursor.execute(sql)
          mydb.commit()
          logInfo = "SQL = " + sql
          logger.info(logInfo)

  logger.info("Finish checking subscriptions")                   
  mydb.disconnect()
  logger.info("Disconnect DB")  

#UpdateDataDB()
schedule.every().day.at("02:00:05").do(UpdateDataDB)
while True:
    schedule.run_pending()
    time.sleep(1)