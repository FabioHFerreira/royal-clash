# Criar o arquivo cards.py
cat > game/cards.py << 'EOL'
import json
import random
from enum import Enum

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

    def upgrade(self):
        if self.experience >= self.level * 100:
            self.level += 1
            self.attack += self.level * 2
            self.defense += self.level * 2
            self.experience = 0
            return True
        return False

    def use_special_ability(self, target=None):
        if self.special_ability:
            return self.special_ability(self, target)
        return None

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
                    self.cards[card.id] = card
        except FileNotFoundError:
            self._create_default_cards()

    def _create_special_ability(self, ability_data):
        if not ability_data:
            return None
            
        def ability(card, target):
            # Implement special abilities here
            pass
            
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
                "description": "A brave knight ready for battle"
            },
            {
                "id": "wizard",
                "name": "Wizard",
                "rarity": "Rare",
                "type": "Troop",
                "attack": 150,
                "defense": 50,
                "cost": 4,
                "description": "A powerful wizard with magical abilities"
            },
            {
                "id": "dragon",
                "name": "Dragon",
                "rarity": "Epic",
                "type": "Troop",
                "attack": 200,
                "defense": 150,
                "cost": 5,
                "description": "A fearsome dragon that breathes fire"
            },
            {
                "id": "king",
                "name": "King",
                "rarity": "Legendary",
                "type": "Troop",
                "attack": 300,
                "defense": 200,
                "cost": 6,
                "description": "The mighty king of the realm"
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
