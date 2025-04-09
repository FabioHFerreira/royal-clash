# Criar o arquivo cards.py
cat > game/cards.py << 'EOL'
import json
import random
from enum import Enum
from PIL import Image
import pygame
from PIL import Image, ImageTk
import customtkinter as ctk
import os

class CardRarity(Enum):
    COMMON = "Common"
    RARE = "Rare"
    EPIC = "Epic"
    LEGENDARY = "Legendary"

class CardType(Enum):
    TROOP = "Troop"
    SPELL = "Spell"
    BUILDING = "Building"

class Card:
    def __init__(self, id, name, rarity, type, attack, defense, cost, description, special_ability=None):
        self.id = id
        self.name = name
        self.rarity = rarity
        self.type = type
        self.attack = attack
        self.defense = defense
        self.cost = cost
        self.description = description
        self.special_ability = special_ability
        self.level = 1
        self.experience = 0
        self.image = None
        self.animation = None
        self.effects = []  # List of active effects on the card
        self.cooldown = 0  # Cooldown for special abilities
        self.element = None
        self.effect = None
        self.sound = None
        self.load_assets()

    def load_assets(self):
        # Load card image
        try:
            image_path = f"assets/cards/{self.id}.png"
            self.image = Image.open(image_path)
            self.image = self.image.resize((150, 200))
            self.image = ctk.CTkImage(self.image, size=(150, 200))
        except FileNotFoundError:
            # Create a colorful placeholder if image not found
            self.image = ctk.CTkImage(Image.new('RGB', (150, 200), color=self.get_rarity_color()), size=(150, 200))
            
        # Load animation if exists
        try:
            animation_path = f"assets/effects/{self.element}.png"
            self.animation = Image.open(animation_path)
            self.animation = self.animation.resize((50, 50))
            self.animation = ctk.CTkImage(self.animation, size=(50, 50))
        except FileNotFoundError:
            self.animation = None
            
        # Load sound effect
        try:
            sound_path = f"assets/sounds/card_play.mp3"
            self.sound = pygame.mixer.Sound(sound_path)
        except:
            self.sound = None

    def get_rarity_color(self):
        colors = {
            "Common": "#808080",  # Gray
            "Rare": "#4169E1",    # Blue
            "Epic": "#9932CC",    # Purple
            "Legendary": "#FFD700" # Gold
        }
        return colors.get(self.rarity, "#808080")
        
    def get_element_color(self):
        colors = {
            "Fire": "#FF4500",    # Orange Red
            "Ice": "#00BFFF",     # Deep Sky Blue
            "Lightning": "#FFD700", # Gold
            "Earth": "#8B4513",   # Saddle Brown
            "Water": "#1E90FF",   # Dodger Blue
            "Wind": "#98FB98"     # Pale Green
        }
        return colors.get(self.element, "#FFFFFF")
        
    def play_sound(self):
        if self.sound:
            self.sound.play()

    def upgrade(self):
        if self.experience >= self.level * 100:
            self.level += 1
            self.attack += self.level * 2
            self.defense += self.level * 2
            self.experience = 0
            return True
        return False

    def use_special_ability(self, target=None):
        if self.special_ability and self.cooldown <= 0:
            effect = self.special_ability(self, target)
            self.cooldown = 3  # Set cooldown to 3 turns
            return effect
        return None

    def add_effect(self, effect):
        self.effects.append(effect)

    def remove_effect(self, effect):
        if effect in self.effects:
            self.effects.remove(effect)

    def update_effects(self):
        # Update cooldown
        if self.cooldown > 0:
            self.cooldown -= 1

        # Process other effects
        for effect in self.effects[:]:
            effect.duration -= 1
            if effect.duration <= 0:
                self.remove_effect(effect)

class CardEffect:
    def __init__(self, name, duration, effect_type, value):
        self.name = name
        self.duration = duration
        self.effect_type = effect_type  # "buff", "debuff", "heal", "damage"
        self.value = value

