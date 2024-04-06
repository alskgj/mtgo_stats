from adapters.repository import MongoRepository
from domain import rules
from domain.tournaments import TournamentHandler
from service_layer.services import get_mongo_db
import logging


def main():
    logging.basicConfig(level=logging.INFO)

    # todo, give cache_tournaments a list of tournaments, instead of MtgoAPI()?
    repo = MongoRepository(get_mongo_db())
    # api = MtgoAPI()
    # cache_tournaments(api, repo)

    tournaments = list(repo.get_tournament_ids())
    all_tournaments = [repo.get(t) for t in tournaments]

    th = TournamentHandler(all_tournaments, rules.universal_classifier())
    th.find_unclassified_decks()
    th.show_stats(max_days=10)


if __name__ == '__main__':
    main()
