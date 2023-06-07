from aiogram import types
from api_func import all_races

confirm_button = types.InlineKeyboardButton('Confirm', callback_data='confirm')
back_button = types.InlineKeyboardButton('Back', callback_data='back')
more_dutton = types.InlineKeyboardButton('More', callback_data='more')


create = types.InlineKeyboardButton('Сreate your own', callback_data='create')
create_random = types.InlineKeyboardButton('Create random character', callback_data='random')
start_1_k = types.InlineKeyboardMarkup().add(create, create_random)

choice_race = types.InlineKeyboardMarkup().add(*[types.InlineKeyboardButton(i, callback_data=i) for i in all_races],back_button)


def confirm_race(more : bool)-> types.InlineKeyboardMarkup:
    keyboard = types.InlineKeyboardMarkup().add(confirm_button, back_button)
    if not more:
        keyboard.add(more_dutton)
    return keyboard

def options_race(options : list) -> types.InlineKeyboardMarkup:
    return types.InlineKeyboardMarkup().add(*[types.InlineKeyboardButton(i['type'].capitalize(), callback_data=i['type']) for i in options])


