import random
from datetime import datetime
import json
import time

class Battle:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.turn = 1
        self.max_turns = 10  # Increased max turns for more strategic gameplay
        self.player1_mana = 5
        self.player2_mana = 5
        self.player1_health = 1000
        self.player2_health = 1000
        self.player1_field = []  # Cards on the field
        self.player2_field = []  # Cards on the field
        self.log = []
        self.winner = None
        self.animation_queue = []  # Queue for battle animations

    def start(self):
        self.log.append(f"Battle started between {self.player1.username} and {self.player2.username}")
        return self.play_turn()

    def play_turn(self):
        if self.turn > self.max_turns:
            return self.end_battle()

        # Increase mana each turn
        self.player1_mana = min(10, self.player1_mana + 1)
        self.player2_mana = min(10, self.player2_mana + 1)

        # Get active cards
        player_card = self.player1_field[0] if self.player1_field else None
        enemy_card = self.player2_field[0] if self.player2_field else None
        
        if not player_card or not enemy_card:
            return False
            
        # Process effects
        player_card.process_effects()
        enemy_card.process_effects()
        
        # Player card attacks enemy card
        damage = player_card.attack
        enemy_card.defense -= damage
        self.log.append(f"{player_card.name} deals {damage} damage to {enemy_card.name}")
        
        # Use special ability if available
        if player_card.special_ability:
            effect = player_card.use_special_ability(enemy_card)
            if effect:
                self.log.append(f"{player_card.name} {effect}")
                self.animation_queue.append({
                    "type": "special_ability",
                    "card": player_card,
                    "effect": effect
                })
        
        # Enemy card counter-attacks if still alive
        if enemy_card.defense > 0:
            damage = enemy_card.attack
            player_card.defense -= damage
            self.log.append(f"{enemy_card.name} deals {damage} damage to {player_card.name}")
            
            # Enemy uses special ability if available
            if enemy_card.special_ability:
                effect = enemy_card.use_special_ability(player_card)
                if effect:
                    self.log.append(f"{enemy_card.name} {effect}")
                    self.animation_queue.append({
                        "type": "special_ability",
                        "card": enemy_card,
                        "effect": effect
                    })
        
        # Remove defeated cards
        if player_card.defense <= 0:
            self.log.append(f"{player_card.name} was defeated!")
            self.player1_field.pop(0)
            
        if enemy_card.defense <= 0:
            self.log.append(f"{enemy_card.name} was defeated!")
            self.player2_field.pop(0)
            
        # Reduce cooldowns
        for card in self.player1_field + self.player2_field:
            if card.cooldown > 0:
                card.cooldown -= 1
                
        self.turn += 1

        # Check if battle should end
        if self.player1_health <= 0 or self.player2_health <= 0:
            return self.end_battle()

        return self.play_turn()

    def _play_strategic_card(self, player, available_mana, field):
        # Get playable cards
        playable_cards = [card for card in player.deck if card.cost <= available_mana]
        
        if not playable_cards:
            return None

        # Basic AI strategy
        if len(field) == 0:
            # If field is empty, prefer high attack cards
            return max(playable_cards, key=lambda x: x.attack)
        elif len(field) >= 3:
            # If field is crowded, prefer high defense cards
            return max(playable_cards, key=lambda x: x.defense)
        else:
            # Otherwise, balance attack and defense
            return max(playable_cards, key=lambda x: (x.attack + x.defense) / 2)

    def _process_card_effects(self, card, owner, opponent):
        # Process special abilities
        if card.special_ability:
            effect = card.use_special_ability(opponent)
            if effect:
                self.log.append(f"{card.name}'s special ability: {effect}")
                self.animation_queue.append({
                    "type": "special_ability",
                    "card": card,
                    "effect": effect
                })

    def _resolve_battles(self):
        # Pair up cards for battle
        while self.player1_field and self.player2_field:
            p1_card = self.player1_field[0]
            p2_card = self.player2_field[0]

            # Calculate damage
            p1_damage = p1_card.attack
            p2_damage = p2_card.attack

            # Apply damage
            p2_card.defense -= p1_damage
            p1_card.defense -= p2_damage

            # Log the battle
            self.log.append(f"{p1_card.name} attacked {p2_card.name} for {p1_damage} damage")
            self.log.append(f"{p2_card.name} attacked {p1_card.name} for {p2_damage} damage")

            # Add to animation queue
            self.animation_queue.append({
                "type": "battle",
                "attacker": p1_card,
                "defender": p2_card,
                "damage": p1_damage
            })
            self.animation_queue.append({
                "type": "battle",
                "attacker": p2_card,
                "defender": p1_card,
                "damage": p2_damage
            })

            # Remove destroyed cards
            if p1_card.defense <= 0:
                self.player1_field.pop(0)
                self.log.append(f"{p1_card.name} was destroyed")
            if p2_card.defense <= 0:
                self.player2_field.pop(0)
                self.log.append(f"{p2_card.name} was destroyed")

        # Remaining cards attack opponent directly
        for card in self.player1_field:
            damage = card.attack
            self.player2_health -= damage
            self.log.append(f"{card.name} attacked opponent directly for {damage} damage")
            self.animation_queue.append({
                "type": "direct_attack",
                "card": card,
                "damage": damage
            })

        for card in self.player2_field:
            damage = card.attack
            self.player1_health -= damage
            self.log.append(f"{card.name} attacked opponent directly for {damage} damage")
            self.animation_queue.append({
                "type": "direct_attack",
                "card": card,
                "damage": damage
            })

    def _cleanup_field(self):
        # Remove any cards with 0 or less defense
        self.player1_field = [card for card in self.player1_field if card.defense > 0]
        self.player2_field = [card for card in self.player2_field if card.defense > 0]

    def end_battle(self):
        if self.player1_health > self.player2_health:
            self.winner = self.player1
            self.player1.earn_trophies(30)
            self.player1.earn_gold(100)
            self.player2.earn_trophies(10)
            self.player2.earn_gold(50)
        else:
            self.winner = self.player2
            self.player2.earn_trophies(30)
            self.player2.earn_gold(100)
            self.player1.earn_trophies(10)
            self.player1.earn_gold(50)

        self.log.append(f"Battle ended! Winner: {self.winner.username}")
        return self.get_battle_result()

    def get_battle_result(self):
        return {
            "winner": self.winner.username if self.winner else None,
            "player1_health": self.player1_health,
            "player2_health": self.player2_health,
            "turns": self.turn,
            "log": self.log,
            "animations": self.animation_queue
        }

