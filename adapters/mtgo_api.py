import abc
import logging
from collections import defaultdict
from datetime import datetime
from typing import List

import httpx
from bs4 import BeautifulSoup

from domain import model
from domain.model import TournamentParticipant, Deck, Card, CardType, Color


class AbstractAPI(abc.ABC):

    @abc.abstractmethod
    async def list_tournament_links(self, months) -> List[str]:
        ...

    @abc.abstractmethod
    async def fetch_tournament(self, tournament_link: str) -> model.Tournament:
        ...


class MtgoAPI(AbstractAPI):
    base_url = 'https://www.mtgo.com'

    async def list_tournament_links(self, months=1) -> List[str]:
        tournaments = []

        today = datetime.now()
        year, month = today.year, today.month
        for i in range(months):
            url = f'{self.base_url}/decklists/{year}/{month:02}'
            logging.debug(f'Fetching tournaments for {month}/{year}')
            tournaments += await self._fetch_tournament_link_page(url)
            if month >= 1:
                month -= 1
            else:
                month = 12
                year -= 1

        logging.info(f'Found {len(tournaments)} pioneer tournaments.')
        return tournaments

    async def _fetch_tournament_link_page(self, url: str) -> List[str]:
        """Parses an url like https://www.mtgo.com/decklists/2024/05"""
        async with httpx.AsyncClient() as client:
            r = await client.get(url)
        data = r.text
        soup = BeautifulSoup(data, features='html.parser')
        links = [decklist.get('href') for decklist in soup.find_all(class_='decklists-link')]
        tournaments = [self.base_url + link for link in links if 'pioneer' in link and 'league' not in link]
        logging.debug(f'Found {len(tournaments)} tournaments on {url}')
        return tournaments

    async def fetch_tournament(self, tournament_link: str) -> model.Tournament:
        logging.debug(f'Fetching new tournament: {tournament_link}.')
        async with httpx.AsyncClient() as client:
            r = await client.get(tournament_link)
        url = None
        for line in r.text.split('\n'):
            if 'window.MTGO.decklists.query' in line:
                url = 'https://census.daybreakgames.com/' + line.strip().split(' = ')[1].strip("'").strip("';")
        if url is None:
            raise NotImplementedError

        async with httpx.AsyncClient(timeout=60, transport=httpx.AsyncHTTPTransport(retries=3)) as client:
            r = await client.get(url)
        return parse_tournament(r.json(), url)


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
