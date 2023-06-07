import asyncio
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State
from decouple import config
from keyboards import *
from api_func import *

API_TOKEN = config('API_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class Form(StatesGroup):
    first = State()
    creat_start = State()
    race_confirm = State()
    race_option = State()


# last_choice = [None,None]
interval = ''

@dp.message_handler(commands=['start'], state = '*')
async def send_welcome(message: types.Message, state: FSMContext):
    await state.finish()
    await message.reply("""Welcome to DnD character bot!
Here you can create, save, search for characters for the Dungeons & Dragons 5e tabletop role-playing game by players handbook.
For commands, type /help""", reply_markup=types.ReplyKeyboardRemove())
    
    
@dp.message_handler(commands=['creat'], state = '*')
async def creat_1(message: types.Message, state: FSMContext):
    last_choice = message.answer("Let's get started, do you want to create your own or get a random character?", reply_markup=start_1_k),\
        Form.creat_start.set()
    # async with state.proxy() as data:
    #     data['last_choice'] = last_choice
        
    await last_choice[1]
    await last_choice[0]

@dp.callback_query_handler(state=Form.race_option)
async def create_1_q(query: types.CallbackQuery, state: FSMContext):     
    async with state.proxy() as data:
        race = data['race']
    if query.data == 'Ability_bonuses':
        pass
    elif query.data == 'proficiencies':
        pass
    elif query.data == 'languages':
        pass
    elif query.data == 'subraces':
        pass

@dp.callback_query_handler(state=Form.creat_start)
async def create_1_q(query: types.CallbackQuery, state: FSMContext):    
    if query.data == 'create':
        last_choice = query.message.edit_text("Alright, let's start by choosing a race:", reply_markup=choice_race),\
            Form.race_confirm.set()
    # async with state.proxy() as data:
    #     data['last_choice'] = last_choice
    await last_choice[1]
    await last_choice[0]


@dp.callback_query_handler(lambda callback: callback.data == 'confirm',state=Form.race_confirm, )
async def create_1_q(query: types.CallbackQuery, state: FSMContext):
    global interval
    race = Race(interval)
    async with state.proxy() as data:
        data['race'] = race
    options = race.race_option()
    if options:
        answer = query.message.edit_text("Let's set up some additional features:", reply_markup=options_race(options))
    else:
        answer = query.message.edit_text("Let's choose a class:", reply_markup=types.ReplyKeyboardRemove())
    await Form.race_option.set()
    await answer
        

@dp.callback_query_handler(state=Form.race_confirm)
async def create_1_q(query: types.CallbackQuery, state: FSMContext):
    global interval
    more = False
    if query.data == 'more': 
        more = True
        async with state.proxy() as data:
            interval = data['interval']
    else: 
        interval = query.data
        async with state.proxy() as data:
            data['interval'] = interval
    last_choice = query.message.edit_text(About.race_about(interval, more), reply_markup=confirm_race(more)),\
        Form.race_confirm.set()
    await last_choice[0]
    
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)