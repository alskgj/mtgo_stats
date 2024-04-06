"""

    model.py
    ========




"""
from datetime import datetime
from enum import Enum

from pydantic import BaseModel
from typing import List, Dict, NewType

from abc import ABC, abstractmethod


class Color(str, Enum):
    white = 'white'
    blue = 'blue'
    black = 'black'
    red = 'red'
    green = 'green'
    colorless = 'colorless'
    unknown = 'unknown'


class Rarity(str, Enum):
    common = 'common'
    uncommon = 'uncommon'
    rare = 'rare'
    mythic = 'mythic'
    promo = 'promo'
    basic_land = 'basic_land'
    bonus = 'bonus'


class CardType(str, Enum):
    creature = 'creature'
    sorcery = 'sorcery'
    instant = 'instant'
    land = 'land'
    enchantment = 'enchantment'
    planeswalker = 'planeswalker'
    artifact = 'artifact'
    unknown = 'unknown'


class Card(BaseModel):
    name: str
    cost: int
    colors: List[Color]
    type: CardType
    quantity: int

    def __str__(self):
        return f'{self.quantity} {self.name}'


class Deck(BaseModel):
    main: List[Card] = []
    side: List[Card] = []

    def contains_at_least_three(self, card_name):
        return any([card.name == card_name and card.quantity >= 3 for card in self.main])

    def contains_at_least(self, x: int, card_name: str):
        return any([card.name == card_name and card.quantity >= x for card in self.main + self.side])

    @property
    def maindeck_creatures(self) -> int:
        return sum(card.quantity for card in self.main if card.type == CardType.creature)

    def __str__(self):
        creatures = [card for card in self.main if card.type == CardType.creature]
        spells = [card for card in self.main if card.type in (CardType.instant, CardType.sorcery)]
        lands = [card for card in self.main if card.type == CardType.land]
        others = [card for card in self.main if card not in creatures+spells+lands]

        result = ""
        grouping = [('Creatures', creatures), ('Spells', spells), ('Lands', lands), ('Other', others)]
        for title, cat in grouping:
            result += f'{title}\n{len(title)*"="}\n'
            for card in cat:
                result += f'{card}\n'
            result += '\n'
        return result


DeckName = NewType('DeckName', str)


class Result(BaseModel):
    deck: Deck
    deck_name: DeckName
    wins: int
    losses: int
    date: datetime


class TournamentParticipant(BaseModel):
    name: str
    rank: int
    wins: int
    losses: int
    deck: Deck


class WinRate(BaseModel):
    mean: float
    lower_bound: float
    upper_bound: float


class DeckStat(BaseModel):
    name: DeckName
    win_rate: WinRate
    play_rate: float
    total_matches: int


class Tournament(BaseModel):
    id: int
    description: str
    format: str
    players: List[TournamentParticipant]
    start_time: datetime
    link: str

    def deckname_to_players(self, classifier: 'Classifier') -> Dict[DeckName, List[TournamentParticipant]]:
        decks: Dict[DeckName, List[TournamentParticipant]] = {}
        for player in self.players:
            deck_name = classifier.classify(player.deck)
            if deck_name not in decks:
                decks[deck_name] = []
            decks[deck_name].append(player)
        return decks

    def play_rates(self, classifier: 'Classifier') -> Dict[str, float]:
        decks = self.deckname_to_players(classifier)
        result = {}
        for deck_name in decks:
            total_decks = len(self.players)
            result[deck_name] = round(len(decks[deck_name]) / total_decks, 2)
        return result


class AbstractClassificationRule(ABC):

    @abstractmethod
    def satisfied_by(self, deck: Deck) -> bool:
        ...

    @property
    @abstractmethod
    def deck_name(self) -> DeckName:
        ...


class Classifier:
    def __init__(self, rules: List[AbstractClassificationRule]):
        self.rules = rules

    def classify(self, deck: Deck) -> DeckName:
        for rule in self.rules:
            if rule.satisfied_by(deck):
                return rule.deck_name
        return DeckName('Unclassified Deck')
