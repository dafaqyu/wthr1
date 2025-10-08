import telebot
import requests
from telebot import types
import os
from dotenv import load_dotenv
load_dotenv()



bot = os.getenv('BOT_TOKEN')
API = os.getenv('API')
bot= telebot.TeleBot(bot)

user_city = {}

city = None

@bot.message_handler(commands=['start'])

def main(message):

    bot.send_message(message.chat.id, "Введите название вашего места жительства транслитом. \n\nНапример: Moscow, Abu dhabi и т.д.")
    
@bot.message_handler(commands=['help'])

def help(message):
    bot.send_message(message.chat.id, '❗Чтобы иметь возможность использовать команды напишите место вашего жительства транслитом. Например: Moscow, Saint petersburg, и т.д.\n\n❗Вы можете в любой момент изменить ваш город, для которого будут производиться команды. Просто повторно отправьте название города, для которого хотите получать данные.\n\n❗Бот использует бесплатную API от OpenWeatherMap.')

@bot.message_handler(commands=['next24'])

def osnova(message):
    user_id = message.from_user.id
    city = user_city.get(user_id)
    if city == None:
        bot.send_message(message.chat.id, 'Ошибка.')
        return



    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1= types.InlineKeyboardButton('Обновить', callback_data=f'update_{user_id}')
    markup.add(btn1)

    weather_text = get_weather_data(city)
    if weather_text:
        bot.send_message(message.chat.id, weather_text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Ошибка.')

def get_weather_data(city):
    try:
        tempspisok = []
        vlazhspisok = []
        windspisok = []
        osadkispisok = []
        oblspisok = []

        response = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API}&units=metric&lang=ru')
        data = response.json()

        for i in range (0,8):
            prognoz = data['list'][i]
            temp = prognoz['main']['temp']
            tempspisok.append(temp)
            vlazh = prognoz['main']['humidity']
            vlazhspisok.append(vlazh)
            wind = prognoz['wind']['speed']
            windspisok.append(wind)
            osadki = prognoz['pop']
            osadkispisok.append(osadki)
            obl = prognoz['clouds']['all']
            oblspisok.append(obl)




        srtemp = sum(tempspisok)/len(tempspisok)
        srvlazh =  sum(vlazhspisok)/len(vlazhspisok)
        srwind = sum(windspisok)/len(windspisok)
        maxosadki = max(osadkispisok) * 100
        srobl = sum(oblspisok)/len(oblspisok)
        if srobl < 20:
            obltrue = 'ясно/малооблачно ☀️'
        elif  20 <= srobl < 60:
            obltrue = 'переменная облачность ⛅'
        elif 60 <= srobl < 90:
            obltrue = 'облачно ☁️'
        elif 90 <= srobl <= 100:
            obltrue ='пасмурно 🌫️'

        return f'Температура🌡️: {srtemp:.1f}°C. \nВлажность💧: {srvlazh:.1f}%. \nСкорость ветра🏍️️: {srwind:.1f} м/c. \nВероятность осадков🌧️: {maxosadki:.1f}%.\nОблачность: {obltrue}\n \n//Взяты средние показатели за 24 часа.\n//Данные предоставлены для:{city}.'
    except:
        None

@bot.callback_query_handler(func=lambda call: call.data.startswith('update_'))

def callback(call):
    if call.data.startswith('update_'):
        user_id = int(call.data.split('_')[1])
        city = user_city.get(user_id)

        if city == None:
            bot.answer_callback_query(call.id,'Ошибка.')
            return

        weather_text = get_weather_data(city)
        if weather_text:
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn1 = types.InlineKeyboardButton('Обновить', callback_data=f'update_{user_id}')
            markup.add(btn1)


            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=weather_text, reply_markup=markup)
                bot.answer_callback_query(call.id, 'Данные обновлены')
            except:
                None
        else:
            None

@bot.message_handler(commands=['whatowear'])

