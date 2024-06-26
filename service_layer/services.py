import logging
from typing import List

import pymongo.database

from adapters.repository import AbstractRepository
from adapters.mtgo_api import AbstractAPI
from domain.model import Classifier, Tournament, DeckName, Deck, CardType
import logging
import os

logger = logging.getLogger(__name__)


def get_mongo_db() -> pymongo.database.Database:
    connection = os.environ.get('MONGO_CONNECTION')
    if not connection:
        logger.info(f'Connecting to MongoDB using default credentials on localhost')
        client = pymongo.MongoClient('mongodb://localhost:27017')
    else:
        logger.info(f'Connecting to MongoDB using {connection}')
        client = pymongo.MongoClient(connection)

    return client.get_database('mtgo-stats-dev')


def cache_tournaments(api: AbstractAPI, repo: AbstractRepository, months=1):
    cached_tournaments = set(repo.list_cached_tournaments())
    available_tournaments = set(api.list_tournament_links(months))
    uncached_tournaments = available_tournaments - cached_tournaments
    logging.info(f'Caching {len(uncached_tournaments)} new tournaments...')
    for tournament_link in uncached_tournaments:
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
            if classifier.classify(player.deck) == DeckName('Unclassified Decks'):
                print(f'{tournament.link}#deck_{player.name}')
                if verbose:
                    print(player.deck)
                else:
                    print_deck_summary(player.deck)
                    print()
                unclassified += 1
            else:
                classified += 1

    print(f'{unclassified} decks are not classified yet')
