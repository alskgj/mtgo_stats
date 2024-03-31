import json

import pytest
import adapters.mtgo_api


@pytest.fixture
def tournament_data():
    with open('unit/tournament_data.json') as fo:
        data = json.load(fo)
    return data['tournament_cover_page_list'][0]


@pytest.fixture
def card_data():
    with open('unit/tournament_data.json') as fo:
        data = json.load(fo)
    return data['tournament_cover_page_list'][0]['decklists'][0]['main_deck'][0]


def test_parse_players(tournament_data):
    parsed = adapters.mtgo_api.parse_players(tournament_data)
    assert True


def test_parse_cards(card_data):
    parsed = adapters.mtgo_api.parse_card(card_data)
    assert True
