import requests
from pymongo import MongoClient
import re
from aiogram import types
from peewee import *


client_con = MongoClient()
obj_db = client_con['CharDnD']
lists = obj_db['list']

api_address = 'https://www.dnd5eapi.co/'


# if not lists.find():
# lists.insert_one({'races' : all_races})
# races = obj_db['races']
# races.insert_many([requests.get(url= api_races + i).json() for i in all_races])


# classes = obj_db['classes']
# classes.insert_many([requests.get(url= api_classes + i).json() for i in all_classes])

class Proficiencies(Model):
    profic = CharField()
    type = CharField()
    class Meta:
        database = SqliteDatabase('DnD.db')

class About:
    @staticmethod
    def all_list(type_):
        return [i['name'] for i in requests.get(url= api_address + f'api/{type_}').json()['results']]
    
    @staticmethod
    def get_type(prof : str)->str:
        return Proficiencies.get(Proficiencies.profic == prof).type
    
    @staticmethod
    def race_about(data: str , more: bool = False):
        race_data = requests.get(url= api_address + 'api/races/' + data.lower()).json()
        
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
        if race_data['subraces']:
            answer_list.append('Subraces: '+About.characteristic(race_data, 'name','subraces'))
        
        return '\n'.join(answer_list)
    
    @staticmethod
    def characteristic(data: dict, key_ind : str, key_cha: str):
        return ', '.join([f'{i[key_ind]}' for i in data[key_cha]])
    
    
class Race():
    def __init__(self, race: str):
        self.race_data = requests.get(url= api_address + 'api/races/' + race.lower()).json()
        self.name = self.race_data['name']
        self.speed = self.race_data['speed']
        self.bonuses = {i["ability_score"]["name"] : i['bonus'] for i in self.race_data['ability_bonuses']}
        self.bonuse_opt = self.race_data.get('ability_bonus_options')
        self.size = self.race_data['size']
        self.proficiencies = [{'name' : i['name'], 'type': About.get_type(i['name'])} for i in self.race_data['starting_proficiencies']]
        self.skill = []
        self.armor = []
        self.art_tool = []
        self.gaming_set = []
        self.musical_instr = []
        self.saving_throw = []
        self.tools = []
        self.weapons = []
        self.proficiencies_opt = {'choose' :  self.race_data['starting_proficiency_options']['choose'],'options' : [{'name' : i['item']['name'], 'type': About.get_type(i['item']['name'])} for i in self.race_data['starting_proficiency_options']['from']['options']]}
        for i in self.proficiencies_opt['options']:
            if i['type'] == 'Skills':
                self.skill.append(i['name'])
            elif i['type'] == 'Armor':
                self.armor.append(i['name'])
            elif i['type'] == "Artisan's Tools":
                self.art_tool.append(i['name'])
            elif i['type'] == "Gaming Sets":
                self.gaming_set.append(i['name'])
            elif i['type'] == "Musical Instruments":
                self.musical_instr.append(i['name'])
            elif i['type'] == "Saving Throwsr":
                self.saving_throw.append(i['name'])
            elif i['type'] == "Other":
                self.tools.append(i['name'])
            elif i['type'] == "Weapons":
                self.weapons.append(i['name'])
        self.languages = [i['name'] for i in self.race_data['languages']]
        self.languages_opt = self.race_data.get('language_options')
        self.traits = [i['index'] for i in self.race_data['traits']]
        self.subrace = None
        self.subraces = [i['name'] for i in self.race_data['subraces']] if self.race_data['subraces'] else None

    def add_data(self, type_: str, characteristik: str):
        
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
                    self.languages.append(characteristik)
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
                        self.skill.append(characteristik)
                    elif sub_type == 'Armor':
                        self.armor.append(characteristik)
                    elif sub_type == "Artisan's Tools":
                        self.art_tool.append(characteristik)
                    elif sub_type == "Gaming Sets":
                        self.gaming_set.append(characteristik)
                    elif sub_type == "Musical Instruments":
                        self.musical_instr.append(characteristik)
                    elif sub_type == "Saving Throwsr":
                        self.saving_throw.append(characteristik)
                    elif sub_type == "Other":
                        self.tools.append(characteristik)
                    elif sub_type == "Weapons":
                        self.weapons.append(characteristik)
                    self.proficiencies_opt['choose'] -= 1
                    options.pop(i)
                    if not self.proficiencies_opt['choose']:
                        self.proficiencies_opt = None
                    return self.proficiencies_opt
                
    def race_option(self) -> list:
        bonus = self.bonuse_opt
        prof = self.proficiencies_opt
        languages = self.languages_opt
        subrace = self.subraces
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
        if subrace:
            subrace = {'str' : 'Choose 1 subrace:','type' : 'subraces', 'choose': 1,'cha' : self.subraces}
        return [i for i in (bonus, languages, prof, subrace) if i]

# print([i['type'] for i in Race('half-elf').race_option()], sep= '\n\n')