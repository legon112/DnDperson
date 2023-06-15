"""Keyboards for Bot"""
from aiogram import types

from api_func import About, Character

confirm_button = types.InlineKeyboardButton('Confirm', callback_data='confirm')
more_dutton = types.InlineKeyboardButton('More', callback_data='more')


create = types.InlineKeyboardButton('Сreate your own', callback_data='create')
create_random = types.InlineKeyboardButton('Create random character', callback_data='random')
start_1_k = types.InlineKeyboardMarkup().add(create, create_random)

choice_race = types.InlineKeyboardMarkup().add(*[types.InlineKeyboardButton(i, callback_data=i) for i in About.all_list('races')])

choice_class = types.InlineKeyboardMarkup().add(*[types.InlineKeyboardButton(i, callback_data=i) for i in About.all_list('classes')])

save = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Save', callback_data='save'))
delete = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton('Delete', callback_data='delete'))


def confirm_race(more : bool)-> types.InlineKeyboardMarkup:
    """Function to generate race confirmation keyboard

    Args:
        more (bool): Checker to display more detailed information

    Returns:
        types.InlineKeyboardMarkup
    """
    keyboard = types.InlineKeyboardMarkup().add(confirm_button)
    if not more:
        keyboard.add(more_dutton)
    return keyboard


def options_race(options : list) -> types.InlineKeyboardMarkup:
    """function to generate keyboard with types of optional skills race

    Args:
        options (list): list of options skills

    Returns:
        types.InlineKeyboardMarkup
    """
    return types.InlineKeyboardMarkup().add(*[types.InlineKeyboardButton(i['type'].capitalize(), callback_data=i['type']) for i in options])


def options_class(options : list) -> types.InlineKeyboardMarkup:
    """function to generate keyboard with types of optional skills class

    Args:
        options (list): list of options skills

    Returns:
        types.InlineKeyboardMarkup
    """
    return types.InlineKeyboardMarkup().add(*[types.InlineKeyboardButton(i['type'].capitalize(), callback_data=i['type']) for i in options])


def options_choose(options : list, type : str = None) -> types.InlineKeyboardMarkup:
    """function to generate keyboard with optional profincies

    Args:
        options (list): list of options profincies
        type (str, optional): _description_. Defaults to None.

    Returns:
        types.InlineKeyboardMarkup
    """
    if type:
        for i in options:
            if i['type'] == type:
                return types.InlineKeyboardMarkup().add(*[types.InlineKeyboardButton(el, callback_data=el) for el in i['cha']])
    else:
        return types.InlineKeyboardMarkup().add(*[types.InlineKeyboardButton(i, callback_data=i) for i in options['cha']])
    
    
def choice_skills(character : Character) -> types.InlineKeyboardMarkup:
    """function to generate keyboard with optional skills

    Args:
        character (Character): Character

    Returns:
        types.InlineKeyboardMarkup: _description_
    """
    return types.InlineKeyboardMarkup().add(*[types.InlineKeyboardButton(i, callback_data=i) for i in character.skills_opt['options']])


def choice_other(character : Character) -> types.InlineKeyboardMarkup:
    """function to generate keyboard with optional profincies of class

    Args:
        character (Character): Character

    Returns:
        types.InlineKeyboardMarkup: _description_
    """
    return types.InlineKeyboardMarkup().add(*[types.InlineKeyboardButton(i, callback_data=i) for i in character.other_opt['options']])


def points_choice(character : Character) -> types.InlineKeyboardMarkup:
    """a function to generate a keyboard to allocate skill points

    Args:
        character (Character): Character
    Returns:
        types.InlineKeyboardMarkup
    """
    return types.InlineKeyboardMarkup().add(*[types.InlineKeyboardButton(i, callback_data=i) for i in character.characteristics if not character.characteristics[i]['points']])


def characters_keyboard(characters : Character) -> types.InlineKeyboardMarkup:
    """function to generate keyboard with user characters

    Args:
        characters (Character): user characters

    Returns:
        types.InlineKeyboardMarkup
    """
    return types.InlineKeyboardMarkup().add(*[types.InlineKeyboardButton(i['name'], callback_data=i['id']) for i in characters])