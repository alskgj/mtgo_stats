from datetime import datetime, timedelta
from typing import Dict, List

import pydantic
import numpy as np
import scipy

from adapters.repository import MongoRepository
from domain import rules
from domain.model import Tournament, Classifier, TournamentParticipant, DeckName, Card
from service_layer.services import get_mongo_db


class WinRate(pydantic.BaseModel):
    mean: float
    lower_bound: float
    upper_bound: float


def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return round(m, 2), round(m-h, 2), round(m+h, 2)


class TournamentHandler:
    def __init__(self, tournaments: List[Tournament], classifier: Classifier):
        self.tournaments = tournaments
        self.classifier = classifier

    def build_decks_tournament_mapping(self, max_days: int = 0) -> Dict[DeckName, List[TournamentParticipant]]:
        tournaments = self.tournaments
        if max_days > 0:
            tournaments = [t for t in self.tournaments if datetime.now() - t.start_time <= timedelta(days=max_days)]

        decks: Dict[DeckName, List[TournamentParticipant]] = {}
        for tournament in tournaments:
            for deckname, players in tournament.deckname_to_players(self.classifier).items():
                if deckname not in decks:
                    decks[deckname] = []
                decks[deckname] += players
        return decks

    def win_rates(self, max_days: int = 0) -> Dict[DeckName, float]:
        decks = self.build_decks_tournament_mapping(max_days)
        result = {}
        for deck_name in decks:

            total_wins = sum(p.wins for p in decks[deck_name])
            total_games = sum(p.wins + p.losses for p in decks[deck_name])
            result[deck_name] = round(total_wins / total_games * 100, 2)
        return result

    def play_rates(self, max_days: int = 0) -> Dict[DeckName, float]:
        decks = self.build_decks_tournament_mapping(max_days)
        result = {}
        total_decks = sum(len(decks[deck_name]) for deck_name in decks)
        for deck_name in decks:
            result[deck_name] = round(len(decks[deck_name])/total_decks*100, 2)
        return result

    def find_unclassified_decks(self):
        for tournament in self.tournaments:
            for player in tournament.players:
                if self.classifier.classify(player.deck) is None:
                    print(f'Unknown deck from {player.name} at: {tournament.link}')
                    print(player.deck)

    def show_stats(self, max_days=14):
        win_rates = self.win_rates(max_days)
        play_rates = self.play_rates(max_days)
        raw = self.build_decks_tournament_mapping(max_days)

        combined = [{'name': deck, 'wr': win_rates[deck], 'pr': play_rates[deck], 'num': len(raw[deck]),
                     }
                    for deck in win_rates]
        combined = sorted(combined, key=lambda deck: deck['pr'], reverse=True)

        name_length = max(len(deck['name']) for deck in combined if deck['name'])+6
        title = f'{"Deck":<{name_length}}{"PR%":<7}{"WR%":<7}{"#decks":<5}'
        print(title)
        print('='*len(title))

        i = 1
        for deck in combined:
            if deck['name'] is None:
                deck['name'] = DeckName('Not Classified')

            # if not deck['name'].startswith('Vamps'):
            #     continue
            # if not deck['name'].startswith('Izzet Phoenix'):
            #     continue

            print(f'{i:<3}{deck["name"]:<{name_length-3}}{deck["pr"]:<7}{deck["wr"]:<7}{deck["num"]:<5}')
            i += 1
