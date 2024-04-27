import logging
from typing import List

import pymongo.database

from adapters.repository import AbstractRepository
from adapters.mtgo_api import AbstractAPI
from domain.model import Classifier, Tournament, DeckName, Deck, CardType


def get_mongo_db() -> pymongo.database.Database:
    client = pymongo.MongoClient('mongodb://localhost:27017')
    return client.get_database('mtgo-stats-dev')


def cache_tournaments(api: AbstractAPI, repo: AbstractRepository):
    cached_tournaments = repo.list_cached_tournaments()

    for tournament_link in api.list_tournament_links():
        if tournament_link not in cached_tournaments:
            tournament = api.fetch_tournament(tournament_link)
            logging.info(f'adding tournament to cache: {tournament.description}-{tournament.id}')
            repo.add(tournament, tournament_link)


def print_deck_summary(deck: Deck):
    four_offs = [card for card in deck.main if card.quantity == 4 and card.type != CardType.land]
    if not four_offs:
        print(deck)
        return
    for card in four_offs:
        print(card)


def find_unclassified_decks(tournaments: List[Tournament], classifier: Classifier, verbose=False):
    classified, unclassified = 0, 0
    for tournament in tournaments:
        for player in tournament.players:
            if classifier.classify(player.deck) == DeckName('Unclassified Deck'):
                print(f'Unknown deck from {player.name} at: {tournament.link}')
                if verbose:
                    print(player.deck)
                else:
                    print_deck_summary(player.deck)
                    print()
                unclassified += 1
            else:
                classified += 1

    print(f'{classified}/{unclassified+classified} decks are classified')
