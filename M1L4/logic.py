import requests
import random

class Pokemon:
    pokemons = {}

    def __init__(self, username):
        self.pokemon_number = random.randint(1, 1000)
        self.username = username

        self.name = self.get_name()
        self.img = self.get_img()

        Pokemon.pokemons[username] = self

    def get_name(self):
        url = f'https://pokeapi.co/api/v2/pokemon/{self.pokemon_number}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['forms'][0]['name']
        else:
            return "pikachu"

    def get_img(self):
        url = f'https://pokeapi.co/api/v2/pokemon/{self.pokemon_number}'
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            return data['sprites']['front_default']
        else:
            return "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"

    def info(self):
        return f"Твой покемон: {self.name.capitalize()} (№{self.pokemon_number})"


    def show_img(self):
        return self.img
