from datetime import datetime, timedelta
from typing import Dict, List

from domain.model import Tournament, Classifier, TournamentParticipant, DeckName
from pprint import pprint

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

    def win_rates(self, max_days: int = 0) -> Dict[str, float]:
        decks = self.build_decks_tournament_mapping(max_days)
        result = {}
        for deck_name in decks:
            total_wins = sum(p.wins for p in decks[deck_name])
            total_games = sum(p.wins + p.losses for p in decks[deck_name])
            result[deck_name] = round(total_wins / total_games * 100, 2)
        return result

    def play_rates(self, max_days: int = 0) -> Dict[str, float]:
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
