import time
import random
import operator as op
import itertools as it

from enum import Enum
from pprint import pformat
from collections import Counter

KINDS = '2 3 4 5 6 7 8 9 Ten Jack Queen King Ace'.split()
SUITS = 'Diamonds Clubs Hearts Spades'.split()


class Rank(Enum):
    HIGHCARD = 1
    PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


class Card:

    def __init__(self, kind, suit):
        self.kind = kind
        self.suit = suit

    def __repr__(self):
        return f"<{self.kind[0]}{self.suit[0]}>"

    def value(self):
        return (KINDS.index(self.kind) + 2) + (SUITS.index(self.suit) + 1)

    @property
    def k(self):
        return KINDS.index(self.kind) + 2

    @property
    def s(self):
        return SUITS.index(self.suit) + 1


GET_KIND = op.attrgetter("k")
GET_SUIT = op.attrgetter("s")


class Hand:
    """ Hand accepts at least 5 cards, and evaluates rank"""

    def __init__(self, cards):
        self.cards = cards

        self.rank = Rank.HIGHCARD
        self.value = []
        self.value_cards = []
        if len(cards) >= 5:
            self._evaluate()

    def __repr__(self):
        if len(self.cards) >= 5:
            return f"{self.rank} : {self.value_cards[:5]}"
        return f"Hand({self.cards})"

    def __lt__(self, other):
        if self.rank.value < other.rank.value:
            return True
        elif self.rank.value == other.rank.value:
            return self.value[:5] < other.value[:5]
        return False

    def __eq__(self, other):
        return self.rank.value == other.rank.value and self.value[:5] == other.value[:5]

    def update(self, cards):
        self.cards = cards
        self._evaluate()

    def _value_cards(self, suit=None):
        self.value_cards.clear()
        for v in self.value:
            if not suit:
                self.value_cards.extend([c for c in self.cards if c.k == v])
            else:
                self.value_cards.extend(
                    [c for c in self.cards if c.k == v and c.s == suit])

    def _evaluate(self):
        """
        highcard            - card of the highest kind
        pair                - a pair of cards of the same kind
        two pair            - two pairs of cards of the same kind
        three_of_a_kind     - three cards of the same kind
        straight            - five consecutive cards of mixed suits
        flush               - five cards of the same suit, non-consecutive
        full_house          - three of a kind plus a pair
        four_of_a_kind      - four cards of the same kind
        straight_flush      - straight in the same suit ending lower than ace
        royal_flush         - straight flush ending in an ace
        """

        self._check_highcard()
        self._check_pair()
        self._check_two_pair()
        self._check_three_of_a_kind()
        self._check_straight()
        self._check_flush()
        self._check_full_house()
        self._check_four_of_a_kind()
        self._check_straight_flush()
        self._check_royal_flush()

    def _check_highcard(self):
        self.rank = Rank.HIGHCARD
        self.value = sorted([c.k for c in self.cards])[::-1]
        self._value_cards()

    def _check_pair(self):
        card_kinds = sorted([c.k for c in self.cards])
        counter_kinds = Counter(card_kinds)
        kinds = list(counter_kinds.values())

        if kinds.count(2) == 1:
            self.rank = Rank.PAIR
            self.value = sorted(
                counter_kinds,
                key=lambda k : (counter_kinds[k], k)
            )[::-1]
            self._value_cards()
            return True
        return False

    def _check_two_pair(self):
        card_kinds = sorted([c.k for c in self.cards])
        counter_kinds = Counter(card_kinds)
        kinds = list(counter_kinds.values())

        if kinds.count(2) == 2:
            self.rank = Rank.TWO_PAIR
            self.value = sorted(
                counter_kinds,
                key=lambda k : (counter_kinds[k], k)
            )[::-1]
            self._value_cards()

    def _check_three_of_a_kind(self):
        card_kinds = sorted([c.k for c in self.cards])
        counter_kinds = Counter(card_kinds)
        kinds = list(counter_kinds.values())

        if kinds.count(3) == 1:
            self.rank = Rank.THREE_OF_A_KIND
            self.value = sorted(
                counter_kinds,
                key=lambda k : (counter_kinds[k], k)
            )[::-1]
            self._value_cards()
            return True
        return False

    def _check_straight(self):
        card_kinds = sorted({c.k for c in self.cards})[::-1]
        if len(card_kinds) < 5:
            return False

        def has_straight(kinds):
            """ check groups of 5 cards for straight """
            for i in range(len(kinds) - 4):
                current = kinds[i:i+5]
                mn, mx = min(current), max(current)
                if current == range(mx+1, mn, -1):
                    self.rank = Rank.STRAIGHT
                    self.value = current
                    self._value_cards()
                    return True

        normal_straight = has_straight(card_kinds)
        if normal_straight:
            return True

        # -- check low ace straight
        if 14 in card_kinds:
            card_kinds.remove(14)
            card_kinds.append(1)
            if has_straight(sorted(card_kinds)[::-1]):
                return True
        return False

    def _check_flush(self):
        card_suits = sorted([c.s for c in self.cards])
        counter_suits = Counter(card_suits)
        suit, count = counter_suits.most_common(1)[-1]

        if count >= 5:
            self.rank = Rank.FLUSH
            self.value = sorted([c.k for c in self.cards if c.s == suit])[::-1]
            self.value += sorted([c.k for c in self.cards if c.s != suit])[::-1]
            self._value_cards(suit)
            return True
        return False

    def _check_full_house(self):
        pair = self._check_pair()
        pair_value = self.value[:2] if pair else []
        three_of_a_kind = self._check_three_of_a_kind()
        toak_value = self.value[:3] if three_of_a_kind else []

        if pair and three_of_a_kind:
            self.rank = Rank.FULL_HOUSE
            val = toak_value + pair_value
            self.value = val + [v for v in self.value if v not in val]
            self._value_cards()

    def _check_four_of_a_kind(self):
        card_kinds = sorted([c.k for c in self.cards])
        counter_kinds = Counter(card_kinds)
        kinds = list(counter_kinds.values())

        if kinds.count(4) == 1:
            self.rank = Rank.FOUR_OF_A_KIND
            self.value = sorted(
                counter_kinds,
                key=lambda k : (counter_kinds[k], k)
            )[::-1]
            self._value_cards()

    def _check_straight_flush(self):
        flush = self._check_flush()
        flush_value = self.value[:5] if flush else []
        straight = self._check_straight()
        straight_value = self.value[:5] if straight else []

        if straight and flush:
            if flush_value == straight_value:
                self.rank = Rank.STRAIGHT_FLUSH
                self._value_cards()

    def _check_royal_flush(self):
        flush = self._check_flush()
        flush_value = self.value[:5] if flush else []
        straight = self._check_straight()
        straight_value = self.value[:5] if straight else []

        if straight and flush:
            if flush_value == straight_value and max(straight_value) == 14:
                self.rank = Rank.ROYAL_FLUSH
                self._value_cards()


class Deck:

    def __init__(self):
        self.cards = []
        self.reset()

    def __repr__(self):
        return f"{pformat(self.cards)}"

    def count(self):
        return len(self.cards)

    def reset(self):
        types = it.product(KINDS, SUITS)
        self.cards = [Card(kind, suit) for kind, suit in types]

    def shuffle(self, n_times=3):
        random.seed(time.time())
        for _ in range(n_times):
            random.shuffle(self.cards)

    def get_random_cards(self, count=1):
        result = []
        for _ in range(count):
            self.shuffle()
            card = random.choice(self.cards)
            self.cards.remove(card)
            result.append(card)
        return result
