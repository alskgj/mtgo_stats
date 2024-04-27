from .services import get_mongo_db
from ..adapters.repository import MongoRepository, AbstractRepository
from ..domain import rules
from ..domain.stats import extract_results, ResultHandler


def get_stats(repo: AbstractRepository, max_days=14):
    tournaments = list(repo.get_tournament_ids(max_days))
    all_tournaments = [repo.get(t) for t in tournaments]
    results = extract_results(all_tournaments, rules.universal_classifier())
    rh = ResultHandler(results)

    # display stats
    rh.show_stats()
