import abc
from typing import List, Set

from domain import model
from pymongo.database import Database
from pymongo.collection import Collection
import datetime


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, tournament: model.Tournament, tournament_link: str):
        ...

    @abc.abstractmethod
    def get(self, tournament_id: int) -> model.Tournament:
        ...

    @abc.abstractmethod
    def list_cached_tournaments(self) -> List[str]:
        ...

    @abc.abstractmethod
    def get_tournament_ids(self, max_days=None) -> Set[int]:
        ...


class MongoRepository(AbstractRepository):

    def __init__(self, database: Database):
        self.db = database
        self.tournaments: Collection = database.tournaments

    def add(self, tournament: model.Tournament, tournament_link: str):
        data = tournament.model_dump()
        data['link'] = tournament_link
        self.tournaments.insert_one(data)

    def get(self, tournament_id: int) -> model.Tournament:
        data = self.tournaments.find_one({'id': tournament_id})
        return model.Tournament(**data)

    def list_cached_tournaments(self) -> Set[str]:
        only_link_field_query = [{'$project': {'link': 1}}]
        result = self.tournaments.aggregate(only_link_field_query)
        return set(r['link'] for r in result)

    def get_tournament_ids(self, max_days=None) -> Set[int]:
        if max_days is None:
            only_link_field_query = [{'$project': {'id': 1}}]
        else:
            date = datetime.datetime.now() - datetime.timedelta(days=max_days)
            only_link_field_query = [
                {'$match': {'start_time': {'$gte': date}}},
                {'$project': {'id': 1}}
            ]

        result = self.tournaments.aggregate(only_link_field_query)
        return set(r['id'] for r in result)
