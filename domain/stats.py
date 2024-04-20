from collections import defaultdict
from datetime import datetime, timedelta
from typing import List, Dict

import numpy
import scipy

from .model import Classifier, Tournament, DeckName, Result, Deck, DeckStat, WinRate


def mean_confidence_interval(data, confidence=0.95):
    if data == [0.0]:
        return 0, 0, 0
    data = 1.0 * numpy.array(data)
    mean, standard_error = numpy.mean(data), scipy.stats.sem(data)
    confidence = standard_error * scipy.stats.t.ppf((1 + confidence) / 2., len(data)-1)
    return round(mean, 4), round(mean-confidence, 4), round(mean+confidence, 4)


def test_mean_confidence_interval():
    data = [0.5, 0.55, 0.6, 0.6]
    mean, lower, upper = mean_confidence_interval(data)
    assert 0.56 == mean
    assert 0.49 == lower
    assert 0.64 == upper


def extract_results(tournaments: List[Tournament], classifier: Classifier) -> List[Result]:
    result: List[Result] = []

    for tournament in tournaments:
        for player in tournament.players:
            result.append(Result(
                deck=player.deck,
                deck_name=classifier.classify(player.deck),
                wins=player.wins,
                losses=player.losses,
                date=tournament.start_time
            ))
    return result


class ResultHandler:
    def __init__(self, results: List[Result]):
        self._population = results
        self.results = results

    def filter(self, max_days=14):
        """
        Filters all results to only contain certain decks

        max_days    Remove all tournaments older than max_days. 0 for no time limit.
        """

        if max_days > 0:
            self.results = [r for r in self.results if datetime.now() - r.date <= timedelta(days=max_days)]

        self._population = self.results

    def split_deck_by_cards(self, deck: DeckName, cards: List[str]):
        """
        Filters all results for a single, specific deck


        deck        Specifies a deck name. Removes all decks from all tournaments that
                    do not contain this string.
        cards       Re-classifies the deck according to how many of card are played
        """

        new_results: List[Result] = []

        for result in self.results:
            if deck != result.deck_name:
                continue

            for name in cards:
                num = sum([card.quantity for card in result.deck.main+result.deck.side if card.name == name])
                result.deck_name = f'{result.deck_name} ({num}x {name})'
            new_results.append(result)

        self.results = new_results

    @staticmethod
    def calculate_win_rate(results: List[Result]) -> WinRate:

        # calculate a WR for every result, weigh it according to number of matches played
        weighted_winrates = []
        for result in results:
            wr = result.wins/(result.wins+result.losses)
            weighted_winrates += [wr]*(result.wins+result.losses)
        mean, lower, upper = mean_confidence_interval(weighted_winrates)

        return WinRate(mean=round(mean*100, 2), lower_bound=round(lower*100, 2), upper_bound=round(upper*100, 2))

    def calculate_play_rate(self, deck: DeckName) -> float:
        # play rate compared with all decks, not just filtered
        total_number_of_decks = len(self._population)
        deck_of_interest = len([res for res in self.results if res.deck_name == deck])
        return round(deck_of_interest/total_number_of_decks*100, 2)

    def calculate_deck_stats(self) -> List[DeckStat]:
        deck_stats: List[DeckStat] = []
        decks: Dict[DeckName, List[Result]] = defaultdict(list)
        for result in self.results:
            decks[result.deck_name].append(result)

        for deck in decks:
            deck_stats.append(DeckStat(
                name=deck,
                win_rate=self.calculate_win_rate(decks[deck]),
                play_rate=self.calculate_play_rate(deck),
                total_matches=sum([d.wins+d.losses for d in decks[deck]]),
            ))

        return deck_stats

    def show_stats(self, min_matches=0):
        deck_stats = self.calculate_deck_stats()
        deck_stats.sort(key=lambda a: a.play_rate, reverse=True)
        deck_stats = [d for d in deck_stats if d.total_matches >= min_matches]

        name_length = max(len(deck.name) for deck in deck_stats)+3
        title = f'{"#":<3}{"Deck":<{name_length}}{"PR%":<7}{"WR%":<7}95% CI: [L, U]    {"#matches":<5}'
        print(title)
        print('=' * len(title))

        for i, deck in enumerate(deck_stats):
            print(f'{i+1:<3}{deck.name:<{name_length}}{deck.play_rate:<7}{deck.win_rate.mean:<7}'
                  f'[{deck.win_rate.lower_bound:<5}%, {deck.win_rate.upper_bound:<5}%]  {deck.total_matches:<5}')
