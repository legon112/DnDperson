"""Classes and Functions for work of Bot"""
import re

import requests
from aiogram import types
from peewee import *
from pymongo import MongoClient



api_address = 'https://www.dnd5eapi.co'

client_con = MongoClient()
obj_db = client_con['NoDnD']


class Proficiencies(Model):
    """Class model for SQL Database"""
    profic = CharField()
    type = CharField()
    class Meta:
        """Meta class for SQL Database"""
        database = SqliteDatabase('DnD.db')


class About:
    """Class with functions for getting information of characteristics"""
    
    @staticmethod
    def all_list(type_ : str) -> list:
        """ Method to get a list with all items of the specified class
        
        Args:
            type_ (str): type of items
        Returns:
            list: list of all items of the specified class
        """
        return [i['name'] for i in requests.get(url= api_address + f'/api/{type_}').json()['results']]
    
    @staticmethod
    def get_type(prof : str)->str:
        """Method to get Proficiencies type
        
        Args:
            prof (str): proficiencies
        Returns:
            str: type of proficiencies
        """
        return Proficiencies.get(Proficiencies.profic == prof).type
    
    @staticmethod
    def race_about(data: str , more: bool = False) -> str:
        """ Method to get race description

        Args:
            data (str): race name
            more (bool, optional): option for more detailed writer

        Returns:
            str: race description
        """
        race_data = requests.get(url= api_address + '/api/races/' + data.lower()).json()
        
        answer_list = []
        answer_list.append(race_data['name'])
        answer_list.append(f'Speed: {race_data["speed"]}')
        answer_list.append('Bonuses: '+', '.join([f'{i["ability_score"]["name"]} + {i["bonus"]}' for i in race_data['ability_bonuses']]))
        if 'ability_bonus_options' in race_data:
            answer_list.append(f'Bonus options: {race_data["ability_bonus_options"]["choose"]}')
        answer_list.append('Languages: '+ About.characteristic(race_data, 'name', 'languages'))
        if more: 
            answer_list[-1] += f'; {race_data["language_desc"]}'
        answer_list.append('Size: ' + race_data['size'])
        if more: 
            answer_list[-1] += f'; {race_data["size_description"]}'
        if race_data['starting_proficiencies']:
            answer_list.append('Proficiencies: '+ About.characteristic(race_data, 'index', 'starting_proficiencies'))
        if 'starting_proficiency_options' in race_data:
            answer_list.append(f'Proficiency options: {race_data["starting_proficiency_options"]["choose"]}')
        answer_list.append('Traits: '+About.characteristic(race_data, 'name', 'traits'))
        
        return '\n'.join(answer_list)
    
    @staticmethod
    def characteristic(data: dict, key_ind : str, key_cha: str) -> str:
        """ Method to get the string representation of the list of characteristics

        Args:
            data (dict): dictionary with information about the characteristic
            key_ind (str): name key
            key_cha (str): characteristic key

        Returns:
            str: String representation of the list of characteristics
        """
        return ', '.join([f'{i[key_ind]}' for i in data[key_cha]])
    
    
    
