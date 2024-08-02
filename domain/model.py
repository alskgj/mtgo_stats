import typing
from collections import defaultdict
from datetime import datetime
from enum import Enum

import pydantic
from pydantic import BaseModel
from typing import List, NewType, Optional

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

    @property
    def combined(self) -> List[Card]:
        """Combines main and sideboard. If a card is 2 times in the main and once
        in the sb, then combined will show it once, with quantity==3"""
        result = []
        mb_card_names = [card.name for card in self.main]
        sb_card_names = [card.name for card in self.side]

        for card in self.main:
            if card.name in sb_card_names:
                card.quantity = card.quantity + [c for c in self.side if c.name == card.name][0].quantity
            result.append(card)

        for card in self.side:
            if card.name in mb_card_names:
                continue
            result.append(card)
        return result


    def __str__(self):
        creatures = [card for card in self.main if card.type == CardType.creature]
        spells = [card for card in self.main if card.type in (CardType.instant, CardType.sorcery)]
        lands = [card for card in self.main if card.type == CardType.land]
        others = [card for card in self.main if card not in creatures + spells + lands]

        result = ""
        grouping = [('Creatures', creatures), ('Spells', spells), ('Lands', lands), ('Other', others)]
        for title, cat in grouping:
            result += f'{title}\n{len(title) * "="}\n'
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
    link: str
    hero_cards: list[str]


class TournamentParticipant(BaseModel):
    name: str
    rank: int
    wins: int
    losses: int
    deck: Deck


class ClassifiedTournamentParticipant(BaseModel):
    name: str
    rank: int
    wins: int
    losses: int
    deck: Deck
    deck_name: DeckName

    @classmethod
    def from_player(cls, player: TournamentParticipant, classifier: 'Classifier') -> 'ClassifiedTournamentParticipant':
        data = player.dict()
        data['deck_name'] = classifier.classify(player.deck)
        return cls(**data)


class WinRate(BaseModel):
    mean: float
    lower_bound: float
    upper_bound: float


class DeckStat(BaseModel):
    name: DeckName
    win_rate: WinRate
    play_rate: float
    total_matches: int
    example_link: str
    hero_cards: list[str]


class Tournament(BaseModel):
    """ A tournament containing only data from mtgo.com/decklist """
    id: int
    description: str
    format: str
    players: List[TournamentParticipant]  # this is capped to top 32
    start_time: datetime
    link: str
    player_count: int

    @classmethod
    def from_json(cls, data: dict) -> 'Tournament':
        date = data['starttime']
        if ' ' in date:
            date = date.split(' ')[0]

        return cls(
            id=data['event_id'],
            description=data['description'],
            start_time=datetime.fromisoformat(date),
            format='pioneer' if data['format'] == 'CPIONEER' else data['format'],
            players=parse_tournament_participants(data),
            link=f'https://www.mtgo.com/decklist/{data["site_name"]}',
            player_count=data['player_count']['players']
        )


class ClassifiedTournament(BaseModel):
    """ A tournament containing data from mtgo.com/decklist and interpretation (guessed deck name) """
    id: int
    description: str
    format: str
    players: List[ClassifiedTournamentParticipant]  # this is capped to top 32
    start_time: datetime
    link: str
    player_count: int

    @classmethod
    def from_tournament(cls, tournament: Tournament, classifier: 'Classifier') -> 'ClassifiedTournament':
        data = tournament.dict()
        data['players'] = [
            ClassifiedTournamentParticipant.from_player(player, classifier) for player in tournament.players
        ]
        return cls(**data)


class AbstractClassificationRule(ABC):

    @abstractmethod
    def satisfied_by(self, deck: Deck) -> bool:
        ...

    @property
    @abstractmethod
    def deck_name(self) -> DeckName:
        ...

    @abstractmethod
    def heroes(self):
        ...


class Classifier:
    def __init__(self, rules: List[AbstractClassificationRule]):
        self.rules = rules

    def classify(self, deck: Deck) -> DeckName:
        for rule in self.rules:
            if rule.satisfied_by(deck):
                return rule.deck_name
        return DeckName('Unclassified Decks')

    def find_hero(self, deck: Deck) -> list[str]:
        for rule in self.rules:
            if rule.satisfied_by(deck):
                return rule.heroes()
        return []


class CardAnalysis(BaseModel):
    name: str
    total_wins: int
    total_losses: int
    example_link: str


class DeckAnalysis(BaseModel):
    name: DeckName
    total_wins: int
    total_losses: int
    cards: typing.Dict[typing.Tuple[int, str], CardAnalysis]

    def update_cards(self, result: Result):
        combined = result.deck.combined
        for card in combined:
            key = (card.quantity, card.name)
            if key not in self.cards:
                self.cards[key] = CardAnalysis(name=card.name, total_wins=0, total_losses=0, example_link=result.link)

            self.cards[key].total_wins += result.wins
            self.cards[key].total_losses += result.losses
            self.cards[key].example_link = result.link


