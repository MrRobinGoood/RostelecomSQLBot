from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from create_bot import dp, bot
from keyboards import keyboards_client
import json
from handlerts.admin import create_sql_query

global ready_for_simple_query
ready_for_simple_query = False


@dp.message_handler(commands=['start', 'help'])
async def command_start(message: types.Message):
    try:
        await bot.send_message(message.from_user.id,
                               'Привет! Я телеграм бот для обработки данных)\nДля начала работы, прикрепи необходимый Json файл.\nЕсли ты не знаешь как это сделать, посмотри соответствующую подсказку в меню.',
                               reply_markup=keyboards_client)
        await message.delete()
    except:
        await message.reply('Общение с ботом через ЛС, напишите ему); \nt.me/RostelecomSQLBot')


@dp.message_handler(commands=['Как_оформить_запрос'])
async def command_start(message: types.Message):
    await bot.send_message(message.from_user.id, 'Правила оформления запроса:\n1) Не использовать знаки препинания\n'
                                                 '2) Если хотим получить количество строк какого-то столбца то пишем:\n' \
                                                 '\t\t\tСколько (или количество) <имя_столбца>\nПример запроса:\n\t\t\tСколько VehicleBrand со значением Status = Действующее\n' \
                                                 '3) Если хотим получить определённое количество строк то пишем:\n\t\t\tТоп <сколько столбцов взять>\n' \
                                                 'Пример запроса:\n\t\t\tТоп 5 самых популярных VehicleModel\n' \
                                                 '4) Если хотим работать с датой, то после слов (день, месяц, год) ставим имя столбца с датой\n' \
                                                 'Пример запроса:\n\t\t\tСколько LicenseNumber выдавалось в месяц LicenseDate\n' \
                                                 'Это всё, можете приступать к формированию запросов!')


@dp.message_handler(commands=['Сменить_Json_файл'])
async def command_start(message: types.Message):
    global ready_for_simple_query
    ready_for_simple_query = False
    await bot.send_message(message.from_user.id, 'Выполнено! Прикрепите новый Json файл')


@dp.message_handler(commands=['Как_создать_Json_файл'])
async def scan_message(message: types.Message):
    await bot.send_message(message.from_user.id,
                           'Для того чтобы бот мог правильно сформировать SQL запрос, тебе нужно отправить файл в формате Json. В нём по ключу Columns должны содержаться описания столбцов таблицы, в которых по ключу Name должны быть имена столбцов.'
                           '\nПример:\n\t\t\t{"Columns":[{"Name":"UserID"},{"Name":"Date"}]}')


def get_columns(json_file):
    with open(json_file, encoding='utf-8') as f:
        templates = json.load(f)
        columns_names = ['Названия столбцов:']
        for i in templates['Columns']:
            columns_names.append(i['Name'])
    return columns_names


@dp.message_handler(content_types=types.ContentType.DOCUMENT)
async def return_columns(message: types.Message, state: FSMContext):
    file_name = message.document.file_name
    if not (file_name[file_name.find('.')::] == '.json'):
        return await bot.send_message(message.from_user.id, 'Пожалуйста проверьте формат файла')
    global ready_for_simple_query
    ready_for_simple_query = True
    destination = f"D:/Saves/PycharmProjects/telegrambot/{file_name}"
    await message.document.download(destination)
    columns_text = get_columns(file_name)
    async with state.proxy() as data:
        data['file_name'] = file_name
        data['columns_text'] = columns_text
    await message.answer('\n'.join(columns_text))
    await bot.send_message(message.from_user.id, 'Введите строку')

    @dp.message_handler()
    async def get_simple_query(message: types.Message, state: FSMContext):
        global ready_for_simple_query
        if ready_for_simple_query:
            async with state.proxy() as data:
                actual_file_name = data['file_name']
                actual_columns_text2 = data['columns_text']
            user_query = message.text
            sql_question = create_sql_query(user_query, actual_columns_text2,
                                            actual_file_name[:actual_file_name.find('.')])
            await message.answer(sql_question)


def register_handler_client(dp: Dispatcher):
    dp.register_message_handler(command_start, commands=['start', 'help'])
    dp.register_message_handler(command_start, commands=['Сменить_Json_файл'])  # scan_message
    dp.register_message_handler(command_start, commands=['Как_создать_Json_файл'])
    dp.register_message_handler(command_start, commands=['Как_оформить_запрос'])
