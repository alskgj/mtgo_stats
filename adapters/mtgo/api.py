import abc
import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from typing import List

from bs4 import BeautifulSoup

from adapters.mtgo.client import AbstractMtgoClient
from domain import model
from domain.model import TournamentParticipant, Deck, Card, CardType, Color


class AbstractAPI(abc.ABC):

    @abc.abstractmethod
    def __init__(self, client: AbstractMtgoClient):
        ...

    @abc.abstractmethod
    async def fetch_tournament_links(self, months) -> List[str]:
        """Fetch all tournament links for the last {months}"""
        ...

    @abc.abstractmethod
    async def fetch_tournament(self, tournament_link: str) -> model.Tournament:
        ...


class MtgoAPI(AbstractAPI):
    base_url = 'https://www.mtgo.com'

    def __init__(self, client: AbstractMtgoClient):
        self.client = client

    async def fetch_tournament_links(self, months=1) -> List[str]:
        """Fetch all tournament links for the last {months}.
        First get tournament pages, then parse those pages for the links.
        """
        targets = []
        year, month = datetime.now().year, datetime.now().month
        for i in range(months):
            targets.append((year, month))
            month -= 1
            if month < 1:
                year, month = year - 1, 12

        tasks = []
        async with asyncio.TaskGroup() as tg:
            for year, month in targets:
                tasks.append(tg.create_task(self.client.fetch_tournaments_page(year, month)))

        tournament_pages = [task.result() for task in tasks]

        return [link for tournament_page in tournament_pages for link in extract_links(tournament_page)]

    async def fetch_tournament(self, tournament_link: str) -> model.Tournament:
        logging.debug(f'Fetching new tournament: {tournament_link}.')

        data = await self.client.fetch_tournament(tournament_link)
        url = self._extract_census_link(data)

        tournament_data = await self.client.fetch_tournament_data(url)
        return parse_tournament(tournament_data, url)

    @staticmethod
    def _extract_census_link(tournament_data: str) -> str:
        for line in tournament_data.split('\n'):
            if 'window.MTGO.decklists.query' in line:
                return 'https://census.daybreakgames.com/' + line.strip().split(' = ')[1].strip("'").strip("';")

        raise ValueError('Could not find census link in tournament data.')


def extract_links(tournament_page: str) -> list[str]:
    base = 'https://www.mtgo.com'
    soup = BeautifulSoup(tournament_page, features='html.parser')
    links = [decklist.get('href') for decklist in soup.find_all(class_='decklists-link')]
    tournaments = [base + link for link in links if 'pioneer' in link and 'league' not in link]
    return tournaments


def parse_tournament(data: dict, link) -> model.Tournament:
    inner = data['tournament_cover_page_list'][0]
    date = inner['starttime']
    if ' ' in date:
        date = date.split(' ')[0]
    return model.Tournament(
        id=inner['event_id'],
        description=inner['description'],
        start_time=datetime.fromisoformat(date),
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