class BattleManager:
    def __init__(self):
        self.battles = {}
        self.load_battle_history()

    def load_battle_history(self):
        try:
            with open("data/battle_history.json", "r") as f:
                self.battle_history = json.load(f)
        except FileNotFoundError:
            self.battle_history = []

    def save_battle_history(self):
        with open("data/battle_history.json", "w") as f:
            json.dump(self.battle_history, f, indent=4)

    def start_battle(self, player1, player2):
        if not player1.deck or not player2.deck:
            return None, "Players need to have a deck to battle"

        battle = Battle(player1, player2)
        result = battle.start()
        
        # Save battle to history
        battle_record = {
            "timestamp": datetime.now().isoformat(),
            "player1": player1.username,
            "player2": player2.username,
            "winner": result["winner"],
            "turns": result["turns"],
            "player1_health": result["player1_health"],
            "player2_health": result["player2_health"]
        }
        self.battle_history.append(battle_record)
        self.save_battle_history()

        return result, "Battle completed"

    def get_player_battle_history(self, username):
        return [battle for battle in self.battle_history 
                if battle["player1"] == username or battle["player2"] == username]

    def get_player_stats(self, username):
        battles = self.get_player_battle_history(username)
        wins = sum(1 for battle in battles if battle["winner"] == username)
        losses = len(battles) - wins
        
        return {
            "total_battles": len(battles),
            "wins": wins,
            "losses": losses,
            "win_rate": (wins / len(battles) * 100) if battles else 0,
            "average_turns": sum(battle["turns"] for battle in battles) / len(battles) if battles else 0,
            "total_damage_dealt": sum(
                battle["player2_health"] if battle["player1"] == username else battle["player1_health"]
                for battle in battles
            ) if battles else 0
        }
