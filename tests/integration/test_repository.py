from typing import List

import pymongo
import pymongo.database
import pytest

import adapters.mtgo.api
import domain
from adapters.repository import MongoRepository
from service_layer.services import cache_tournaments

pytestmark = pytest.mark.slow


# todo: remove, replace with real api using fake client instead?
class FakeAPI(adapters.mtgo.api.AbstractAPI):
    """ Drop in replacement for the MTGO API for testing. Use register_tournament to """

    def __init__(self):
        self._tournaments = {}

    async def fetch_tournament(self, tournament_link: str) -> domain.Tournament:
        return self._tournaments.get(tournament_link)

    async def fetch_tournament_links(self, months=1) -> List[str]:
        return list(self._tournaments.keys())

    def register_tournament(self, link: str, tournament: domain.Tournament):
        """Helper function for testing - adds a new tournament to the FakeMTGO Database"""
        self._tournaments[link] = tournament


@pytest.fixture
def repo() -> MongoRepository:
    client = pymongo.MongoClient('mongodb://localhost:27017')
    yield MongoRepository(client.get_database('test'))
    client.drop_database('test')


@pytest.mark.asyncio
async def test_list_cached_tournaments(small_tournament, repo):
    # arrange
    api = FakeAPI()
    api.register_tournament('www.mtgo.com/tournaments/1', small_tournament)

    # act
    await cache_tournaments(api, repo)

    assert repo.list_cached_tournaments() == {'www.mtgo.com/tournaments/1'}


@pytest.mark.asyncio
async def test_retrieving_tournaments(small_tournament, repo):
    # arrange
    api = FakeAPI()
    link = 'https://www.mtgo.com/decklist/pioneer-challenge-64-2024-03-3012623703'
    api.register_tournament(link, small_tournament)

    # act
    await cache_tournaments(api, repo)

    # assert
    assert repo.get(small_tournament.id).model_dump() == small_tournament.model_dump()


def test_initially_empty(small_tournament, repo):
    api = FakeAPI()
    api.register_tournament('www.mtgo.com/tournaments/1', small_tournament)

    assert len(list(repo.db.tournaments.find())) == 0


@pytest.mark.asyncio
async def test_adding_tournament(small_tournament, repo):
    api = FakeAPI()
    api.register_tournament('www.mtgo.com/tournaments/1', small_tournament)

    await cache_tournaments(api, repo)
    assert len(list(repo.db.tournaments.find())) == 1


@pytest.mark.asyncio
async def test_tournament_is_only_added_once(small_tournament, repo):
    api = FakeAPI()
    api.register_tournament('www.mtgo.com/tournaments/1', small_tournament)

    await cache_tournaments(api, repo)
    await cache_tournaments(api, repo)
    assert len(list(repo.db.tournaments.find())) == 1