class Race():
    """Describes the unified attributes and methods for work with them"""
    def __init__(self, race: str) -> None:
        """Method to create an object of the Race class

        Args:
            race (str): Race name
        """
        self.race_data = requests.get(url= api_address + '/api/races/' + race.lower()).json()
        self.name = self.race_data['name']
        self.speed = self.race_data['speed']
        self.bonuses = {i["ability_score"]["name"] : i['bonus'] for i in self.race_data['ability_bonuses']}
        self.bonuse_opt = self.race_data.get('ability_bonus_options')
        self.size = self.race_data['size']
        self.proficiencies = [{'name' : i['name'], 'type': About.get_type(i['name'])} for i in self.race_data['starting_proficiencies']]
        self.skill = set()
        self.prof_dict = {i.type : set() for i in Proficiencies.select(Proficiencies.type).group_by(Proficiencies.type) if i.type != 'Skills'}
        self.proficiencies_opt = {'choose' :  self.race_data['starting_proficiency_options']['choose'],'options' : [{'name' : i['item']['name'], 'type': About.get_type(i['item']['name'])} for i in self.race_data['starting_proficiency_options']['from']['options']]} if self.race_data.get('starting_proficiency_options') else None
        if self.proficiencies:
            for i in self.proficiencies:
                if i['type'] == 'Skills':
                    self.skill.add(i['name'])
                else:
                    self.prof_dict[i['type']].add(i['name'])
                    
        self.languages = {i['name'] for i in self.race_data['languages']}
        self.languages_opt = self.race_data.get('language_options')
        self.traits = [i['index'] for i in self.race_data['traits']]
        
    def __str__(self) -> str:
        """Magic method for string representation of the object of class Race

        Returns:
            str: String representation
        """
        return f'''Race: {self.name}
    Speed: {self.speed}
    Bonuses: {self.bonuses}
    Size: {self.size}
    Skills: {self.skill}
    Languages: {self.languages}'''

    def add_data(self, type_: str, characteristik: str):
        """Method for adding race data

        Args:
            type_ (str): Type of race
            characteristik (str): Name of characteristik

        Returns:
            Nonetype: if option list is empty
            dict: dict of options if it is not empty
        """
        
        if type_ == 'ability-scores':
            options = self.bonuse_opt['from']['options']
            for i in range(len(options)):
                if options[i]['ability_score']['name'] == characteristik:
                    self.bonuses.update({characteristik : options[i]['bonus']})
                    self.bonuse_opt['choose'] -= 1
                    options.pop(i)
                    if not self.bonuse_opt['choose']:
                        self.bonuse_opt = None
                    return self.bonuse_opt
                
        elif type_ == 'languages':
            options = self.languages_opt['from']['options']
            for i in range(len(options)):
                if options[i]['item']['name'] == characteristik:
                    self.languages.add(characteristik)
                    self.languages_opt['choose'] -= 1
                    options.pop(i)
                    if not self.languages_opt['choose']:
                        self.languages_opt = None
                    return self.languages_opt
        
        elif type_ == 'proficiencies':
            options = self.proficiencies_opt['options']             
            for i in range(len(options)):
                sub_type = options[i]['type']
                if options[i]['name'] == characteristik:
                    if sub_type == 'Skills':
                        self.skill.add(characteristik)
                    else:
                        self.prof_dict[sub_type].add(characteristik)
                    self.proficiencies_opt['choose'] -= 1
                    options.pop(i)
                    if not self.proficiencies_opt['choose']:
                        self.proficiencies_opt = None
                    return self.proficiencies_opt
                
    def race_option(self) -> list:
        """Method to get a list of dictionarty of all optional characteristics

        Returns:
            list: list of dictionarty of all optional characteristics
        """
        bonus = self.bonuse_opt
        prof = self.proficiencies_opt
        languages = self.languages_opt
        if bonus: 
            bonus = {'str' : f'Choose {bonus["choose"]} {bonus["type"]}:',
                'choose': bonus['choose'],
                'cha' : [i['ability_score']['name'] for i in bonus['from']['options']],
                'type' : bonus['type'],
                'bonus' : bonus['from']['options'][0]['bonus']}
        if prof: 
            prof = {'str' : f'Choose {prof["choose"]} proficiencies',
                'choose' : prof['choose'],
                'type' : 'proficiencies',
                'cha' : [i['name'] for i in prof['options']]}
        if languages: 
            languages = {'str' : f'Choose {languages["choose"]} {languages["type"]}',
                'choose' : languages['choose'],
                'type' : languages['type'],
                'cha' : [el['item']['name'] for el in languages['from']['options']],}
        return [i for i in (bonus, languages, prof) if i]
    
    
    
