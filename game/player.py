import pygame
from PIL import Image, ImageTk
import customtkinter as ctk
import os
from datetime import datetime
import json
import sys
from pathlib import Path

# Adiciona o diretório pai ao path para importar corretamente
sys.path.append(str(Path(__file__).parent.parent))
from game.cards import Card, CardRarity, CardType

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
        self.avatar = None
        self.load_avatar()
        self.load_initial_cards()
        
    def load_initial_cards(self):
        try:
            # Verifica o caminho atual
            current_dir = os.path.dirname(os.path.abspath(__file__))
            initial_deck_path = os.path.join(current_dir, "..", "data", "initial_deck.json")
            print(f"Tentando carregar deck inicial de: {initial_deck_path}")
            
            if not os.path.exists(initial_deck_path):
                raise FileNotFoundError(f"Arquivo não encontrado: {initial_deck_path}")
            
            with open(initial_deck_path, "r") as f:
                initial_cards = json.load(f)
                print(f"Cards encontrados: {len(initial_cards['cards'])}")
                
                # Primeiro adiciona todos os cards à coleção
                for card_data in initial_cards["cards"]:
                    print(f"Processando card: {card_data['name']}")
                    try:
                        card = Card(
                            id=card_data["id"],
                            name=card_data["name"],
                            rarity=CardRarity(card_data["rarity"]),
                            type=CardType(card_data["type"]),
                            attack=card_data["attack"],
                            defense=card_data["defense"],
                            cost=card_data["cost"],
                            description=card_data["description"],
                            special_ability=card_data.get("special_ability")
                        )
                        self.cards.append(card)  # Adiciona direto à lista de cards
                        print(f"Card {card.name} adicionado à coleção")
                    except Exception as e:
                        print(f"Erro ao criar card {card_data['name']}: {str(e)}")
                
                # Depois adiciona os cards ao deck
                for card in self.cards:
                    self.deck.append(card)  # Adiciona direto ao deck
                    print(f"Card {card.name} adicionado ao deck")
                    
        except FileNotFoundError as e:
            print(f"Arquivo de deck inicial não encontrado: {str(e)}")
        except Exception as e:
            print(f"Erro ao carregar deck inicial: {str(e)}")
        
    def load_avatar(self):
        try:
            avatar_path = f"assets/avatars/{self.username}.png"
            self.avatar = Image.open(avatar_path)
            self.avatar = self.avatar.resize((100, 100))
            self.avatar = ctk.CTkImage(self.avatar, size=(100, 100))
        except FileNotFoundError:
            # Use default avatar if not found
            try:
                default_avatar = Image.open("assets/avatars/default.png")
                default_avatar = default_avatar.resize((100, 100))
                self.avatar = ctk.CTkImage(default_avatar, size=(100, 100))
            except FileNotFoundError:
                # Create a colorful placeholder if no default avatar
                self.avatar = ctk.CTkImage(Image.new('RGB', (100, 100), color='blue'), size=(100, 100))
                
    def earn_gold(self, amount):
        self.gold += amount
        # Play gold sound effect
        try:
            gold_sound = pygame.mixer.Sound("assets/sounds/gold.mp3")
            gold_sound.play()
        except:
            pass
            
    def spend_gold(self, amount):
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
        
    def earn_gems(self, amount):
        self.gems += amount
        # Play gem sound effect
        try:
            gem_sound = pygame.mixer.Sound("assets/sounds/gem.mp3")
            gem_sound.play()
        except:
            pass
            
    def spend_gems(self, amount):
        if self.gems >= amount:
            self.gems -= amount
            return True
        return False
        
    def add_card(self, card):
        if card not in self.cards:  # Evita duplicatas
            self.cards.append(card)
            # Play card sound effect
            try:
                card_sound = pygame.mixer.Sound("assets/sounds/card_collect.mp3")
                card_sound.play()
            except:
                pass
            
    def add_to_deck(self, card):
        if len(self.deck) < 8 and card in self.cards and card not in self.deck:  # Evita duplicatas no deck
            self.deck.append(card)
            return True
        return False
        
    def earn_trophies(self, amount):
        self.trophies += amount
        # Play trophy sound effect
        try:
            trophy_sound = pygame.mixer.Sound("assets/sounds/trophy.mp3")
            trophy_sound.play()
        except:
            pass
            
    def add_chest(self, chest_type, unlock_time):
        self.chests.append({
            "type": chest_type,
            "unlock_time": unlock_time,
            "unlocked": False
        })
        # Play chest sound effect
        try:
            chest_sound = pygame.mixer.Sound("assets/sounds/chest_collect.mp3")
            chest_sound.play()
        except:
            pass 