def whattowear(message):
    user_id = message.from_user.id
    city = user_city.get(user_id)
    tempspisok = []
    if city == None:
        bot.send_message(message.chat.id, 'Ошибка.')
    else:
        response = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API}&units=metric&lang=ru')
        data = response.json()
        for i in range (0,4):
            prognoz = data['list'][i]
            temp = prognoz['main']['temp']
            tempspisok.append(temp)
        srtemp = (int(tempspisok[0])+int(tempspisok[1])+int(tempspisok[2])+int(tempspisok[3]))/4
        bot.send_message(message.chat.id, f'Средняя температура в ближайшее время🌡️:{srtemp}°C')
        if srtemp > 20:
            bot.send_message(message.chat.id, '☀️Одежда:Футболка/майка, шорты/юбка/легкие брюки.\nОбувь:Сандалии,кеды.\nДополнительно:Головной убор.')
        elif 20 >= srtemp > 10:
            bot.send_message(message.chat.id,'🌥️Одежда:Легкая куртка/ветровка, джинсы/брюки, лонгслив/кофта. \nОбувь:Кроссовки, кеды.\n')
        elif 10 >= srtemp >= 0:
            bot.send_message(message.chat.id,'☔Одежда:Теплая куртка, джинсы/плотные брюки, свитер/толстовка.\nОбувь:Закрытая обувь на плотной подошве/осенние ботинки.\nАксессуары: Легкая шапка, шарф, перчатки.')
        elif srtemp < 0:
            bot.send_message(message.chat.id,'☃️Одежда:Зимняя куртка, утепленные брюки, свитер, термобелье.\nОбувь:Зимние ботинки/сапоги.\nАксессуары:Теплая шапка, шарф, варежки/перчатки.')

@bot.message_handler(commands=['next5days'])

def neosnova(message):
    user_id = message.from_user.id
    city = user_city.get(user_id)
    if city == None:
        bot.send_message(message.chat.id, 'Ошибка.')
        return



    markup = types.InlineKeyboardMarkup(row_width=1)
    btn1= types.InlineKeyboardButton('Обновить', callback_data=f'update5_{user_id}')
    markup.add(btn1)

    weather_text = next5days(city)
    if weather_text:
        bot.send_message(message.chat.id, weather_text, reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Ошибка.')

def next5days(city):
    try:
        response = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API}&units=metric&lang=ru')
        data = response.json()
        tempspisok = []
        oblspisok = []
        osadkispisok = []
        for i in range (0,40):
            prognoz = data['list'][i]
            temp = prognoz['main']['temp']
            tempspisok.append(temp)
            obl = prognoz['clouds']['all']
            oblspisok.append(obl)
            osadki = prognoz['pop']
            osadkispisok.append(osadki)
        tempspisok1 = tempspisok[:8]
        tempspisok2 = tempspisok[8:17]
        tempspisok3 = tempspisok[17:25]
        tempspisok4 = tempspisok[25:33]
        tempspisok5 = tempspisok[33:]
        oblspisok1 = oblspisok[:8]
        oblspisok2 = oblspisok[8:17]
        oblspisok3 = oblspisok[17:25]
        oblspisok4 = oblspisok[25:33]
        oblspisok5 = oblspisok[33:]
        osadkispisok1 = osadkispisok[:8]
        osadkispisok2 = osadkispisok[8:17]
        osadkispisok3 = osadkispisok[17:25]
        osadkispisok4 = osadkispisok[25:33]
        osadkispisok5 = osadkispisok[33:]
        temp1 = sum(tempspisok1)/len(tempspisok1)
        temp2 = sum(tempspisok2) / len(tempspisok2)
        temp3 = sum(tempspisok3) / len(tempspisok3)
        temp4 = sum(tempspisok4) / len(tempspisok4)
        temp5 = sum(tempspisok5) / len(tempspisok5)
        obl1 = sum(oblspisok1) / len(oblspisok1)
        obl2 = sum(oblspisok2) / len(oblspisok2)
        obl3 = sum(oblspisok3) / len(oblspisok3)
        obl4 = sum(oblspisok4) / len(oblspisok4)
        obl5 = sum(oblspisok5) / len(oblspisok5)
        osadki1 = max(osadkispisok1)*100
        osadki2 = max(osadkispisok2)*100
        osadki3 = max(osadkispisok3)*100
        osadki4 = max(osadkispisok4)*100
        osadki5 = max(osadkispisok5)*100
        def cloudiness(cld):
            if cld < 20:
                return 'ясно/малооблачно ☀️'
            elif 20 <= cld < 60:
                return 'переменная облачность ⛅'
            elif 60 <= cld < 90:
                return 'облачно ☁️'
            elif 90 <= cld <= 100:
                return  'пасмурно 🌫️'

        return f'1 День(сегодня):🌡️{round(temp1,1)}°C. Облачность:{cloudiness(obl1)}. Вероятность осадков:🌧️{osadki1}%.\n\n2 День(завтра):🌡️{round(temp2,1)}°C. Облачность:{cloudiness(obl2)}. Вероятность осадков:🌧️{osadki2}%.\n\n3 День:🌡️{round(temp3,1)}°C. Облачность:{cloudiness(obl3)}. Вероятность осадков:🌧️{osadki3}%.\n\n4 День:🌡️{round(temp4,1)}°C. Облачность:{cloudiness(obl4)}. Вероятность осадков:🌧️{osadki4}%.\n\n5 День:🌡️{round(temp5,1)}°C. Облачность:{cloudiness(obl5)}. Вероятность осадков:🌧️{osadki5}%.\n\n//Данные предоставлены для:{city}.'









    except:
        None

