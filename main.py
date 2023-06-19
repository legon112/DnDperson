"""Main code of the Bot"""
import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from decouple import config

from api_func import *
from keyboards import *

API_TOKEN = config('API_TOKEN')

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

class Form(StatesGroup):
    """class with states for Bot"""
    first = State()
    race_confirm = State()
    race_option = State()
    class_choice = State()
    points_choice = State()
    save_form = State()
    character_info = State()
    search = State()




@dp.message_handler(commands=['start'], state = '*')
async def send_welcome(message: types.Message, state: FSMContext):
    """Send welcome message"""
    await state.finish()
    await message.reply("""Welcome to DnD character bot!
Here you can create, save, search for characters for the Dungeons & Dragons 5e tabletop role-playing game by players handbook.
For commands, type /help""", reply_markup=types.ReplyKeyboardRemove())
    
    
@dp.message_handler(commands=['help'], state = '*')
async def send_help(message: types.Message):
    """Send list of commands"""
    await message.reply("""/start - exit from all modes
/help - list of commands
/create - character creation
/my_characters - list of your characters
/search - search for a character by ID""")
    


    
"""           !!!!!!CREATING OF CHARACTER!!!!!!            """
@dp.message_handler(commands=['create'], state = '*')
async def create_1_q(message: types.Message):    
    """race selection"""
    text = "Alright, let's start by choosing a race:"
    reply_markup = choice_race
    await Form.race_confirm.set()
    await message.answer(text=text, reply_markup=reply_markup)


@dp.callback_query_handler(lambda callback: callback.data == 'confirm',state=Form.race_confirm, )
async def create_1_qf(query: types.CallbackQuery, state: FSMContext):
    """displaying a list of optional skills"""
    async with state.proxy() as data:
        race = Race(data['interval'])
        data['race'] = race
    options = race.race_option()
    if options:
        answer = query.message.edit_text("Let's set up some additional features:", reply_markup=options_race(options))
        await Form.race_option.set()
    else:
        answer = query.message.edit_text("Let's choose a class:",reply_markup=choice_class)
        await Form.class_choice. set()
    await answer
    

@dp.callback_query_handler(state=Form.race_confirm)
async def create_1_qm(query: types.CallbackQuery, state: FSMContext):
    """output of information about Race"""
    more = False
    if query.data == 'more': 
        more = True
        async with state.proxy() as data:
            interval = data['interval']
    else: 
        interval = query.data
        async with state.proxy() as data:
            data['interval'] = interval
    await query.message.edit_text(About.race_about(interval, more), reply_markup=confirm_race(more))

   
@dp.callback_query_handler(state=Form.race_option)
async def create_1_qp(query: types.CallbackQuery, state: FSMContext):
    """race skill selection"""    
    async with state.proxy() as data:
        race = data['race']
    text = "Let's set up some additional features:"
    reply_markup = None
    if query.data in ('ability_bonuses', 'proficiencies', 'languages'):
        for i in race.race_option():
            if i['type'] == query.data:
                text = f"Choose {i['choose']} {i['type']}:"
                reply_markup = options_choose(i)
    elif query.data in About.all_list('ability-scores'):
        if race.add_data('ability-scores', query.data):
            text = f"Choose {race.bonuse_opt['choose']} ability_bonuses:"
            reply_markup = options_choose(race.race_option(), type='ability_bonuses')
    elif query.data in About.all_list('languages'):
        if race.add_data('languages', query.data):
            text = f"Choose {race.languages_opt['choose']} languages:"
            reply_markup = options_choose(race.race_option(), type='languages')       
    elif query.data in About.all_list('proficiencies'):
        if race.add_data('proficiencies', query.data):
            text = f"Choose {race.proficiencies_opt['choose']} proficiencies:"
            reply_markup = options_choose(race.race_option(), type='proficiencies')
    if not reply_markup:
        if race.race_option():
            reply_markup = options_race(race.race_option())
        else:
            text = "Let's choose a class:"
            reply_markup = choice_class
            await Form.class_choice.set()
    async with state.proxy() as data:
        data['race'] = race
    await query.message.edit_text(text=text, reply_markup=reply_markup)  
   
 
@dp.callback_query_handler(lambda callback: callback.data in About.all_list('classes'), state=Form.class_choice)
async def create_2_q_class(query: types.CallbackQuery, state: FSMContext):
    """race selection"""
    async with state.proxy() as data:
        race = data['race']
        character = Character(query.data, race)
        data['race'] = None
        data['character'] = character
    text = f"Let's select {character.skills_opt['choice']} skills from the class:"
    reply_markup = choice_skills(character)
    await query.message.edit_text(text, reply_markup=reply_markup)


