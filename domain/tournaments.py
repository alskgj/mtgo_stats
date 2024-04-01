from datetime import datetime, timedelta
from typing import Dict, List

from domain.model import Tournament, Classifier, TournamentParticipant, DeckName


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

    def show_stats(self, max_days=14):
        win_rates = self.win_rates(max_days)
        play_rates = self.play_rates(max_days)
        combined = [{'name': deck, 'wr': win_rates[deck], 'pr': play_rates[deck]} for deck in win_rates]
        combined = sorted(combined, key=lambda deck: deck['pr'], reverse=True)

        title = f'{"Deck":<24}{"PR":<7}{"WR":<5}'
        print(title)
        print('='*len(title))
        for i, deck in enumerate(combined):
            if deck['name'] is None:
                deck['name'] = 'Not Classified'
            print(f'{i+1:<3}{deck["name"]:<21}{deck["pr"]:<7}{deck["wr"]:<5}')
