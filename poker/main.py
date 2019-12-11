from poker import PokerGame
from deck import Deck, Hand


def test_hand_evaluation():
    NUM_PLAYERS = 8

    hands = []
    deck = Deck()
    community_cards = deck.get_random_cards(5)

    print("{:#^100}".format(" POKER HANDS "))
    print(f"\n\t {community_cards} \n\n")
    for i in range(NUM_PLAYERS):
        player_cards = deck.get_random_cards(2)
        player_best_hand = Hand(community_cards + player_cards)

        print(f"\t PLAYER {i+1} :  {player_cards}")
        print(f"\t\t BEST HAND = {player_best_hand}")
        hands.append((i+1, player_best_hand))

    winner = sorted(hands, key=lambda h: h[1])[-1]
    print(f"\n\tWINNER is Player {winner[0]} with {winner[1]}\n\n")

    for player, hand in sorted(hands, key=lambda h:h[1])[::-1]:
        print(f"Player {player} : {hand}")


def test_poker_game():
    pg = PokerGame(buyin=250, smallblind=50)
    pg.run()


def main():
    # test_hand_probabilities()
    test_hand_evaluation()
    # test_poker_game()


if __name__ == "__main__":
    main()