class Character():
    """Describes the unified attributes and methods for work with them"""
    
    def __init__(self, classes: str, race : Race) -> None:
        """Method to create an object of the Character class

        Args:
            classes (str): Name of the class
            race (Race): Finished object of class race
        """
        self.class_data = requests.get(url= api_address + '/api/classes/' + classes.lower()).json()
        self.level = 1
        self.prof_bonus = 2
        self.classes = self.class_data['name']
        self.hit_die = self.class_data['hit_die']
        self.race = race.name
        self.speed = race.speed
        self.bonuses = race.bonuses
        self.characteristics = {i : {'points': 0, 'mod' : None} for i in About.all_list('ability-scores')}
        self.points = [15,14,13,12,10,8]
        self.size = race.size
        self.proficiencies = [{'name' : i['name'], 'type': About.get_type(i['name'])} for i in self.class_data['proficiencies']]
        self.skill = race.skill
        self.prof_dict = race.prof_dict
        for i in self.proficiencies:
            if i['type'] == 'Skills':
                if not i['name'] in self.skill:
                    self.skill.add(i['name']) 
            else:
                if not i['name'] in self.prof_dict[i['type']]:
                    self.prof_dict[i['type']].add(i['name'])
        self.languages = race.languages
        self.traits = race.traits
        self.traits.extend([i['name'] for i in requests.get(url= api_address + '/api/classes/' + classes.lower() + '/levels/1').json()['features']])
        self.skills_opt = {'choice' : self.class_data['proficiency_choices'][0]['choose'],'options':[el['item']['name'] for el in self.class_data['proficiency_choices'][0]['from']['options'] if not el['item']['name'] in self.skill]}
        self.other_opt = dict()
        if len(self.class_data['proficiency_choices']) > 1:
            self.other_opt['choose'] = self.class_data['proficiency_choices'][1]['choose']
            self.other_opt['options'] = set()
            options = self.class_data['proficiency_choices'][1]['from']['options']
            if options[0].get('choice'):
                for i in options:
                    self.other_opt['options'].update({el['item']['name']for el in i['choice']['from']['options'] if not el['item']['name']  in self.prof_dict[About.get_type(el['item']['name'])]})
            else:
                self.other_opt['options'].update({el['item']['name'] for el in options if not el['item']['name'] in self.prof_dict[About.get_type(el['item']['name'])]})
        self.spellcasting = requests.get(url= api_address + '/api/classes/' + classes.lower() + '/levels/1').json().get('spellcasting')
        if self.spellcasting:
            keys = list(self.spellcasting.keys())
            index = 0
            dict_spell = dict()
            while self.spellcasting[keys[index]]:
                dict_spell[keys[index]] = self.spellcasting[keys[index]]
                index += 1
            self.spellcasting = dict_spell
                    
    def __str__(self) -> str:
        """Magic method for string representation of the object of class Character

        Returns:
            str: String representation
        """
        answer =  f'''Race: {self.race}
Class: {self.classes}
Level: {self.level}\n'''
        for i in self.characteristics: 
            answer += f"{i}: {self.characteristics[i]['points']}, mod {self.characteristics[i]['mod']}\n"
        answer += f'''Speed: {self.speed}
Prof bonus: {self.prof_bonus}
Hits: {self.hp}
Hit dice: {self.hit_die}
Size: {self.size}\n'''
        answer += 'Skills: ' + ', '.join([i[7:] for i in self.skill]) + '\nLanguages: ' + ', '.join(self.languages) + '\n'
        answer += 'Traits: ' + ', '.join(self.traits) + '\n'
        for i in self.prof_dict:
            if self.prof_dict[i]:
                answer += f"{i}: " + ', '.join([el[14:] if i == 'Saving Throws' else el for el in self.prof_dict[i] ]) + "\n"
        if self.spellcasting:
            for i in self.spellcasting:
                answer += f"{i.replace('_', ' ').capitalize()}: {self.spellcasting[i]}\n"
        return answer
    
    def in_dict(self) -> dict:
        """Method for dictionary representation of the object of class Character

        Returns:
            dict: Dictionary representation 
        """
        return {
            'id' : self.id,
            'name' : self.name,
            'level' : self.level,
            'prof_bonus' : self.prof_bonus,
            'classes' : self.classes,
            'hit_die' : self.hit_die,
            'race' : self.race,
            'speed' : self.speed,
            'hp' : self.hp,
            'characteristics' : self.characteristics,
            'size' : self.size,
            'prof_dict' : {i : list(self.prof_dict[i]) for i in self.prof_dict if self.prof_dict[i]},
            'skills' : list(self.skill),
            'languages' : list(self.languages),
            'traits' : self.traits,
            'spellcasting' : self.spellcasting,
            'user' : self.user
        }
    
    def add_data(self, prof : str, *, skill : bool = True):
        """Method for adding class data

        Args:
            prof (str): Proficiencies
            skill (bool, optional): Counter to indicate whether the proficiencies is a skill. Defaults to True.

        Returns:
            Nonetype: if option list is empty
            dict: dict of options if it is not empty
        """
        if skill:
            self.skill.add(prof)
            options = self.skills_opt['options']
            for i in range(len(options)):
                if options[i] == prof:
                    options.pop(i)
                    break
            self.skills_opt['choice'] -= 1
            if not self.skills_opt['choice']: 
                self.skills_opt = None
            return self.skills_opt
        else:
            self.prof_dict[About.get_type(prof)].add(prof)
            options = self.other_opt['options']
            for i in options:
                if i == prof:
                    options.remove(i)
                    break
            self.other_opt['choose'] -= 1
            if not self.other_opt['choose']: 
                self.other_opt = None
            return self.other_opt
        
    def add_cha(self, cha : str):
        """Method for setting the characteristic value

        Args:
            cha (str): Name of the characteristic
        """
        point = self.points.pop(0)
        if self.bonuses.get(cha):
            point += self.bonuses[cha]
        self.characteristics[cha] = {'points' : point, 'mod' : (point-10)//2}
        
    def hp_create(self):
        """method for setting HP value"""
        mod = self.characteristics['CON']['mod']
        if mod < 0:
            mod = 0
        self.hp = self.hit_die + mod
        
    def name_create(self, name : str, id : dict):
        """method to set character name and id and the user who created the character

        Args:
            name (str): Name of the character
            id (dict): Message data from name
        """
        self.name = name
        self.id = id.message_id
        self.user = id['from']['username']
        
        
        
class Character_from_db():
    """Describes the unified attributes and methods for work with them"""
    
    def __init__(self, character : dict) -> None:
        """Method to create an object of the Character_from_db class

        Args:
            character (dict): character information dictionary
        """
        self.id = character['id']
        self.name = character['name']
        self.hp = character['hp']
        self.level = character['level']
        self.prof_bonus = character['prof_bonus']
        self.classes = character['classes']
        self.hit_die = character['hit_die']
        self.race = character['race']
        self.speed = character['speed']
        self.characteristics = character['characteristics']
        self.size = character['size']
        self.skills = set(character['skills'])
        self.prof_dict = {i : set(character['prof_dict'][i]) for i in character['prof_dict']}
        self.languages = set(character['languages'])
        self.traits = character['traits']
        self.spellcasting = character['spellcasting']
        
    def __str__(self) -> str:
        """Magic method for string representation of the object of class Character_from_db

        Returns:
            str: String representation
        """
        answer =  f'''ID: {self.id}
Name: {self.name}
Race: {self.race}
Class: {self.classes}
Level: {self.level}\n'''
        for i in self.characteristics: 
            answer += f"{i}: {self.characteristics[i]['points']}, mod {self.characteristics[i]['mod']}\n"
        answer += f'''Speed: {self.speed}
Prof bonus: {self.prof_bonus}
Hits: {self.hp}
Hit dice: {self.hit_die}
Size: {self.size}\n'''
        answer += 'Skills: ' + ', '.join([i[7:] for i in self.skills]) + '\nLanguages: ' + ', '.join(self.languages) + '\n'
        answer += 'Traits: ' + ', '.join(self.traits) + '\n'
        for i in self.prof_dict:
            if self.prof_dict[i]:
                answer += f"{i}: " + ', '.join([el[14:] if i == 'Saving Throws' else el for el in self.prof_dict[i] ]) + "\n"
        if self.spellcasting:
            for i in self.spellcasting:
                answer += f"{i.replace('_', ' ').capitalize()}: {self.spellcasting[i]}\n"
        return answer
        
        
        
class DB_func():
    """class with methods for working Bot with the NoSQL database"""
    
    @staticmethod
    def save_character(character : Character):
        """Method to save character in database

        Args:
            character (Character): Character to save
        """
        obj_db['Characters'].insert_one(character.in_dict())
        
    @staticmethod
    def find_characters(user : str):
        """Method to find user characters

        Args:
            user (str): Name of the user

        Returns:
            NoneType: if characters not found
            list : list of user characters if found
        """
        return obj_db['Characters'].aggregate([{'$match' : {'user' : user}}])
    
    @staticmethod
    def find_by_id(id : int) -> dict:
        """Method for searching character by ID

        Args:
            id (int): id of the character

        Returns:
            dict: dictionary of characters
        """
        return obj_db['Characters'].find_one({'id' : {'$eq' : id}})
    
    @staticmethod
    def delete_character(id : int) -> None:
        """Method for deleting a character by ID

        Args:
            id (int): id of the character
        """
        obj_db['Characters'].delete_one({'id' : id})
        





# my_collection = obj_db['Race']
# my_collection.insert_many([requests.get(url= api_address + 'api/races/' + i.lower()).json() for i in About.all_list('races')])

# my_collection = obj_db['Classes']
# my_collection.insert_many([requests.get(url= api_address + 'api/classes/' + i.lower()).json() for i in About.all_list('classes')])