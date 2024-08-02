from adapters import MtgoAPI
from adapters.repository import MongoRepository
from domain import ClassifiedTournament, CompetitionScoreListing
from domain.rules import universal_classifier
from service_layer.services import get_mongo_db


def main():
    repo = MongoRepository(get_mongo_db())
    tournament_ids = repo.get_tournament_ids(21)
    raw_tournaments = [repo.get(id_) for id_ in tournament_ids]
    classifier = universal_classifier()
    tournaments = [ClassifiedTournament.from_tournament(t, classifier) for t in raw_tournaments]
    cs = CompetitionScoreListing.from_tournaments(tournaments)
    print(cs)
    print(cs.matches_seen)


if __name__ == '__main__':
    main()
