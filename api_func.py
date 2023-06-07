import requests
from pymongo import MongoClient
import re
from aiogram import types



client_con = MongoClient()
obj_db = client_con['CharDnD']
lists = obj_db['list']

api_address = 'https://www.dnd5eapi.co/'
api_races = api_address + 'api/races/'
api_classes = api_address + 'api/classes/'

all_races = [i['name'] for i in requests.get(url= api_races).json()['results']]

# if not lists.find():
# lists.insert_one({'races' : all_races})
races = obj_db['races']
# races.insert_many([requests.get(url= api_races + i).json() for i in all_races])

all_classes = [i['index'] for i in requests.get(url= api_classes).json()['results']]
classes = obj_db['classes']
# classes.insert_many([requests.get(url= api_classes + i).json() for i in all_classes])

class About:
    @staticmethod
    def race_about(data: str , more: bool = False):
        race_data = requests.get(url= api_races + data.lower()).json()
        
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
        self.race_data = requests.get(url= api_races + race.lower()).json()
        self.name = self.race_data['name']
        self.speed = self.race_data['speed']
        self.bonuses = {i["ability_score"]["name"] : i['bonus'] for i in self.race_data['ability_bonuses']}
        self.bonuse_opt = self.race_data.get('ability_bonus_options')
        self.size = self.race_data['size']
        self.proficiencies = [i['name'][7:] for i in self.race_data['starting_proficiencies']] if self.race_data['starting_proficiencies'] else None
        self.proficiencies_opt = self.race_data.get('starting_proficiency_options')
        self.languages = [i['index'] for i in self.race_data['languages']]
        self.languages_opt = self.race_data.get('language_options')
        self.traits = [i['index'] for i in self.race_data['traits']]
        self.subraces = [i['name'] for i in self.race_data['subraces']] if self.race_data['subraces'] else None

    
    def race_option(self) -> list:
        options = [self.bonuse_opt, self.proficiencies_opt, self.languages_opt]
        answer = [{'str' : f'Choose {i["choose"]} {i["type"]}:',
                'choose': i['choose'],
                'cha' : [el['ability_score']['name'] if i['type'] == "ability_bonuses" else el['item']['name'] for el in i['from']['options']],
                'type' : i['type']} for i in options if i]
        if self.subraces:
            answer.append({'type' : 'subraces', 'choose' : self.subraces})
        return answer
# print(Race('Half-Elf').race_option())