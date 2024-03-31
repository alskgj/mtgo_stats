from adapters.repository import AbstractRepository, AbstractAPI


def cache_tournaments(api: AbstractAPI, repo: AbstractRepository):
    cached_tournaments = repo.list_cached_tournaments()

    for tournament_link in api.list_tournament_links():
        if tournament_link not in cached_tournaments:
            tournament = api.fetch_tournament(tournament_link)
            repo.add(tournament, tournament_link)
