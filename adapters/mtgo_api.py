import abc
import logging
from collections import defaultdict
from datetime import datetime
from typing import List

import requests
from bs4 import BeautifulSoup

from domain import model
from domain.model import TournamentParticipant, Deck, Card, CardType, Color


class AbstractAPI(abc.ABC):

    @abc.abstractmethod
    def list_tournament_links(self) -> List[str]:
        ...

    @abc.abstractmethod
    def fetch_tournament(self, tournament_link: str) -> model.Tournament:
        ...


class MtgoAPI(AbstractAPI):
    base_url = 'https://www.mtgo.com'

    def list_tournament_links(self) -> List[str]:
        data = requests.get(self.base_url+'/decklists').text
        soup = BeautifulSoup(data, features='html.parser')
        links = [decklist.get('href') for decklist in soup.find_all(class_='decklists-link')]
        tournaments = [self.base_url + l for l in links if 'pioneer' in l and 'league' not in l]
        logging.info(f'Found {len(tournaments)} pioneer tournaments.')
        return tournaments


    def fetch_tournament(self, tournament_link: str) -> model.Tournament:
        logging.info(f'Fetching new tournament: {tournament_link}.')
        r = requests.get(tournament_link)
        url = None
        for line in r.text.split('\n'):
            if 'window.MTGO.decklists.query' in line:
                url = 'https://census.daybreakgames.com/' + line.strip().split(' = ')[1].strip("'").strip("';")
        if url is None:
            raise NotImplementedError
        else:
            return self.parse_tournament(requests.get(url).json(), url)

    def parse_tournament(self, data: dict, link) -> model.Tournament:
        inner = data['tournament_cover_page_list'][0]
        return model.Tournament(
            id=inner['event_id'],
            description=inner['description'],
            start_time=datetime.fromisoformat(inner['starttime']),
            format='pioneer' if inner['format'] == 'CPIONEER' else inner['format'],
            players=parse_players(inner),
            link=link
        )


def parse_players(data: dict) -> List[TournamentParticipant]:
    """
    need
    name, rank, wins, losses, deck
    """
    intermediate = defaultdict(dict)

    # collect necessary data
    for entry in data['winloss']:
        intermediate[entry['loginid']]['wins'] = entry['wins']
        intermediate[entry['loginid']]['losses'] = entry['losses']
    for entry in data['standings']:
        intermediate[entry['loginid']]['rank'] = entry['rank']
    for entry in data['decklists']:
        intermediate[entry['loginid']]['name'] = entry['player']
        main_deck = merge_cards([parse_card(card_data) for card_data in entry['main_deck']])
        side_deck = merge_cards([parse_card(card_data) for card_data in entry['sideboard_deck']])
        intermediate[entry['loginid']]['deck'] = Deck(main=main_deck, side=side_deck)

    # build the tournament participant
    result = []
    for loginid, entry in intermediate.items():
        try:
            result.append(TournamentParticipant(
                name=entry['name'],
                rank=entry['rank'],
                wins=entry['wins'],
                losses=entry['losses'],
                deck=entry['deck']
            ))
        except KeyError:
            continue
    return result


def parse_card(data: dict) -> Card:
    attributes = data['card_attributes']
    card_types = {
        'iscrea': CardType.creature,
        'sorcry': CardType.sorcery,
        'instnt': CardType.instant,
        'land': CardType.land,
        'enchmt': CardType.enchantment,
        'plnwkr': CardType.planeswalker,
        'artfct': CardType.artifact,
        'other': CardType.unknown

    }
    colors = {
        'COLOR_BLACK': Color.black,
        'COLOR_WHITE': Color.white,
        'COLOR_BLUE': Color.blue,
        'COLOR_RED': Color.red,
        'COLOR_GREEN': Color.green,
        'COLOR_COLORLESS': Color.colorless,
        'unknown': Color.unknown
    }

    if 'card_type' not in attributes:
        attributes['card_type'] = 'other'  # some dual sided new cards?
    if 'cost' not in attributes:
        attributes['cost'] = -1  # dual cards like Claim/Fame
    if 'colors' not in attributes:
        attributes['colors'] = ['unknown']  # Claim/Fame

    return Card(
        name=attributes['card_name'],
        cost=attributes['cost'],
        colors=[colors[color] for color in attributes['colors']],
        type=card_types[attributes['card_type'].lower().strip()],
        quantity=data['qty']
    )


def merge_cards(cards: List[Card]) -> List[Card]:
    """Removes duplicate cards and merges them"""
    by_name = dict()
    for card in cards:
        if card.name not in by_name:
            by_name[card.name] = card
        else:
            by_name[card.name].quantity += card.quantity

    return [card for _, card in by_name.items()]