class CardManager:
    def __init__(self):
        self.cards = {}
        self.load_cards()

    def load_cards(self):
        try:
            with open("data/cards.json", "r") as f:
                cards_data = json.load(f)
                for card_data in cards_data:
                    card = Card(
                        id=card_data["id"],
                        name=card_data["name"],
                        rarity=CardRarity(card_data["rarity"]),
                        type=CardType(card_data["type"]),
                        attack=card_data["attack"],
                        defense=card_data["defense"],
                        cost=card_data["cost"],
                        description=card_data["description"],
                        special_ability=self._create_special_ability(card_data.get("special_ability"))
                    )
                    card.load_image()
                    self.cards[card.id] = card
        except FileNotFoundError:
            self._create_default_cards()

    def _create_special_ability(self, ability_data):
        if not ability_data:
            return None
            
        def ability(card, target):
            if ability_data["type"] == "heal":
                # Heal target card or player
                if target:
                    target.defense = min(target.defense + ability_data["value"], target.defense * 2)
                    return f"Healed {ability_data['value']} health"
                return None
                
            elif ability_data["type"] == "buff":
                # Add buff effect to target
                effect = CardEffect(
                    name=ability_data["name"],
                    duration=ability_data["duration"],
                    effect_type="buff",
                    value=ability_data["value"]
                )
                target.add_effect(effect)
                return f"Applied {ability_data['name']} buff"
                
            elif ability_data["type"] == "debuff":
                # Add debuff effect to target
                effect = CardEffect(
                    name=ability_data["name"],
                    duration=ability_data["duration"],
                    effect_type="debuff",
                    value=ability_data["value"]
                )
                target.add_effect(effect)
                return f"Applied {ability_data['name']} debuff"
                
            elif ability_data["type"] == "damage":
                # Deal damage to target
                if target:
                    target.defense -= ability_data["value"]
                    return f"Dealt {ability_data['value']} damage"
                return None
                
            return None
            
        return ability

    def _create_default_cards(self):
        default_cards = [
            {
                "id": "knight",
                "name": "Knight",
                "rarity": "Common",
                "type": "Troop",
                "attack": 100,
                "defense": 100,
                "cost": 3,
                "description": "A brave knight ready for battle",
                "special_ability": {
                    "type": "buff",
                    "name": "Battle Cry",
                    "duration": 2,
                    "value": 20
                }
            },
            {
                "id": "wizard",
                "name": "Wizard",
                "rarity": "Rare",
                "type": "Troop",
                "attack": 150,
                "defense": 50,
                "cost": 4,
                "description": "A powerful wizard with magical abilities",
                "special_ability": {
                    "type": "damage",
                    "value": 200
                }
            },
            {
                "id": "dragon",
                "name": "Dragon",
                "rarity": "Epic",
                "type": "Troop",
                "attack": 200,
                "defense": 150,
                "cost": 5,
                "description": "A fearsome dragon that breathes fire",
                "special_ability": {
                    "type": "debuff",
                    "name": "Burning",
                    "duration": 3,
                    "value": 30
                }
            },
            {
                "id": "king",
                "name": "King",
                "rarity": "Legendary",
                "type": "Troop",
                "attack": 300,
                "defense": 200,
                "cost": 6,
                "description": "The mighty king of the realm",
                "special_ability": {
                    "type": "heal",
                    "value": 100
                }
            },
            {
                "id": "healer",
                "name": "Healer",
                "rarity": "Rare",
                "type": "Troop",
                "attack": 50,
                "defense": 100,
                "cost": 3,
                "description": "A skilled healer who can restore health",
                "special_ability": {
                    "type": "heal",
                    "value": 150
                }
            },
            {
                "id": "archer",
                "name": "Archer",
                "rarity": "Common",
                "type": "Troop",
                "attack": 120,
                "defense": 60,
                "cost": 3,
                "description": "A precise archer with deadly aim",
                "special_ability": {
                    "type": "damage",
                    "value": 100
                }
            }
        ]
        
        with open("data/cards.json", "w") as f:
            json.dump(default_cards, f, indent=4)
            
        self.load_cards()

    def get_random_card(self, rarity=None):
        if rarity:
            available_cards = [card for card in self.cards.values() if card.rarity == rarity]
        else:
            available_cards = list(self.cards.values())
            
        if not available_cards:
            return None
            
        return random.choice(available_cards)

    def get_card_by_id(self, card_id):
        return self.cards.get(card_id)

    def get_cards_by_rarity(self, rarity):
        return [card for card in self.cards.values() if card.rarity == rarity]

    def get_cards_by_type(self, card_type):
        return [card for card in self.cards.values() if card.type == card_type]
