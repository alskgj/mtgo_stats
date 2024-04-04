"""
Frontend commands

-- fetch decks from mtgo server
mtgotracker cache

-- find unclassified decks
mtgotracker unclassified

-- find decks that are classified by multiple Rules?

-- show stats
    args:
        columns (pr, wr, confidence interval, number of decks)
        detailed deck breakdowns (Izzet Phoenix w/ Temporal Trespass)
        filters
        time
mtgotracker stats -c pr -c wr -c num --sortkey pr


-- show deck archetypes
mtgotracker stats --deck "Izzet Phoenix" --card "Arclight Phoenix" --card "Temporal Trespass"
Deck                                   PR%    WR%    #decks
===========================================================
1  Izzet Phoenix (proft=0)             17.63  50.61  394
2  Izzet Phoenix (proft=2)             0.18   47.37  4
3  Izzet Phoenix (proft=1)             0.04   57.14  1


"""

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
