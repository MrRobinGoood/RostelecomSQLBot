from aiogram.utils import executor
from create_bot import dp

async def on_startup(_):
    print('Бот вышел в онлайн')
from handlerts import client

client.register_handler_client(dp)
'''**********************************CLIENT SIDE*************************************'''
'''*********************************ADMIN PART***************************************'''
executor.start_polling(dp, skip_updates=True, on_startup=on_startup)