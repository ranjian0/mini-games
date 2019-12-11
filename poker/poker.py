import sys
import itertools as it

from player import Bot
from deck import Deck, Hand


class PokerGame:
    def __init__(self, players=8, buyin=200, smallblind=20):
        # -- chip variables
        self.pot = 0
        self.buyin = buyin
        self.smallblind = smallblind

        # -- player variables
        self.players = []
        self.num_players = players

        # -- card variables
        self.deck = Deck()
        self.community_cards = []

        # -- game state
        self.speed = 1

    def initialize(self):
        self._add_players()

    def update(self):
        _round = 0
        while len(self.players) > 1:
            # PRE FLOP
            self._clear_bets()
            self._set_blinds(_round)
            self._deal_player_cards()
            self.get_actions(self.smallblind*2)
            self.check_winner("PRE-FLOP")

            # FLOP
            self._deal_community_cards("FLOP")
            self._clear_bets()
            self.get_actions(0)
            self.check_winner("FLOP")

            # TURN
            self._deal_community_cards("TURN")
            self._clear_bets()
            self.get_actions(0)
            self.check_winner("TURN")

            # RIVER
            self._deal_community_cards("RIVER")
            self._clear_bets()
            self.get_actions(0)
            self.check_winner("RIVER")

            # XXX ------- XXX
            self.print_game()

            self._finish_round(_round+1)
            _round += 1

    def finalize(self):
        print(self.players[-1])

    def _add_players(self):
        for _ in range(self.num_players):
            self.players.append(Bot(self.buyin))

    def _clear_bets(self):
        for p in self.players:
            p.bet = 0

    def _clear_blinds(self):
        for p in self.players:
            p.is_dealer = False
            p.is_smallblind = False
            p.is_bigblind = False

    def _get_dealer_and_blinds(self, _round):
        players = it.cycle(self.players)
        dealer = next(players)
        while _round > 0:
            dealer = next(players)
            _round -= 1
        return dealer, next(players), next(players)

    def _set_blinds(self, _round=0):
        self._clear_blinds()
        if len(self.players) > 2:
            dealer, sblind, bblind = self._get_dealer_and_blinds(_round)
            dealer.is_dealer = True
        else:
            sblind, bblind, _ = self._get_dealer_and_blinds(_round)

        # -- set small blind
        sblind.is_smallblind = True
        if sblind.chips >= self.smallblind:
            sblind.chips -= self.smallblind
            sblind.bet = self.smallblind
        else:
            sblind.bet = sblind.chips
            sblind.chips = 0
            sblind.is_allin = True

        # -- set big blind
        bblind.is_bigblind = True
        if bblind.chips >= self.smallblind*2:
            bblind.bet = self.smallblind*2
            bblind.chips -= self.smallblind*2
        else:
            bblind.bet = bblind.chips
            bblind.chips = 0
            bblind.is_allin = True

    def _deal_player_cards(self):
        for p in self.players:
            p.cards.clear()
            p.cards = self.deck.get_random_cards(count=2)

    def _deal_community_cards(self, event):
        if event == "FLOP":
            self.community_cards.clear()
            self.community_cards = self.deck.get_random_cards(count=3)

        elif event == "TURN":
            self.community_cards += self.deck.get_random_cards(count=1)

        elif event == "RIVER":
            self.community_cards += self.deck.get_random_cards(count=1)

    def _finish_round(self, _round):
        self._remove_losers(_round)
        self._reset_inactive_players()
        self._update_blind_amounts(_round)

        # -- clean game state
        self.pot = 0
        self.deck = Deck()
        self.community_cards.clear()

    def _remove_losers(self, _round):
        self.players = [p for p in self.players if p.chips > 0]

    def _update_blind_amounts(self, _round):
        if _round % 3 == 0:
            self.smallblind *= 2

    def _reset_inactive_players(self):
        for p in self.players:
            if not p.active:
                p.active = True

    def _players_with_dealer_last(self):
        """ Order players so that dealer is last """
        bb_idx = [
            idx for idx, p in enumerate(self.players, 1) if p.is_bigblind
        ][-1]
        return list(
            it.islice(it.cycle(self.players), bb_idx, bb_idx+len(self.players))
        )

    def get_actions(self, stake):
        # -- reset actions from previous rounds
        for p in self.players:
            p.action = ""

        action_rounds = 1
        while action_rounds > 0:

            for player in self._players_with_dealer_last():
                if not player.active or player.is_allin:
                    # -- skip players that have folded / are all in
                    continue

                action = player.get_action(stake)
                action_amount = action()

                if action_amount == 0:
                    if not player.active:
                        # -- player folded
                        pass
                    elif player.bet == stake:
                        # -- player checked
                        self.pot += stake

                elif action_amount == stake:
                    # -- this player called
                    self.pot += action_amount

                elif action_amount > stake:
                    self.pot += action_amount
                    stake += action_amount
                    if player.chips == 0:
                        # -- this player is all in
                        pass
                    else:
                        # -- this player raised
                        pass

                    # -- add one more round so other players decide to call/raise/fold
                    action_rounds += 1

                elif action_amount < stake:
                    # -- this player is all in but with small amount
                    self.pot += action_amount
                    stake += action_amount

                # XXX ------- XXX
                # self.print_game()
                # # time.sleep(self.speed)
                # cont = input("Next Action?")
                # if cont == "n":
                #     sys.exit()
                # self.clear_game()

            action_rounds -= 1
        return stake

    def check_winner(self, _round="RIVER"):
        if _round == "PRE-FLOP":
            # check for winner if
            # a. everyone else folded
            pass

        elif _round in ("FLOP", "TURN"):
            # check for winner if:
            # a. everyone is all in
            # b. only two players active
            # c. everyone floded, only one player remaining
            pass
        else:
            # check for player with the best hand
            winner, hand = max(
                [(p, Hand(p.cards + self.community_cards)) for p in self.players],
                key=lambda hp: hp[1]
            )
            # winner = random.choice(self.players)
            winner.chips += self.pot
            print(f"\nWINNER : {winner}\n\n")

    def print_game(self):
        # -- game
        HEADER = f"""
            Texas Holdem Poker
            ``````````````````
            BUY IN     : {self.buyin}
            SMALLBLIND : {self.smallblind}
        """

        POT = f"""
            POT             : {self.pot}

            COMMUNITY CARDS :{self.community_cards}
        """

        PLAYER_TEPMLATE = """
            {id}. {player} ({kind:2}): Cards = {cards} | Chips = {chips} | {hand}
                        ACTION --> {action}
                        BET    --> {bet}
        """
        PLAYERS = ""
        for idx, p in enumerate(self.players, start=1):
            kind = ""
            if p.is_dealer:
                kind = "D"
            elif p.is_smallblind:
                kind = "SB"
            elif p.is_bigblind:
                kind = "BB"

            PLAYERS += PLAYER_TEPMLATE.format(
                id=idx, cards=p.cards, chips=p.chips, action=p.action, player=p,
                kind=kind, bet=p.bet, hand=Hand(p.cards + self.community_cards))

        GAME = HEADER + POT + PLAYERS
        sys.stdout.write(GAME)
        sys.stdout.flush()

    def clear_game(self):
        # -- clear
        sys.stdout.write(" \n" * 35 + "\r")
        sys.stdout.flush()

    def run(self):
        self.initialize()
        self.update()
        self.finalize()
