from game.player import Player

def test_initial_cards():
    print("Testando carregamento de cards iniciais...")
    player = Player("test_player")
    print(f"\nCards do jogador: {len(player.cards)}")
    print(f"Cards no deck: {len(player.deck)}")
    print("\nDetalhes dos cards:")
    for card in player.cards:
        print(f"- {card.name} (ID: {card.id}, Raridade: {card.rarity}, Tipo: {card.type})")

if __name__ == "__main__":
    test_initial_cards() 