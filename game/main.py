import customtkinter as ctk
import json
import os
from PIL import Image, ImageTk
from datetime import datetime
import random
import pygame
import time
from player import Player
from cards import Card, CardRarity, CardType
from battle import BattleManager

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

        p1 = self.players[player1]
        p2 = self.players[player2]

        if not p1.deck or not p2.deck:
            return None

        # Play battle sound
        self.safe_play_sound("battle")

        # Create battle manager and start battle
        battle_manager = BattleManager()
        result, message = battle_manager.start_battle(p1, p2)

        if result:
            winner = p1 if result["winner"] == p1.username else p2
            loser = p2 if winner == p1 else p1

            # Play victory/defeat sounds
            self.safe_play_sound("victory")

            self.save_game_data()
            return winner.username, loser.username
        
        return None

class GameApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Configure window
        self.title("Royal Clash")
        self.geometry("1200x800")
        
        # Set appearance mode and color theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Initialize game
        self.game = Game()
        self.current_player = None
        
        # Setup UI
        self.setup_ui()
        
    def setup_ui(self):
        # Main container with animated background
        self.main_container = ctk.CTkFrame(self, fg_color="#2b2b2b")
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Background image with animation
        try:
            bg_image = Image.open("assets/backgrounds/main_menu.png")
            bg_image = bg_image.resize((1200, 800))
            self.bg_photo = ctk.CTkImage(bg_image, size=(1200, 800))
            self.bg_label = ctk.CTkLabel(self.main_container, image=self.bg_photo, text="")
            self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except FileNotFoundError:
            # If no background image, use a colorful gradient
            self.main_container.configure(fg_color="#2b2b2b")
            
        # Login frame with animation
        self.login_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.login_frame.pack(fill="both", expand=True)
        
        # Animated title
        title_label = ctk.CTkLabel(self.login_frame, 
                                 text="Royal Clash", 
                                 font=("Comic Sans MS", 48, "bold"),
                                 text_color="#FFD700")
        title_label.pack(pady=40)
        
        # Animated login box with sparkle effect
        self.login_box = ctk.CTkFrame(self.login_frame, 
                                    fg_color="#1a1a1a",
                                    corner_radius=20)
        self.login_box.pack(pady=20, padx=100, fill="both", expand=True)
        
        # Username entry with animation
        self.username_entry = ctk.CTkEntry(self.login_box, 
                                         placeholder_text="Enter your name, brave warrior!",
                                         font=("Comic Sans MS", 16),
                                         height=40,
                                         corner_radius=10)
        self.username_entry.pack(pady=20, padx=20)
        
        # Animated login button
        self.login_button = ctk.CTkButton(self.login_box, 
                                        text="Start Adventure!", 
                                        command=self.login,
                                        font=("Comic Sans MS", 16, "bold"),
                                        height=40,
                                        fg_color="#FFD700",
                                        hover_color="#FFA500",
                                        text_color="black",
                                        corner_radius=10)
        self.login_button.pack(pady=20, padx=20)
        
        # Game frame (initially hidden)
        self.game_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        
    def login(self):
        username = self.username_entry.get()
        if not username:
            return
            
        if username not in self.game.players:
            self.game.add_player(username)
            # Give new player basic cards
            player = self.game.players[username]
            basic_cards = [
                Card(
                    id="basic_warrior",
                    name="Basic Warrior",
                    rarity=CardRarity.COMMON,
                    type=CardType.TROOP,
                    attack=5,
                    defense=5,
                    cost=2,
                    description="A basic warrior ready for battle"
                ),
                Card(
                    id="basic_archer",
                    name="Basic Archer",
                    rarity=CardRarity.COMMON,
                    type=CardType.TROOP,
                    attack=4,
                    defense=3,
                    cost=2,
                    description="A basic archer with ranged attacks"
                ),
                Card(
                    id="basic_tank",
                    name="Basic Tank",
                    rarity=CardRarity.COMMON,
                    type=CardType.TROOP,
                    attack=3,
                    defense=7,
                    cost=3,
                    description="A basic tank with high defense"
                )
            ]
            for card in basic_cards:
                player.add_card(card)
                player.add_to_deck(card)
            
        self.current_player = self.game.players[username]
        self.show_game_frame()
        
    def show_game_frame(self):
        self.login_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)
        
        # Player stats with animated avatar
        stats_frame = ctk.CTkFrame(self.game_frame, fg_color="#1a1a1a")
        stats_frame.pack(fill="x", padx=20, pady=10)
        
        # Animated avatar
        if self.current_player.avatar:
            avatar_label = ctk.CTkLabel(stats_frame, image=self.current_player.avatar, text="")
            avatar_label.pack(side="left", padx=10)
            
        # Stats with colorful text
        stats_text = f"Player: {self.current_player.username} | Level: {self.current_player.level} | Gold: {self.current_player.gold} | Gems: {self.current_player.gems} | Trophies: {self.current_player.trophies}"
        ctk.CTkLabel(stats_frame, 
                    text=stats_text,
                    font=("Comic Sans MS", 14),
                    text_color="white").pack(side="left", padx=10)
        
        # Main menu buttons with hover effects
        menu_frame = ctk.CTkFrame(self.game_frame, fg_color="transparent")
        menu_frame.pack(fill="x", padx=20, pady=20)
        
        button_style = {
            "font": ("Comic Sans MS", 16, "bold"),
            "height": 50,
            "width": 200,
            "corner_radius": 10,
            "fg_color": "#FFD700",
            "hover_color": "#FFA500",
            "text_color": "black"
        }
        
        # Battle button with sword icon
        battle_button = ctk.CTkButton(menu_frame, 
                                    text="⚔️ Battle", 
                                    command=self.show_battle_screen,
                                    **button_style)
        battle_button.pack(side="left", padx=10, pady=10)
        
        # Deck Builder button with cards icon
        deck_button = ctk.CTkButton(menu_frame, 
                                  text="🃏 Deck Builder", 
                                  command=self.show_deck_builder,
                                  **button_style)
        deck_button.pack(side="left", padx=10, pady=10)
        
        # Shop button with coins icon
        shop_button = ctk.CTkButton(menu_frame, 
                                  text="💰 Shop", 
                                  command=self.show_shop,
                                  **button_style)
        shop_button.pack(side="left", padx=10, pady=10)
        
        # Chests button with chest icon
        chests_button = ctk.CTkButton(menu_frame, 
                                    text="🎁 Chests", 
                                    command=self.show_chests,
                                    **button_style)
        chests_button.pack(side="left", padx=10, pady=10)
        
    def show_battle_screen(self):
        # Play menu sound
        self.game.safe_play_sound("menu")
        
        # Clear current content
        for widget in self.game_frame.winfo_children():
            widget.destroy()
            
        # Create battle frame with animated background
        battle_frame = ctk.CTkFrame(self.game_frame, fg_color="#1a1a1a")
        battle_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        try:
            battle_bg = Image.open("assets/backgrounds/battle.png")
            battle_bg = battle_bg.resize((1200, 800))
            battle_bg_photo = ctk.CTkImage(battle_bg, size=(1200, 800))
            battle_bg_label = ctk.CTkLabel(battle_frame, image=battle_bg_photo, text="")
            battle_bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except FileNotFoundError:
            pass
        
        # Header with animated back button
        header_frame = ctk.CTkFrame(battle_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        
        back_button = ctk.CTkButton(header_frame, 
                                  text="← Back to Castle", 
                                  command=self.show_game_frame,
                                  width=150,
                                  fg_color="#FFD700",
                                  hover_color="#FFA500",
                                  text_color="black",
                                  font=("Comic Sans MS", 14, "bold"),
                                  corner_radius=10)
        back_button.pack(side="left")
        
        # Battle title with animation
        title_label = ctk.CTkLabel(header_frame,
                                 text="⚔️ Battle Arena ⚔️",
                                 font=("Comic Sans MS", 24, "bold"),
                                 text_color="#FFD700")
        title_label.pack(side="left", padx=20)
        
        # Battle options frame with animations
        options_frame = ctk.CTkFrame(battle_frame, fg_color="transparent")
        options_frame.pack(expand=True, pady=50)
        
        # Quick match button with sword animation
        quick_match_button = ctk.CTkButton(options_frame,
                                         text="⚔️ Quick Match",
                                         command=self.start_quick_match,
                                         font=("Comic Sans MS", 20, "bold"),
                                         width=300,
                                         height=60,
                                         fg_color="#FFD700",
                                         hover_color="#FFA500",
                                         text_color="black",
                                         corner_radius=15)
        quick_match_button.pack(pady=20)
        
        # Training button with shield animation
        training_button = ctk.CTkButton(options_frame,
                                      text="🛡️ Training Battle",
                                      command=self.start_training_battle,
                                      font=("Comic Sans MS", 20, "bold"),
                                      width=300,
                                      height=60,
                                      fg_color="#FFD700",
                                      hover_color="#FFA500",
                                      text_color="black",
                                      corner_radius=15)
        training_button.pack(pady=20)
        
    def start_quick_match(self):
        # Simulate finding an opponent
        opponent_names = ["Alex", "Sarah", "John", "Emma", "Michael"]
        opponent_name = random.choice([name for name in opponent_names if name != self.current_player.username])
        
        # Add opponent to game if not exists
        if opponent_name not in self.game.players:
            self.game.add_player(opponent_name)
            # Give opponent basic cards
            opponent = self.game.players[opponent_name]
            basic_cards = [
                Card(
                    id="basic_warrior",
                    name="Basic Warrior",
                    rarity=CardRarity.COMMON,
                    type=CardType.TROOP,
                    attack=5,
                    defense=5,
                    cost=2,
                    description="A basic warrior ready for battle"
                ),
                Card(
                    id="basic_archer",
                    name="Basic Archer",
                    rarity=CardRarity.COMMON,
                    type=CardType.TROOP,
                    attack=4,
                    defense=3,
                    cost=2,
                    description="A basic archer with ranged attacks"
                ),
                Card(
                    id="basic_tank",
                    name="Basic Tank",
                    rarity=CardRarity.COMMON,
                    type=CardType.TROOP,
                    attack=3,
                    defense=7,
                    cost=3,
                    description="A basic tank with high defense"
                )
            ]
            for card in basic_cards:
                opponent.add_card(card)
                opponent.add_to_deck(card)
        
        # Start battle
        result = self.game.battle(self.current_player.username, opponent_name)
        if result is None:
            # Show error message if battle cannot be started
            self.show_battle_error("Cannot start battle. Make sure both players have cards in their deck.")
            return
            
        winner, loser = result
        self.show_battle_result(winner, loser)
        
    def start_training_battle(self):
        # Create a training bot
        bot_name = "Training Bot"
        if bot_name not in self.game.players:
            self.game.add_player(bot_name)
            bot = self.game.players[bot_name]
            # Give bot some basic cards
            basic_cards = [
                Card(
                    id="basic_warrior",
                    name="Basic Warrior",
                    rarity=CardRarity.COMMON,
                    type=CardType.TROOP,
                    attack=5,
                    defense=5,
                    cost=2,
                    description="A basic warrior ready for battle"
                ),
                Card(
                    id="basic_archer",
                    name="Basic Archer",
                    rarity=CardRarity.COMMON,
                    type=CardType.TROOP,
                    attack=4,
                    defense=3,
                    cost=2,
                    description="A basic archer with ranged attacks"
                ),
                Card(
                    id="basic_tank",
                    name="Basic Tank",
                    rarity=CardRarity.COMMON,
                    type=CardType.TROOP,
                    attack=3,
                    defense=7,
                    cost=3,
                    description="A basic tank with high defense"
                )
            ]
            for card in basic_cards:
                bot.add_card(card)
                bot.add_to_deck(card)
        
        # Start battle
        result = self.game.battle(self.current_player.username, bot_name)
        if result is None:
            # Show error message if battle cannot be started
            self.show_battle_error("Cannot start battle. Make sure you have cards in your deck.")
            return
            
        winner, loser = result
        self.show_battle_result(winner, loser)
        
    def show_battle_result(self, winner, loser):
        # Clear battle frame
        for widget in self.game_frame.winfo_children():
            widget.destroy()
            
        # Create result frame with animated background
        result_frame = ctk.CTkFrame(self.game_frame, fg_color="#1a1a1a")
        result_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Show result message with animation
        result_text = "🎉 Victory! 🎉" if winner == self.current_player.username else "😢 Defeat! 😢"
        result_color = "#FFD700" if winner == self.current_player.username else "#FF4444"
        
        result_label = ctk.CTkLabel(result_frame,
                                  text=result_text,
                                  font=("Comic Sans MS", 48, "bold"),
                                  text_color=result_color)
        result_label.pack(pady=50)
        
        # Show rewards with animation
        rewards_text = "🎁 Rewards:\n"
        if winner == self.current_player.username:
            rewards_text += "💰 100 Gold\n"
            rewards_text += "🏆 30 Trophies"
        else:
            rewards_text += "💰 50 Gold\n"
            rewards_text += "🏆 10 Trophies"
        
        rewards_label = ctk.CTkLabel(result_frame,
                                   text=rewards_text,
                                   font=("Comic Sans MS", 24),
                                   text_color="white")
        rewards_label.pack(pady=30)
        
        # Continue button with animation
        continue_button = ctk.CTkButton(result_frame,
                                      text="Continue Adventure!",
                                      command=self.show_game_frame,
                                      font=("Comic Sans MS", 20, "bold"),
                                      width=200,
                                      height=50,
                                      fg_color="#FFD700",
                                      hover_color="#FFA500",
                                      text_color="black",
                                      corner_radius=10)
        continue_button.pack(pady=40)
        
    def show_deck_builder(self):
        # Play menu sound
        self.game.safe_play_sound("menu")
        
        # Clear current content
        for widget in self.game_frame.winfo_children():
            widget.destroy()
            
        # Create deck builder frame with animated background
        deck_frame = ctk.CTkFrame(self.game_frame, fg_color="#1a1a1a")
        deck_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        try:
            deck_bg = Image.open("assets/backgrounds/deck_builder.png")
            deck_bg = deck_bg.resize((1200, 800))
            deck_bg_photo = ctk.CTkImage(deck_bg, size=(1200, 800))
            deck_bg_label = ctk.CTkLabel(deck_frame, image=deck_bg_photo, text="")
            deck_bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except FileNotFoundError:
            pass
        
        # Header with animated back button
        header_frame = ctk.CTkFrame(deck_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        
        back_button = ctk.CTkButton(header_frame, 
                                  text="← Back to Castle", 
                                  command=self.show_game_frame,
                                  width=150,
                                  fg_color="#FFD700",
                                  hover_color="#FFA500",
                                  text_color="black",
                                  font=("Comic Sans MS", 14, "bold"),
                                  corner_radius=10)
        back_button.pack(side="left")
        
        # Deck Builder title with animation
        title_label = ctk.CTkLabel(header_frame,
                                 text="🃏 Deck Builder 🃏",
                                 font=("Comic Sans MS", 24, "bold"),
                                 text_color="#FFD700")
        title_label.pack(side="left", padx=20)
        
        # Create two columns for cards
        columns_frame = ctk.CTkFrame(deck_frame, fg_color="transparent")
        columns_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Available cards column
        available_frame = ctk.CTkFrame(columns_frame, fg_color="#2b2b2b")
        available_frame.pack(side="left", fill="both", expand=True, padx=10)
        
        available_label = ctk.CTkLabel(available_frame,
                                     text="Your Cards",
                                     font=("Comic Sans MS", 16, "bold"),
                                     text_color="#FFD700")
        available_label.pack(pady=10)
        
        # Create scrollable frame for available cards
        available_cards_frame = ctk.CTkScrollableFrame(available_frame, fg_color="transparent")
        available_cards_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Current deck column
        deck_frame = ctk.CTkFrame(columns_frame, fg_color="#2b2b2b")
        deck_frame.pack(side="right", fill="both", expand=True, padx=10)
        
        deck_label = ctk.CTkLabel(deck_frame,
                                text="Your Deck",
                                font=("Comic Sans MS", 16, "bold"),
                                text_color="#FFD700")
        deck_label.pack(pady=10)
        
        # Create scrollable frame for deck cards
        deck_cards_frame = ctk.CTkScrollableFrame(deck_frame, fg_color="transparent")
        deck_cards_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Display available cards
        for card in self.current_player.cards:
            card_frame = ctk.CTkFrame(available_cards_frame, fg_color="#1a1a1a")
            card_frame.pack(fill="x", pady=5)
            
            # Card image
            if card.image:
                image_label = ctk.CTkLabel(card_frame, image=card.image, text="")
                image_label.pack(side="left", padx=5)
            
            # Card info
            info_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=5)
            
            name_label = ctk.CTkLabel(info_frame,
                                    text=card.name,
                                    font=("Comic Sans MS", 14, "bold"),
                                    text_color=card.get_rarity_color())
            name_label.pack(anchor="w")
            
            stats_label = ctk.CTkLabel(info_frame,
                                     text=f"⚔️ {card.attack} | 🛡️ {card.defense} | 💰 {card.cost}",
                                     font=("Comic Sans MS", 12),
                                     text_color="white")
            stats_label.pack(anchor="w")
            
            # Add to deck button
            add_button = ctk.CTkButton(card_frame,
                                     text="Add to Deck",
                                     command=lambda c=card: self.add_card_to_deck(c),
                                     width=100,
                                     fg_color="#FFD700",
                                     hover_color="#FFA500",
                                     text_color="black",
                                     font=("Comic Sans MS", 12, "bold"),
                                     corner_radius=5)
            add_button.pack(side="right", padx=5)
        
        # Display deck cards
        for card in self.current_player.deck:
            card_frame = ctk.CTkFrame(deck_cards_frame, fg_color="#1a1a1a")
            card_frame.pack(fill="x", pady=5)
            
            # Card image
            if card.image:
                image_label = ctk.CTkLabel(card_frame, image=card.image, text="")
                image_label.pack(side="left", padx=5)
            
            # Card info
            info_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
            info_frame.pack(side="left", fill="x", expand=True, padx=5)
            
            name_label = ctk.CTkLabel(info_frame,
                                    text=card.name,
                                    font=("Comic Sans MS", 14, "bold"),
                                    text_color=card.get_rarity_color())
            name_label.pack(anchor="w")
            
            stats_label = ctk.CTkLabel(info_frame,
                                     text=f"⚔️ {card.attack} | 🛡️ {card.defense} | 💰 {card.cost}",
                                     font=("Comic Sans MS", 12),
                                     text_color="white")
            stats_label.pack(anchor="w")
            
            # Remove from deck button
            remove_button = ctk.CTkButton(card_frame,
                                        text="Remove",
                                        command=lambda c=card: self.remove_card_from_deck(c),
                                        width=100,
                                        fg_color="#FF4444",
                                        hover_color="#FF0000",
                                        text_color="white",
                                        font=("Comic Sans MS", 12, "bold"),
                                        corner_radius=5)
            remove_button.pack(side="right", padx=5)
            
    def add_card_to_deck(self, card):
        if len(self.current_player.deck) < 8:
            if self.current_player.add_to_deck(card):
                self.show_deck_builder()
                # Play card sound effect
                self.game.safe_play_sound("card_play")
            else:
                self.show_error("You already have this card in your deck!")
        else:
            self.show_error("Your deck is full! Remove a card first.")
            
    def remove_card_from_deck(self, card):
        if card in self.current_player.deck:
            self.current_player.deck.remove(card)
            self.show_deck_builder()
            
    def show_error(self, message):
        error_frame = ctk.CTkFrame(self.game_frame, fg_color="#1a1a1a")
        error_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        error_label = ctk.CTkLabel(error_frame,
                                text="⚠️ Oops! ⚠️",
                                font=("Comic Sans MS", 32, "bold"),
                                text_color="#FF4444")
        error_label.pack(pady=30)
        
        message_label = ctk.CTkLabel(error_frame,
                                  text=message,
                                  font=("Comic Sans MS", 16),
                                  text_color="white")
        message_label.pack(pady=20)
        
        back_button = ctk.CTkButton(error_frame,
                                 text="Back",
                                 command=self.show_deck_builder,
                                 font=("Comic Sans MS", 16, "bold"),
                                 width=150,
                                 height=40,
                                 fg_color="#FFD700",
                                 hover_color="#FFA500",
                                 text_color="black",
                                 corner_radius=10)
        back_button.pack(pady=30)
        
    def show_shop(self):
        # Play shop sound
        self.game.safe_play_sound("shop")
        
        # Clear current content
        for widget in self.game_frame.winfo_children():
            widget.destroy()
            
        # Create shop frame
        shop_frame = ctk.CTkFrame(self.game_frame, fg_color="#1a1a1a")
        shop_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header with back button
        header_frame = ctk.CTkFrame(shop_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=10, pady=10)
        
        back_button = ctk.CTkButton(header_frame, 
                                  text="← Back to Castle", 
                                  command=self.show_game_frame,
                                  width=150,
                                  fg_color="#FFD700",
                                  hover_color="#FFA500",
                                  text_color="black",
                                  font=("Comic Sans MS", 14, "bold"),
                                  corner_radius=10)
        back_button.pack(side="left")
        
        # Shop title
        title_label = ctk.CTkLabel(header_frame,
                                 text="💰 Shop 💰",
                                 font=("Comic Sans MS", 24, "bold"),
                                 text_color="#FFD700")
        title_label.pack(side="left", padx=20)
        
        # Player resources
        resources_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        resources_frame.pack(side="right")
        
        gold_label = ctk.CTkLabel(resources_frame,
                                text=f"💰 {self.current_player.gold}",
                                font=("Comic Sans MS", 16, "bold"),
                                text_color="#FFD700")
        gold_label.pack(side="left", padx=10)
        
        gems_label = ctk.CTkLabel(resources_frame,
                                text=f"💎 {self.current_player.gems}",
                                font=("Comic Sans MS", 16, "bold"),
                                text_color="#00BFFF")
        gems_label.pack(side="left", padx=10)
        
        # Shop tabs
        tabs_frame = ctk.CTkFrame(shop_frame, fg_color="transparent")
        tabs_frame.pack(fill="x", padx=20, pady=10)
        
        cards_button = ctk.CTkButton(tabs_frame,
                                   text="Cards",
                                   command=self.show_cards_shop,
                                   width=150,
                                   fg_color="#FFD700",
                                   hover_color="#FFA500",
                                   text_color="black",
                                   font=("Comic Sans MS", 14, "bold"),
                                   corner_radius=10)
        cards_button.pack(side="left", padx=5)
        
        chests_button = ctk.CTkButton(tabs_frame,
                                    text="Chests",
                                    command=self.show_chests_shop,
                                    width=150,
                                    fg_color="#FFD700",
                                    hover_color="#FFA500",
                                    text_color="black",
                                    font=("Comic Sans MS", 14, "bold"),
                                    corner_radius=10)
        chests_button.pack(side="left", padx=5)
        
        # Show cards shop by default
        self.show_cards_shop()
        
    def show_cards_shop(self):
        # Clear shop content
        for widget in self.game_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()
        
        # Create cards shop content
        shop_content = ctk.CTkFrame(self.game_frame, fg_color="transparent")
        shop_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create scrollable frame for cards
        cards_frame = ctk.CTkScrollableFrame(shop_content, fg_color="transparent")
        cards_frame.pack(fill="both", expand=True)
        
        # Display available cards for purchase
        for card in self.game.cards.values():
            if card not in self.current_player.cards:  # Only show cards the player doesn't have
                card_frame = ctk.CTkFrame(cards_frame, fg_color="#2b2b2b")
                card_frame.pack(fill="x", pady=5, padx=10)
                
                # Card image
                if card.image:
                    image_label = ctk.CTkLabel(card_frame, image=card.image, text="")
                    image_label.pack(side="left", padx=5)
                
                # Card info
                info_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=5)
                
                name_label = ctk.CTkLabel(info_frame,
                                        text=card.name,
                                        font=("Comic Sans MS", 14, "bold"),
                                        text_color=card.get_rarity_color())
                name_label.pack(anchor="w")
                
                stats_label = ctk.CTkLabel(info_frame,
                                         text=f"⚔️ {card.attack} | 🛡️ {card.defense} | 💰 {card.cost}",
                                         font=("Comic Sans MS", 12),
                                         text_color="white")
                stats_label.pack(anchor="w")
                
                # Price and buy button
                price_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
                price_frame.pack(side="right", padx=5)
                
                price = self.calculate_card_price(card)
                price_label = ctk.CTkLabel(price_frame,
                                         text=f"💰 {price}",
                                         font=("Comic Sans MS", 14, "bold"),
                                         text_color="#FFD700")
                price_label.pack(side="left", padx=5)
                
                buy_button = ctk.CTkButton(price_frame,
                                         text="Buy",
                                         command=lambda c=card, p=price: self.buy_card(c, p),
                                         width=100,
                                         fg_color="#FFD700",
                                         hover_color="#FFA500",
                                         text_color="black",
                                         font=("Comic Sans MS", 12, "bold"),
                                         corner_radius=5)
                buy_button.pack(side="right", padx=5)
                
    def show_chests_shop(self):
        # Clear shop content
        for widget in self.game_frame.winfo_children():
            if isinstance(widget, ctk.CTkFrame):
                widget.destroy()
        
        # Create chests shop content
        shop_content = ctk.CTkFrame(self.game_frame, fg_color="transparent")
        shop_content = ctk.CTkFrame(self.game_frame, fg_color="transparent", name="shop_content")
        shop_content.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Create grid for chests
        chests_frame = ctk.CTkFrame(shop_content, fg_color="transparent")
        chests_frame.pack(fill="both", expand=True)
        
        # Define chest types and their prices
        chests = [
            {"name": "Wooden Chest", "price": 100, "color": "#8B4513", "rarity": "Common"},
            {"name": "Silver Chest", "price": 250, "color": "#C0C0C0", "rarity": "Rare"},
            {"name": "Golden Chest", "price": 500, "color": "#FFD700", "rarity": "Epic"},
            {"name": "Magic Chest", "price": 1000, "color": "#9932CC", "rarity": "Legendary"}
        ]
        
        # Display chests in a grid
        for i, chest in enumerate(chests):
            row = i // 2
            col = i % 2
            
            chest_frame = ctk.CTkFrame(chests_frame, fg_color="#2b2b2b")
            chest_frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
            
            # Chest image
            try:
                chest_image = Image.open(f"assets/chests/{chest['name'].lower().replace(' ', '_')}.png")
                chest_image = chest_image.resize((200, 200))
                chest_photo = ctk.CTkImage(chest_image, size=(200, 200))
                image_label = ctk.CTkLabel(chest_frame, image=chest_photo, text="")
                image_label.pack(pady=10)
            except FileNotFoundError:
                # Create placeholder if image not found
                placeholder = ctk.CTkLabel(chest_frame,
                                         text="🎁",
                                         font=("Comic Sans MS", 48),
                                         text_color=chest["color"])
                placeholder.pack(pady=10)
            
            # Chest info
            name_label = ctk.CTkLabel(chest_frame,
                                    text=chest["name"],
                                    font=("Comic Sans MS", 16, "bold"),
                                    text_color=chest["color"])
            name_label.pack()
            
            rarity_label = ctk.CTkLabel(chest_frame,
                                      text=f"Rarity: {chest['rarity']}",
                                      font=("Comic Sans MS", 12),
                                      text_color="white")
            rarity_label.pack()
            
            price_frame = ctk.CTkFrame(chest_frame, fg_color="transparent")
            price_frame.pack(pady=10)
            
            price_label = ctk.CTkLabel(price_frame,
                                     text=f"💰 {chest['price']}",
                                     font=("Comic Sans MS", 14, "bold"),
                                     text_color="#FFD700")
            price_label.pack(side="left", padx=5)
            
            buy_button = ctk.CTkButton(price_frame,
                                     text="Buy",
                                     command=lambda c=chest: self.buy_chest(c),
                                     width=100,
                                     fg_color="#FFD700",
                                     hover_color="#FFA500",
                                     text_color="black",
                                     font=("Comic Sans MS", 12, "bold"),
                                     corner_radius=5)
            buy_button.pack(side="right", padx=5)
            
    def calculate_card_price(self, card):
        # Base price based on rarity
        base_prices = {
            "Common": 50,
            "Rare": 100,
            "Epic": 250,
            "Legendary": 500
        }
        
        # Calculate price based on card stats and rarity
        price = base_prices.get(card.rarity, 50)
        price += (card.attack + card.defense) * 2
        price += card.cost * 5
        
        return price
        
    def buy_card(self, card, price):
        if self.current_player.gold >= price:
            self.current_player.spend_gold(price)
            self.current_player.add_card(card)
            self.show_shop()
            # Play purchase sound
            self.game.safe_play_sound("shop")
        else:
            self.show_error("Not enough gold!")
            
    def buy_chest(self, chest):
        if self.current_player.gold >= chest["price"]:
            self.current_player.spend_gold(chest["price"])
            self.current_player.add_chest(chest["name"], datetime.now())
            self.show_shop()
            # Play chest sound
            self.game.safe_play_sound("chest_collect")
        else:
            self.show_error("Not enough gold!")

    def show_chests(self):
        # Play menu sound
        self.game.safe_play_sound("menu")
        
        # Implement chests screen with opening animations
        pass

    def show_battle_error(self, message):
        # Clear battle frame
        for widget in self.game_frame.winfo_children():
            widget.destroy()
            
        # Create error frame with animated background
        error_frame = ctk.CTkFrame(self.game_frame, fg_color="#1a1a1a")
        error_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Show error message with animation
        error_label = ctk.CTkLabel(error_frame,
                                text="⚠️ Oops! ⚠️",
                                font=("Comic Sans MS", 32, "bold"),
                                text_color="#FF4444")
        error_label.pack(pady=30)
        
        message_label = ctk.CTkLabel(error_frame,
                                  text=message,
                                  font=("Comic Sans MS", 16),
                                  text_color="white")
        message_label.pack(pady=20)
        
        # Back button with animation
        back_button = ctk.CTkButton(error_frame,
                                 text="Back to Battle",
                                 command=self.show_battle_screen,
                                 font=("Comic Sans MS", 16, "bold"),
                                 width=150,
                                 height=40,
                                 fg_color="#FFD700",
                                 hover_color="#FFA500",
                                 text_color="black",
                                 corner_radius=10)
        back_button.pack(pady=30)

if __name__ == "__main__":
    app = GameApp()
    app.mainloop()