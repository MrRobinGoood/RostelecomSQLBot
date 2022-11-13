from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b1 = KeyboardButton('/Сменить_Json_файл')
b2 = KeyboardButton('/Как_создать_Json_файл')
b3 = KeyboardButton('/Как_оформить_запрос')

keyboards_client = ReplyKeyboardMarkup(resize_keyboard=True)

keyboards_client.add(b1).add(b2).add(b3)