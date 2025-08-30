import telebot
import random
import requests
from datetime import datetime, timedelta
from config import token

class Pokemon:
    pokemons = {}

    def __init__(self, username: str, name: str, img: str):
        self.username = username
        self.name = name
        self.img = img
        self.hp = random.randint(60, 110)
        self.max_hp = self.hp
        self.power = random.randint(5, 15)
        self.wins = 0
        self.last_feed_time = datetime.now() - timedelta(seconds=1000)
        Pokemon.pokemons[username] = self

    def info(self):
        return (
            f"Твой покемон: {self.name.capitalize()}\n"
            f"HP: {self.hp}/{self.max_hp}\n"
            f"Сила: {self.power}\n"
            f"Побед: {self.wins}"
        )

    def feed(self, feed_interval=20, hp_increase=10):
        current_time = datetime.now()
        delta_time = timedelta(seconds=feed_interval)
        if current_time - self.last_feed_time > delta_time:
            self.hp = min(self.max_hp, self.hp + hp_increase)
            self.last_feed_time = current_time
            return f"Здоровье покемона увеличено. Текущее здоровье: {self.hp}/{self.max_hp}"
        else:
            next_time = self.last_feed_time + delta_time
            return f"Рано кормить! Следующее кормление доступно в: {next_time.strftime('%H:%M:%S')}"

    def attack(self, enemy):
        if isinstance(enemy, Wizard):
            chance = random.randint(1, 5)
            if chance == 1:
                return f"{enemy.name.capitalize()} применил магический щит 🛡 и избежал урона!"
        if self.hp <= 0:
            return f"{self.name.capitalize()} выбыл и не может атаковать!"
        if enemy.hp <= 0:
            return f"{enemy.name.capitalize()} уже повержен!"
        damage = self.power
        if enemy.hp > damage:
            enemy.hp -= damage
            return (
                f"{self.name.capitalize()} атакует {enemy.name.capitalize()} на {damage} урона. "
                f"У врага осталось {enemy.hp}/{enemy.max_hp} HP."
            )
        else:
            enemy.hp = 0
            self.wins += 1
            self.hp = min(self.max_hp, self.hp + 5)
            return f"{self.name.capitalize()} победил {enemy.name.capitalize()}! 🎉"


class Wizard(Pokemon):
    def __init__(self, username: str, name: str, img: str):
        super().__init__(username, name, img)
        self.hp += 20
        self.max_hp = self.hp

    def info(self):
        return "У тебя покемон-волшебник 🧙\n" + super().info()

    def feed(self, feed_interval=20, hp_increase=15):
        return super().feed(feed_interval, hp_increase)


class Fighter(Pokemon):
    def __init__(self, username: str, name: str, img: str):
        super().__init__(username, name, img)
        self.power += 5

    def attack(self, enemy):
        super_boost = random.randint(5, 15)
        self.power += super_boost
        result = super().attack(enemy)
        self.power -= super_boost
        return result + f"\nБоец применил супер-атаку силой: {super_boost}! 💥"

    def info(self):
        return "У тебя покемон-боец 🥊\n" + super().info()

    def feed(self, feed_interval=10, hp_increase=10):
        return super().feed(feed_interval, hp_increase)


def create_random_pokemon(username: str):
    pokemon_number = random.randint(1, 500)
    url = f"https://pokeapi.co/api/v2/pokemon/{pokemon_number}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200:
            data = r.json()
            name = data["forms"][0]["name"]
            img = data["sprites"]["front_default"]
        else:
            name = "pikachu"
            img = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"
    except:
        name = "pikachu"
        img = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/25.png"
    cls = random.choice([Wizard, Fighter])
    return cls(username, name, img)


@bot.message_handler(commands=["start"])
def start(message):
    username = message.from_user.username or message.from_user.first_name
    if username not in Pokemon.pokemons:
        poke = create_random_pokemon(username)
        bot.send_message(message.chat.id, f"Привет, @{username}! Тебе достался покемон:")
        bot.send_photo(message.chat.id, poke.img, caption=poke.info())
    else:
        bot.send_message(message.chat.id, "У тебя уже есть покемон!")


@bot.message_handler(commands=["my_pokemon"])
def my_pokemon(message):
    username = message.from_user.username or message.from_user.first_name
    if username in Pokemon.pokemons:
        poke = Pokemon.pokemons[username]
        bot.send_photo(message.chat.id, poke.img, caption=poke.info())
    else:
        bot.send_message(message.chat.id, "У тебя пока нет покемона, используй /start!")


@bot.message_handler(commands=["info"])
def info(message):
    username = message.from_user.username or message.from_user.first_name
    if username in Pokemon.pokemons.keys():
        pok = Pokemon.pokemons[username]
        bot.send_photo(message.chat.id, pok.img, caption=pok.info())
    else:
        bot.send_message(message.chat.id, "У тебя пока нет покемона, используй /start!")


@bot.message_handler(commands=["feed"])
def feed(message):
    username = message.from_user.username or message.from_user.first_name
    if username in Pokemon.pokemons:
        pok = Pokemon.pokemons[username]
        result = pok.feed()
        bot.send_message(message.chat.id, result)
    else:
        bot.send_message(message.chat.id, "У тебя пока нет покемона, используй /start!")


@bot.message_handler(commands=["fight"])
def fight(message):
    username = message.from_user.username or message.from_user.first_name
    if username not in Pokemon.pokemons:
        bot.send_message(message.chat.id, "Сначала создай покемона: /start")
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.send_message(message.chat.id, "Используй: /fight @имя_тренера")
        return
    enemy_name = parts[1].replace("@", "")
    if enemy_name not in Pokemon.pokemons:
        bot.send_message(message.chat.id, f"У @{enemy_name} нет покемона!")
        return
    player = Pokemon.pokemons[username]
    enemy = Pokemon.pokemons[enemy_name]
    result = player.attack(enemy)
    bot.send_message(message.chat.id, result)


if __name__ == "__main__":
    print("Бот запущен... ✅")
    bot.infinity_polling()


