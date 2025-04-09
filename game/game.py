import pygame
import json
import os
from datetime import datetime
import random
from PIL import Image, ImageTk
import customtkinter as ctk

class Game:
    def __init__(self):
        self.players = {}
        
        # Initialize pygame mixer
        try:
            pygame.mixer.init()
        except pygame.error:
            print("Warning: Sound system initialization failed. Game will run without sound.")
            
        # Initialize empty sounds dictionary
        self.sounds = {}
        
        # Create necessary directories if they don't exist
        os.makedirs("data", exist_ok=True)
        os.makedirs("assets/sounds", exist_ok=True)
        os.makedirs("assets/cards", exist_ok=True)
        os.makedirs("assets/avatars", exist_ok=True)
        
        # Try to load sounds, but continue if they don't exist
        sound_files = {
            "battle": "assets/sounds/battle.mp3",
            "victory": "assets/sounds/victory.mp3",
            "defeat": "assets/sounds/defeat.mp3",
            "card_play": "assets/sounds/card_play.mp3",
            "menu": "assets/sounds/menu.mp3",
            "shop": "assets/sounds/shop.mp3",
            "chest_open": "assets/sounds/chest_open.mp3"
        }
        
        for sound_name, sound_path in sound_files.items():
            try:
                self.sounds[sound_name] = pygame.mixer.Sound(sound_path)
            except (FileNotFoundError, pygame.error):
                print(f"Warning: Sound file {sound_path} not found or could not be loaded.")
                
        if not self.sounds:
            print("No sound files were loaded. Game will run without sound.")
            print("Sound files should be placed in assets/sounds/ directory.")
            
        self.load_game_data()
        
    def safe_play_sound(self, sound_name):
        """Safely play a sound if it exists in the sounds dictionary."""
        if sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except pygame.error:
                pass  # Ignore sound playing errors
                
    def load_game_data(self):
        try:
            with open("data/game_data.json", "r") as f:
                data = json.load(f)
                self.players = {username: Player(username) for username in data.get("players", [])}
                for player in self.players.values():
                    player.load_avatar()
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
            self.players[username].load_avatar()
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
            
        # Play battle sound
        self.safe_play_sound("battle")
        
        # Calculate scores with special abilities
        p1_score = 0
        p2_score = 0
        
        for card in p1_deck:
            p1_score += card.attack + card.defense
            if card.special_ability:
                p1_score += 2  # Bonus for special abilities
                
        for card in p2_deck:
            p2_score += card.attack + card.defense
            if card.special_ability:
                p2_score += 2  # Bonus for special abilities
                
        # Add some randomness to make battles more exciting
        p1_score += random.randint(-2, 2)
        p2_score += random.randint(-2, 2)
        
        winner = player1 if p1_score > p2_score else player2
        loser = player2 if winner == player1 else player1
        
        # Play victory/defeat sounds
        if winner == player1:
            self.safe_play_sound("victory")
        else:
            self.safe_play_sound("defeat")
            
        # Award rewards
        self.players[winner].earn_gold(100)
        self.players[winner].earn_trophies(30)
        self.players[loser].earn_gold(50)
        self.players[loser].earn_trophies(10)
        
        self.save_game_data()
        return winner, loser 