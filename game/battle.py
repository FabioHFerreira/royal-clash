# Criar o arquivo battle.py
cat > game/battle.py << 'EOL'
import random
from datetime import datetime
import json

class Battle:
    def __init__(self, player1, player2):
        self.player1 = player1
        self.player2 = player2
        self.turn = 1
        self.max_turns = 5
        self.player1_mana = 5
        self.player2_mana = 5
        self.player1_health = 1000
        self.player2_health = 1000
        self.log = []
        self.winner = None

    def start(self):
        self.log.append(f"Battle started between {self.player1.username} and {self.player2.username}")
        return self.play_turn()

    def play_turn(self):
        if self.turn > self.max_turns:
            return self.end_battle()

        # Increase mana each turn
        self.player1_mana = min(10, self.player1_mana + 1)
        self.player2_mana = min(10, self.player2_mana + 1)

        # Players play cards
        p1_card = self._play_random_card(self.player1, self.player1_mana)
        p2_card = self._play_random_card(self.player2, self.player2_mana)

        # Calculate damage
        if p1_card:
            damage = p1_card.attack
            self.player2_health -= damage
            self.log.append(f"{self.player1.username} played {p1_card.name} and dealt {damage} damage")
            self.player1_mana -= p1_card.cost

        if p2_card:
            damage = p2_card.attack
            self.player1_health -= damage
            self.log.append(f"{self.player2.username} played {p2_card.name} and dealt {damage} damage")
            self.player2_mana -= p2_card.cost

        self.turn += 1

        # Check if battle should end
        if self.player1_health <= 0 or self.player2_health <= 0:
            return self.end_battle()

        return self.play_turn()

    def _play_random_card(self, player, available_mana):
        playable_cards = [card for card in player.deck if card.cost <= available_mana]
        if not playable_cards:
            return None
        return random.choice(playable_cards)

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
            "log": self.log
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
            "turns": result["turns"]
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
            "win_rate": (wins / len(battles) * 100) if battles else 0
        }
