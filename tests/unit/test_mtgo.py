import json

import pytest

import adapters
from adapters import MtgoAPI
from adapters.mtgo.client import AbstractMtgoClient
import pathlib

TEST_DATA = pathlib.Path(__file__).parent.parent.resolve() / 'data'


class FakeMtgoClient(AbstractMtgoClient):

    async def fetch_tournaments_page(self, year, month):
        with open(TEST_DATA / 'response_tournaments_page.html') as fo:
            return fo.read()

    async def fetch_tournament(self, url) -> str:
        with open(TEST_DATA / 'response_tournament_challenge_64.html') as fo:
            return fo.read()


@pytest.fixture
def tournament_data():
    with open(TEST_DATA / 'response_tournament_challenge_64.json') as fo:
        data = json.load(fo)
    return data


@pytest.fixture
def card_data():
    with open(TEST_DATA / 'response_tournament_challenge_64.json') as fo:
        data = json.load(fo)
    return data['decklists'][0]['main_deck'][0]


@pytest.fixture
def mtgo_api() -> MtgoAPI:
    return MtgoAPI(FakeMtgoClient())


def test_parse_players(tournament_data):
    parsed = adapters.mtgo.api.parse_players(tournament_data)
    assert True


def test_parse_cards(card_data):
    parsed = adapters.mtgo.api.parse_card(card_data)
    assert True


@pytest.mark.asyncio
async def test_fetch_tournament_links(mtgo_api):
    links = await mtgo_api.fetch_tournament_links()
    assert len(links) == 71
    assert 'https://www.mtgo.com/decklist/pioneer-challenge-32-2024-05-3112643048' in links


@pytest.mark.asyncio
async def test_fetch_tournament(mtgo_api):
    tournament = await mtgo_api.fetch_tournament('fake')
    assert len(tournament.players) == 32