@bot.callback_query_handler(func=lambda call: call.data.startswith('update5_'))

def callback5(call):
    if call.data.startswith('update5_'):
        user_id = int(call.data.split('_')[1])
        city = user_city.get(user_id)

        if city == None:
            bot.answer_callback_query(call.id,'Ошибка.')
            return

        weather_text = next5days(city)
        if weather_text:
            markup = types.InlineKeyboardMarkup(row_width=1)
            btn1 = types.InlineKeyboardButton('Обновить', callback_data=f'update5_{user_id}')
            markup.add(btn1)


            try:
                bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=weather_text, reply_markup=markup)
                bot.answer_callback_query(call.id, 'Данные обновлены')
            except:
                None
        else:
            None

@bot.message_handler(commands=['whatodo'])

def whatodo(message):

    user_id = message.from_user.id
    city = user_city.get(user_id)

    if city == None:
        bot.send_message(message.chat.id, 'Введите название города.')

    else:
        tempspisok = []
        osadkispisok = []

        response = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API}&units=metric&lang=ru')
        data = response.json()
        for i in range(0, 3):
            prognoz = data['list'][i]
            tempspisok.append(prognoz['main']['temp'])
            osadkispisok.append(prognoz['pop'])
        tempp = sum(tempspisok)/len(tempspisok)
        if max(osadkispisok) > 0.65:
            bot.send_message(message.chat.id, f'В ближайшее время скорее всего будут осадки, вероятность:{max(osadkispisok)*100}. Лучше остаться дома☕.')
        else:
            if tempp > 20:
                bot.send_message(message.chat.id, 'Идеальная погода! 🚴‍♀️ Самое время для пикника, велопрогулки и солнечных ванн. Не забудьте солнцезащитный крем! ☀️🧴')
            elif 20 >= tempp > 10:
                bot.send_message(message.chat.id,'Отличная погода для активности! 🏃‍♂️ Берите велосипед или отправляйтесь на пробежку. Идеально и для посиделок в уличном кафе! ☕')
            elif 10 >= tempp > 0:
                bot.send_message(message.chat.id,'Свежо, но комфортно! 🚶‍♀️ Отправляйтесь на прогулку, займитесь скандинавской ходьбой или согрейтесь чаем из термоса в парке. 🧣')
            elif 0 >= tempp > -10:
                bot.send_message(message.chat.id,'Идеальная погода для активного отдыха! ❄️ Самое время кататься на коньках, лепить снеговика и гулять по хрустящему снегу.')
            elif 20 >= tempp > 10:
                bot.send_message(message.chat.id,'Суровый мороз! ⚠️ Будьте осторожны, одевайтесь очень тепло. Прогулки должны быть короткими. Лучший план — уют дома с горячим какао и книгой. 🏠📚')

@bot.message_handler(content_types=['text'])

def get_smth(message):
    user_id = message.from_user.id
    citycheck = message.text.strip().lower()

    response = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?q={citycheck}&appid={API}&units=metric&lang=ru')
    if response.status_code == 200:
        user_city[user_id] = citycheck

        bot.send_message(message.chat.id, 'Город сохранен. Выберите действие из списка команд.')





    else:
        bot.send_message(message.chat.id,'Неверно введено название места жительства.')

bot.polling(none_stop=True)

# wwsemyonmakushin