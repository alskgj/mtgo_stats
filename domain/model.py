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


class Rarity(str, Enum):
    common = 'common'
    uncommon = 'uncommon'
    rare = 'rare'
    mythic = 'mythic'


class CardType(str, Enum):
    creature = 'creature'
    sorcery = 'sorcery'
    instant = 'instant'
    land = 'land'


class Card(BaseModel):
    name: str
    cost: int
    id: int
    rarity: Rarity
    colors: List[Color]
    type: CardType
    quantity: int


class Deck(BaseModel):
    main: List[Card] = []
    side: List[Card] = []

    def contains_at_least_three(self, card_name):
        return any([card.name == card_name and card.quantity >= 3 for card in self.main+self.side])


class TournamentParticipant(BaseModel):
    name: str
    rank: int
    wins: int
    losses: int
    deck: Deck


DeckName = NewType('DeckName', str)


class Tournament(BaseModel):
    id: int
    description: str
    format: str
    players: List[TournamentParticipant]
    start_time: datetime

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
