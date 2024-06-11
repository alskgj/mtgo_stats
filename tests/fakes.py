import datetime
from typing import List, Set

import domain
from adapters.repository import AbstractRepository


class FakeRepository(AbstractRepository):
    def __init__(self):
        self._tournaments: dict[int, domain.Tournament] = {}
        self._cached: list[str] = []

    def get(self, tournament_id: int) -> domain.Tournament:
        return self._tournaments[tournament_id]

    def get_tournament_ids(self, max_days=None) -> Set[int]:
        now = datetime.datetime.now()
        relevant = [
            tournament.id for _, tournament in self._tournaments.items()
            if not max_days or (now - tournament.start_time).days < max_days
        ]
        return set(relevant)

    def add(self, tournament: domain.Tournament, tournament_link: str):
        self._tournaments[tournament.id] = tournament
        self._cached.append(tournament_link)

    def list_cached_tournaments(self) -> List[str]:
        return self._cached
