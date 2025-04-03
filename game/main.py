# Criar o arquivo main.py
cat > game/main.py << 'EOL'
import customtkinter as ctk
import json
import os
from PIL import Image, ImageTk
from datetime import datetime
import random
import pygame

class Card:
    def __init__(self, id, name, rarity, attack, defense, cost):
        self.id = id
        self.name = name
        self.rarity = rarity
        self.attack = attack
        self.defense = defense
        self.cost = cost
        self.level = 1
        self.experience = 0

    def upgrade(self):
        if self.experience >= self.level * 100:
            self.level += 1
            self.attack += self.level * 2
            self.defense += self.level * 2
            self.experience = 0
            return True
        return False

class Player:
    def __init__(self, username):
        self.username = username
        self.level = 1
        self.experience = 0
        self.gold = 1000
        self.gems = 50
        self.cards = []
        self.deck = []
        self.trophies = 0
        self.chests = []
        self.last_login = datetime.now()
        self.daily_rewards = []
        self.achievements = {}

    def earn_gold(self, amount):
        self.gold += amount

    def spend_gold(self, amount):
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False

    def earn_gems(self, amount):
        self.gems += amount

    def spend_gems(self, amount):
        if self.gems >= amount:
            self.gems -= amount
            return True
        return False

    def add_card(self, card):
        self.cards.append(card)

    def add_to_deck(self, card):
        if len(self.deck) < 8 and card in self.cards:
            self.deck.append(card)
            return True
        return False

    def earn_trophies(self, amount):
        self.trophies += amount

    def add_chest(self, chest_type, unlock_time):
        self.chests.append({
            "type": chest_type,
            "unlock_time": unlock_time,
            "unlocked": False
        })

class Game:
    def __init__(self):
        self.players = {}
        self.load_game_data()
        pygame.mixer.init()
        self.sounds = {
            "battle": pygame.mixer.Sound("assets/sounds/battle.mp3"),
            "victory": pygame.mixer.Sound("assets/sounds/victory.mp3"),
            "defeat": pygame.mixer.Sound("assets/sounds/defeat.mp3"),
            "card": pygame.mixer.Sound("assets/sounds/card.mp3")
        }

    def load_game_data(self):
        try:
            with open("data/game_data.json", "r") as f:
                data = json.load(f)
                self.players = {username: Player(username) for username in data.get("players", [])}
        except FileNotFoundError:
            self.players = {}

    def save_game_data(self):
        data = {
            "players": list(self.players.keys()),
            "last_save": datetime.now().isoformat()
        }
        with open("data/game_data.json", "w") as f:
            json.dump(data, f)

    def add_player(self, username):
        if username not in self.players:
            self.players[username] = Player(username)
            self.save_game_data()
            return True
        return False

    def battle(self, player1, player2):
        if player1 not in self.players or player2 not in self.players:
            return None

        p1_deck = self.players[player1].deck
        p2_deck = self.players[player2].deck

        if not p1_deck or not p2_deck:
            return None

        p1_score = sum(card.attack + card.defense for card in p1_deck)
        p2_score = sum(card.attack + card.defense for card in p2_deck)

        winner = player1 if p1_score > p2_score else player2
        loser = player2 if winner == player1 else player1

        self.players[winner].earn_gold(100)
        self.players[winner].earn_trophies(30)
        self.players[loser].earn_gold(50)
        self.players[loser].earn_trophies(10)

        self.save_game_data()
        return winner, loser

class GameApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Royal Clash")
        self.geometry("1200x800")
        self.configure(fg_color="#1a1a1a")
        
        self.game = Game()
        self.current_player = None
        
        self.setup_ui()
        
    def setup_ui(self):
        # Main container
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Login frame
        self.login_frame = ctk.CTkFrame(self.main_container)
        self.login_frame.pack(fill="both", expand=True)
        
        # Login widgets
        ctk.CTkLabel(self.login_frame, text="Royal Clash", font=("Helvetica", 32, "bold")).pack(pady=20)
        
        self.username_entry = ctk.CTkEntry(self.login_frame, placeholder_text="Username")
        self.username_entry.pack(pady=10)
        
        self.login_button = ctk.CTkButton(self.login_frame, text="Login", command=self.login)
        self.login_button.pack(pady=10)
        
        # Game frame (initially hidden)
        self.game_frame = ctk.CTkFrame(self.main_container)
        
    def login(self):
        username = self.username_entry.get()
        if not username:
            return
            
        if username not in self.game.players:
            self.game.add_player(username)
            
        self.current_player = self.game.players[username]
        self.show_game_frame()
        
    def show_game_frame(self):
        self.login_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)
        
        # Player stats
        stats_frame = ctk.CTkFrame(self.game_frame)
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        ctk.CTkLabel(stats_frame, text=f"Player: {self.current_player.username}").pack(side="left", padx=10)
        ctk.CTkLabel(stats_frame, text=f"Level: {self.current_player.level}").pack(side="left", padx=10)
        ctk.CTkLabel(stats_frame, text=f"Gold: {self.current_player.gold}").pack(side="left", padx=10)
        ctk.CTkLabel(stats_frame, text=f"Gems: {self.current_player.gems}").pack(side="left", padx=10)
        ctk.CTkLabel(stats_frame, text=f"Trophies: {self.current_player.trophies}").pack(side="left", padx=10)
        
        # Main menu buttons
        menu_frame = ctk.CTkFrame(self.game_frame)
        menu_frame.pack(fill="x", padx=20, pady=20)
        
        ctk.CTkButton(menu_frame, text="Battle", command=self.show_battle_screen).pack(side="left", padx=10)
        ctk.CTkButton(menu_frame, text="Deck Builder", command=self.show_deck_builder).pack(side="left", padx=10)
        ctk.CTkButton(menu_frame, text="Shop", command=self.show_shop).pack(side="left", padx=10)
        ctk.CTkButton(menu_frame, text="Chests", command=self.show_chests).pack(side="left", padx=10)
        
    def show_battle_screen(self):
        # Implement battle screen
        pass
        
    def show_deck_builder(self):
        # Implement deck builder
        pass
        
    def show_shop(self):
        # Implement shop
        pass
        
    def show_chests(self):
        # Implement chests screen
        pass

if __name__ == "__main__":
    app = GameApp()
    app.mainloop()
EOL
