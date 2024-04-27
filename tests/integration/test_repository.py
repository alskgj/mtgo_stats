from typing import List

import pytest

import pymongo
import pymongo.database

import adapters.mtgo_api
import domain

from mtgoResultsTracker.adapters.repository import MongoRepository
from mtgoResultsTracker.service_layer.services import cache_tournaments


class FakeAPI(adapters.mtgo_api.AbstractAPI):
    """ Drop in replacement for the MTGO API for testing. Use register_tournament to """

    def __init__(self):
        self._tournaments = {}

    def fetch_tournament(self, tournament_link: str) -> domain.Tournament:
        return self._tournaments.get(tournament_link)

    def list_tournament_links(self) -> List[str]:
        return list(self._tournaments.keys())

    def register_tournament(self, link: str, tournament: domain.Tournament):
        self._tournaments[link] = tournament


@pytest.fixture()
def repo() -> MongoRepository:
    client = pymongo.MongoClient('mongodb://localhost:27017')
    yield MongoRepository(client.get_database('test'))
    client.drop_database('test')


def test_list_cached_tournaments(small_tournament, repo):
    # arrange
    api = FakeAPI()
    api.register_tournament('www.mtgo.com/tournaments/1', small_tournament)

    # act
    cache_tournaments(api, repo)

    assert repo.list_cached_tournaments() == {'www.mtgo.com/tournaments/1'}


def test_retrieving_tournaments(small_tournament, repo):
    # arrange
    api = FakeAPI()
    link = 'https://www.mtgo.com/decklist/pioneer-challenge-64-2024-03-3012623703'
    api.register_tournament(link, small_tournament)

    # act
    cache_tournaments(api, repo)

    # assert
    assert repo.get(small_tournament.id).model_dump() == small_tournament.model_dump()


def test_initially_empty(small_tournament, repo):
    api = FakeAPI()
    api.register_tournament('www.mtgo.com/tournaments/1', small_tournament)

    assert len(list(repo.db.tournaments.find())) == 0


def test_adding_tournament(small_tournament, repo):
    api = FakeAPI()
    api.register_tournament('www.mtgo.com/tournaments/1', small_tournament)

    cache_tournaments(api, repo)
    assert len(list(repo.db.tournaments.find())) == 1


def test_tournament_is_only_added_once(small_tournament, repo):
    api = FakeAPI()
    api.register_tournament('www.mtgo.com/tournaments/1', small_tournament)

    cache_tournaments(api, repo)
    cache_tournaments(api, repo)
    assert len(list(repo.db.tournaments.find())) == 1
