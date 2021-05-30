import re
import config

mydb = config.mydb
updateTimeStart = "02:00"
updateTimeFinish = "02:05"

def CheckIsUpdateTime(time):
    if (time >= updateTimeStart and time <= updateTimeFinish):
        return True 
    else:
        return False
        
def TranslateLetters(text):
    lettersDictionary = {
            'Е' : 'E',
            'І' : 'I',
            'О' : 'O',
            'Р' : 'P',
            'А' : 'A',
            'Н' : 'H',
            'К' : 'K',
            'Х' : 'X',
            'С' : 'C',
            'В' : 'B',
            'М' : 'M',
            'Т' : 'T'
    }
    result = ""
    text = text.upper()
    for i in text:
        if i in lettersDictionary:
            result += lettersDictionary[i]
        else:
            result += i
    return result

def CheckStateNumberBool(number):
    a = re.findall("^[ABCKHI][ABCEHIKMOPTXZY][0-9]{4}[ABCEHIKMOPTXFZY][A-PR-Z]$", number)
    b = re.findall("^[ABCKHI][ABCEHIKMOPTXZY][ABCEHIKMOPTXFZY][A-PR-Z][0-9]{4}$", number) 
    c = re.findall("^[0-2][1-9][ABCEHIKMOPTXFZY][A-PR-Z][0-9]{4}$", number) 
    d = re.findall("^T1[ABCEHIKMOPTXFZY][A-PR-Z][0-9]{4}$", number) 
    e = re.findall("^CDP(([1-4][0-9][0-9])|(0[1-9][0-9])|(00[1-9]))$", number) 
    f = re.findall("^DP(([1-4][0-9][0-9])|(0[1-9][0-9])|(00[1-9]))(([1-9][0-9][0-9])|(0[1-9][0-9])|(00[1-9]))$", number) 
    g = re.findall("^S(([1-4][0-9][0-9])|(0[1-9][0-9])|(00[1-9]))(([1-9][0-9][0-9])|(0[1-9][0-9])|(00[1-9]))$", number) 
    h = re.findall("^[0-9]{5}[ABCEHIKMOPTXFZY][A-PR-Z]$", number) 
    i = re.findall("^Т[ABCKHI][ABCEHIKMOPTXZY][0-9]{5}$", number)
    j = re.findall("^[0-9]{4}[A-PR-Z][0-9]$", number) 
    k = re.findall("[0-9]{4}", number)
    l = re.findall("^ТP[ABCKHI][ABCEHIKMOPTXZY][0-9]{4}$", number) 
    m = re.findall("^[ABCKHI][ABCEHIKMOPTXZY](([1-9][0-9][0-9])|(0[1-9][0-9])|(00[1-9]))E$", number)
    n = re.findall("^[ABCKHI][ABCEHIKMOPTXZY](([1-9][0-9][0-9])|(0[1-9][0-9])|(00[1-9]))B$", number)
    o = re.findall("^[ABCKHI][ABCEHIKMOPTXZY](([1-9][0-9][0-9])|(0[1-9][0-9])|(00[1-9]))G$", number)
    if (a or b or c or d or e or f or g or h or i or j or k or l or m or n or o):
        return True
    else:
        return False

def GetInfoAboutUpdates(query):
    global mydb
    mycursor = mydb.cursor()
    mycursor.execute(query)
    myresult = mycursor.fetchall()
    strOut = "Інформація про оновлення:"
    count = 1
    if myresult:
        for p in myresult:
            strOut += '\n№ ' + str(count)
            strOut += '\nДата оновлення: ' + str(p[1]) + '\n'
            strOut += 'Кількість записів: ' + str(p[2]) + '\n'
            count += 1
    else:
        strOut = 'Інформації про оновлення немає'
    return strOut

def GetSubscriptions(query):
    global mydb
    mycursor = mydb.cursor()
    mycursor.execute(query)
    myresult = mycursor.fetchall()
    strOut = "Ваші підписки:"
    if myresult:
        for p in myresult:
            strOut += '\nТип номера: ' + str(p[0]) + '\n'
            strOut += 'Номер: ' + p[1] + '\n'
    else:
        strOut = 'Ви не підписані на жодний номер.'
    return strOut

def GetHelpString():
    helpString = "Для початку роботи з ботом оберіть дію.\
    \n\
    \n1 - Пошук за <b>державним номером ТЗ</b>.\
    \nВведіть державний номер транспортного засобу та натисніть кнопку <i>надіслати</i>.\
    \nВи можете ввести номер будь-якою комбінацією символів як за регістром (верхній, нижній та змішаний), так і за мовою (англійські символи або українські).\
    \n\
    \n2 - Пошук за <b>номером кузова (VIN) ТЗ</b>.\
    \nВведіть номер кузова транспортного засобу та натисніть кнопку <i>надіслати</i>.\
    \nВи можете ввести номер будь-якою комбінацією символів за регістром (верхній, нижній та змішаний) <b>лише англійською мовою</b>.\
    \n\
    \n3 - Пошук за <b>номером двигуна ТЗ</b>.\
    \nВведіть номер двигуна транспортного засобу та натисніть кнопку <i>надіслати</i>.\
    \nВи можете ввести номер будь-якою комбінацією символів за регістром (верхній, нижній та змішаний) <b>лише англійською мовою</b>.\
    \n\
    \n4 - Підписки.\
    \nВ даному розділі Ви можете переглянути список номерів, на які Ви підписані.\
    \n\
    \nПосилання на всю базу даних:\
    \nhttps://data.gov.ua/dataset/2a746426-b289-4eb2-be8f-aac03e68948c"
    return helpString

def GetInfoAboutCar(query):
    global mydb
    mycursor = mydb.cursor()
    mycursor.execute(query)
    myresult = mycursor.fetchall()
    if myresult:
        for p in myresult:
            strOut = 'Підрозділ, що здійснює розшук: ' + p[1] + '\n'
            strOut += 'Марка, модель: ' + p[2] + '\n'
            strOut += 'Тип ТЗ: ' + p[3] + '\n'
            strOut += 'Колір: ' + p[4] + '\n'
            strOut += 'Державний номерний знак: ' + p[5] + '\n'
            strOut += 'Номер кузова (VIN): ' + p[6] + '\n'
            strOut += 'Номер шасі: ' + p[7] + '\n'
            strOut += 'Номер двигуна: ' + p[8] + '\n'
            strOut += 'Дата незаконного заволодіння: ' + str(p[9]) + '\n'
            strOut += 'Дата обліку інформації: ' + str(p[10]) + '\n'
    else:
        strOut = 'None'
    return strOut