@dp.callback_query_handler(state=Form.class_choice)
async def create_2_q(query: types.CallbackQuery, state: FSMContext):
    """choice of skills of the class"""
    skill = False    
    async with state.proxy() as data:
        character = data['character']
    if query.data[:6] == 'Skill:':
        skill = True
    
    if character.add_data(query.data, skill = skill):
        if skill:
            text = f"Select {character.skills_opt['choice']} skills:"
            reply_markup = choice_skills(character)
        else:
            text = f"Select {character.other_opt['choose']} instruments :"
            reply_markup = choice_other(character)
    else:
        if character.other_opt:
            text = f"Let's select {character.other_opt['choose']} instruments from the class:"
            reply_markup = choice_other(character)
        else:
            text = f"""You have points: {character.points}
Choose where to distribute {character.points[0]} points:"""
            reply_markup = points_choice(character)
            await Form.points_choice.set()
                
    async with state.proxy() as data:
        data['character'] = character
    await query.message.edit_text(text, reply_markup=reply_markup)


@dp.callback_query_handler(state=Form.points_choice)
async def create_3_q(query: types.CallbackQuery, state: FSMContext):
    """the third stage of character creation"""
    async with state.proxy() as data:
        character = data['character']
    character.add_cha(query.data)
    if character.points:
        text = f"""You have points: {character.points}
Choose where to distribute {character.points[0]} points:"""
        reply_markup = points_choice(character)
    else: 
        character.hp_create()
        await Form.save_form.set()
        text = character
        reply_markup = save
    
    async with state.proxy() as data:
        data['character'] = character
    await query.message.edit_text(text, reply_markup=reply_markup)


@dp.callback_query_handler(lambda callback: callback.data == 'save', state=Form.save_form)
async def save_q(query: types.CallbackQuery):
    """Please give a name"""
    await query.message.edit_text('Give the character a name')
    
    
@dp.message_handler(state=Form.save_form)
async def final(message: types.Message, state: FSMContext):
    """completion of character creation"""
    async with state.proxy() as data:
        character = data['character']
    character.name_create(message.text, message)
    DB_func.save_character(character)
    text = "Your character has been saved!\n You can find him in /my_characters menu"
    await message.answer(text)
    await state.finish()  
"""        !!!!!!END OF CREATING OF CHARACTER!!!!!!           """





"""          !!!!!!WORK WITH USER CHARACTERS!!!!!!               """
@dp.message_handler(commands=['my_characters'], state = '*')
async def characters(message: types.Message):
    """List of user characters"""
    characters = [*DB_func.find_characters(message['from']['username'])]
    if characters: 
        text = 'Select the desired character:'
        reply_markup = characters_keyboard(characters)
        await Form.character_info.set()
    else:
        text = "You don't have characters(\nYou can create them in /create menu"
        reply_markup = None
    await message.answer(text, reply_markup=reply_markup)


@dp.callback_query_handler(state = Form.character_info)
async def character_info(query: types.CallbackQuery, state: FSMContext):
    """Character data"""
    if query.data == 'delete':
        async with state.proxy() as data:
            id = data['id']
        DB_func.delete_character(id)
        await state.finish()
        text = 'Character deleted'
        reply_markup = None
    else:
        text = Character_from_db(DB_func.find_by_id(int(query.data)))
        reply_markup = delete
        async with state.proxy() as data:
            data['id'] = int(query.data)
    await query.message.edit_text(text, reply_markup=reply_markup)
"""        !!!!!!END OF WORK WITH USER CHARACTERS!!!!!!             """   




"""          !!!!!!SEARCHING CHARACTER!!!!!!               """
@dp.message_handler(commands=['search'], state = '*')
async def search_cmnd(message: types.Message):
    """Switch to search mode"""
    await Form.search.set()
    await message.answer("Enter character ID:")
    
    
@dp.message_handler(state = Form.search)
async def search(message: types.Message, state: FSMContext):
    """Search by ID"""
    id = message.text
    if id.isdigit():
        character_dict = DB_func.find_by_id(int(id))
        if not character_dict:
            text = 'Character not found'
        else:
            text = Character_from_db(character_dict)
    else: 
        text = 'ID must be numbers'
    await message.answer(text)
"""          !!!!!!END OF SEARCHING CHARACTER!!!!!!               """    
    


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)