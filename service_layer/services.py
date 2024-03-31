import logging

import pymongo.database

from adapters.repository import AbstractRepository
from adapters.mtgo_api import AbstractAPI


def get_mongo_db() -> pymongo.database.Database:
    client = pymongo.MongoClient('mongodb://localhost:27017')
    return client.get_database('dev')


def cache_tournaments(api: AbstractAPI, repo: AbstractRepository):
    cached_tournaments = repo.list_cached_tournaments()

    for tournament_link in api.list_tournament_links():
        if tournament_link not in cached_tournaments:
            tournament = api.fetch_tournament(tournament_link)
            logging.info(f'adding tournament to cache: {tournament.description}-{tournament.id}')
            repo.add(tournament, tournament_link)
