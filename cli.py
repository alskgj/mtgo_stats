"""
Frontend commands

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
import logging
import os
import webbrowser
from typing import Annotated, List

import typer

from adapters.mtgo_api import MtgoAPI
from adapters.repository import MongoRepository
from domain import rules
from domain.model import DeckName
from domain.stats import ResultHandler, extract_results
from service_layer.services import cache_tournaments, get_mongo_db, find_unclassified_decks
from service_layer.stats import get_stats, create_html_table, analyze_deck, display_deck_analysis

app = typer.Typer(pretty_exceptions_enable=False)


@app.command()
def fetch(months: int = 1):

    # todo implement
    if months != 1:
        raise NotImplementedError

    repo = MongoRepository(get_mongo_db())
    api = MtgoAPI()
    cache_tournaments(api, repo)


@app.command()
def unclassified(max_days: int = 7):
    repo = MongoRepository(get_mongo_db())
    tournaments = list(repo.get_tournament_ids(max_days))
    all_tournaments = [repo.get(t) for t in tournaments]
    find_unclassified_decks(all_tournaments, rules.universal_classifier())


@app.command()
def stats(
        deck: Annotated[str, typer.Option(help="Stats for a specific deck, e.g. 'Izzet Phoenix'")] = None,
        card: Annotated[List[str], typer.Option(help="Implies --deck, differentiate win rate by this card")] = None,
        max_days: int = 14,
        max_results: int = 15,
        fmt: str = 'text',
        colorize: bool = True
):

    deck = DeckName(deck)
    if card and deck is None:
        print("Got --card {card}, but no deck specified!")
        return
    if card is None:
        card = []
    repo = MongoRepository(get_mongo_db())

    if fmt == 'html':
        s = get_stats(repo, deck, cards=card, max_days=max_days)[:max_results]
        table = create_html_table(s, colorize)
        with open('out.html', 'w') as f:
            f.write(table)
        webbrowser.open('file://'+os.path.realpath('out.html'))
        return

    tournaments = list(repo.get_tournament_ids(max_days))
    all_tournaments = [repo.get(t) for t in tournaments]
    results = extract_results(all_tournaments, rules.universal_classifier())
    rh = ResultHandler(results)

    # filter decks   -> fewer decks
    if deck:
        rh.split_deck_by_cards(deck, card)

    # display stats
    print(f'Displaying Stats for the last {max_results} days')
    rh.show_stats(max_results=max_results)


@app.command()
def analyze(
        deck: Annotated[str, typer.Option(help="Stats for a specific deck, e.g. 'Izzet Phoenix'")],
        max_days: int = 14,
):
    repo = MongoRepository(get_mongo_db())
    tournaments = list(repo.get_tournament_ids(max_days))
    all_tournaments = [repo.get(t) for t in tournaments]
    results = extract_results(all_tournaments, rules.universal_classifier())
    data = analyze_deck(DeckName(deck), results)
    display_deck_analysis(data)


def main():
    logging.getLogger('pymongo').setLevel(logging.WARNING)
    logging.basicConfig(level=logging.INFO)
    app()


if __name__ == '__main__':
    main()
