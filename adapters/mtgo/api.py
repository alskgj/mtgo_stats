import abc
import asyncio
import json
import logging
from collections import defaultdict
from datetime import datetime
from typing import List

from bs4 import BeautifulSoup

import domain
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
        tournament_data = self.json_data(data)

        return domain.Tournament.from_json(tournament_data)

    @staticmethod
    def json_data(tournament_data: str) -> dict:
        for line in tournament_data.split('\n'):
            if 'window.MTGO.decklists.data' in line:
                return json.loads(line.strip().split(' = ')[1].strip(";"))

        raise ValueError('Could not find tournament data in html.')


def extract_links(tournament_page: str) -> list[str]:
    base = 'https://www.mtgo.com'
    soup = BeautifulSoup(tournament_page, features='html.parser')
    links = [decklist.get('href') for decklist in soup.find_all(class_='decklists-link')]
    tournaments = [base + link for link in links if 'pioneer' in link and 'league' not in link]
    return tournaments