def parse_tournament_participants(data: dict) -> List[TournamentParticipant]:
    """
    need
    name, rank, wins, losses, deck
    """
    intermediate = defaultdict(dict)

    # collect necessary data
    for entry in data['winloss']:
        intermediate[entry['loginid']]['wins'] = entry['wins']
        intermediate[entry['loginid']]['losses'] = entry['losses']
    for entry in data['standings']:
        intermediate[entry['loginid']]['rank'] = entry['rank']
    for entry in data['decklists']:
        intermediate[entry['loginid']]['name'] = entry['player']
        main_deck = merge_cards([parse_card(card_data) for card_data in entry['main_deck']])
        side_deck = merge_cards([parse_card(card_data) for card_data in entry['sideboard_deck']])
        intermediate[entry['loginid']]['deck'] = Deck(main=main_deck, side=side_deck)

    # build the tournament participant
    result = []
    for loginid, entry in intermediate.items():
        try:
            result.append(TournamentParticipant(
                name=entry['name'],
                rank=entry['rank'],
                wins=entry['wins'],
                losses=entry['losses'],
                deck=entry['deck']
            ))
        except KeyError:
            continue
    return result


def parse_card(data: dict) -> Card:
    attributes = data['card_attributes']
    card_types = {
        'iscrea': CardType.creature,
        'sorcry': CardType.sorcery,
        'instnt': CardType.instant,
        'land': CardType.land,
        'enchmt': CardType.enchantment,
        'plnwkr': CardType.planeswalker,
        'artfct': CardType.artifact,
        'other': CardType.unknown

    }
    colors = {
        'COLOR_BLACK': Color.black,
        'COLOR_WHITE': Color.white,
        'COLOR_BLUE': Color.blue,
        'COLOR_RED': Color.red,
        'COLOR_GREEN': Color.green,
        'COLOR_COLORLESS': Color.colorless,
        'unknown': Color.unknown
    }

    if 'card_type' not in attributes:
        attributes['card_type'] = 'other'  # some dual sided new cards?
    if 'cost' not in attributes:
        attributes['cost'] = -1  # dual cards like Claim/Fame
    if 'colors' not in attributes:
        attributes['colors'] = ['unknown']  # Claim/Fame

    return Card(
        name=attributes['card_name'],
        cost=attributes['cost'],
        colors=[colors[color] for color in attributes['colors']],
        type=card_types[attributes['card_type'].lower().strip()],
        quantity=data['qty']
    )


def merge_cards(cards: List[Card]) -> List[Card]:
    """Removes duplicate cards and merges them"""
    by_name = dict()
    for card in cards:
        if card.name not in by_name:
            by_name[card.name] = card
        else:
            by_name[card.name].quantity += card.quantity

    return [card for _, card in by_name.items()]


class CompetitionScore(pydantic.BaseModel):
    """
    Score is a float between 0 and 1, where 1 means this deck always got first place
    and 0 means this deck always got last place
    """
    score: float
    number_of_entries: int


class CompetitionScoreListing(pydantic.BaseModel):
    result: dict[DeckName, CompetitionScore]
    matches_seen: int

    @classmethod
    def from_tournaments(cls, tournaments:  List[ClassifiedTournament]) -> 'CompetitionScoreListing':
        temporary_results: dict[DeckName, list[(float, int)]] = {}
        for tournament in tournaments:
            n = len(tournament.players)  # mtgo gives at most 32 results
            for player in tournament.players:
                score = (n - player.rank) / (n - 1)
                weight = tournament.player_count  # weigh larger tournamnets more
                if player.deck_name not in temporary_results:
                    temporary_results[player.deck_name] = []
                temporary_results[player.deck_name].append((score, weight))

        result = cls(result={}, matches_seen=0)
        for deck in temporary_results:
            total_score = 0
            total_weight = 0
            for score, weight in temporary_results[deck]:
                total_score += score * weight
                total_weight += weight
            result.result[deck] = CompetitionScore(
                score=total_score / total_weight,
                number_of_entries=len(temporary_results[deck])
            )
            result.matches_seen += len(temporary_results[deck])

        return result

    def __str__(self):
        results = [(name, self.result[name].score, self.result[name].number_of_entries/self.matches_seen)
                   for name in self.result]
        results.sort(key=lambda x: x[2], reverse=True)

        answer = f"{'Deck':<20} {'score':<4} {'meta share'}\n"
        answer += "="*len(answer) + "\n"
        for result in results:
            answer += f'{result[0]:<20} {result[1]:.2f} {result[2]*100:.2f}\n'
        return answer
