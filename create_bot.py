from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
# token=os.getenv('TOKEN')
bot = Bot('5615243714:AAHyfh3rofFb0R1Vom-vgh_MukwFtplcR-s')
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
