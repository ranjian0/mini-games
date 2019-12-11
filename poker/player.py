
class PokerPlayer:
    INDEX = 1

    def __init__(self, chips, *args, **kwargs):
        self.chips = chips
        self.cards = []

        self.bet = 0
        self.stakes = 0
        self.action = ""
        self.active = True
        self.is_allin = False
        self.is_dealer = False
        self.is_bigblind = False
        self.is_smallblind = False

        # store player id for unique identification
        self.id = PokerPlayer.INDEX
        PokerPlayer.INDEX += 1

    def __repr__(self):
        return f"Player<id={self.id}>"

    def check(self):
        """ Stakes equal our bet """
        self.action = "CHECK"
        return 0

    def call(self):
        if self.stakes <= self.chips:
            self.action = "CALL"
            self.chips -= (self.stakes - self.bet)
            self.bet = self.stakes
            return self.bet
        else:
            return self.all_in()

    def raise_(self, raise_value=0):
        self.chips -= self.stakes
        self.chips -= raise_value
        self.action = "RAISE"
        self.bet += self.stakes + raise_value
        return raise_value + self.stakes

    def fold(self):
        self.action = "FOLD"
        self.active = False
        return 0

    def all_in(self):
        self.bet = self.chips
        self.chips = 0
        self.is_allin = True
        self.action = "ALL IN"
        return self.chips

    def get_blind(self, smallblind_value):
        if self.is_smallblind:
            self.chips -= smallblind_value
        elif self.is_bigblind:
            self.chips -= smallblind_value * 2

    def action_options(self, stakes):
        pass

    def get_action(self, stakes):
        raise NotImplementedError()


class Human(PokerPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_action(self, stakes):
        self.stakes = stakes
        return self.fold


class Bot(PokerPlayer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_action(self, stakes):
        self.stakes = stakes


        if self.bet == stakes:
            return self.check
        elif self.bet < stakes:
            return self.call
        print(stakes, self.bet)
