import typing

import pydantic
import pytest

import domain
import service_layer
from domain.rules import universal_classifier
from domain.stats import ResultHandler
from service_layer import stats
from service_layer.stats import get_stats


def test_win_rate_calculations(izzet_phoenix_result, rakdos_vampires_result):
    assert ResultHandler.calculate_win_rate([izzet_phoenix_result]).mean == 100.0
    assert ResultHandler.calculate_win_rate([rakdos_vampires_result]).mean == 50.0

    # 3 izzet phoenix wins, 1 rakdos vampire win, 1 rakdos vampire loss --> 80% WR
    assert ResultHandler.calculate_win_rate([izzet_phoenix_result, rakdos_vampires_result]).mean == 80.0


def test_play_rate_calculations(izzet_phoenix_result, rakdos_vampires_result):
    rh = ResultHandler([izzet_phoenix_result, rakdos_vampires_result])
    assert rh.calculate_play_rate(izzet_phoenix_result.deck_name) == 50.0
    assert rh.calculate_play_rate(rakdos_vampires_result.deck_name) == 50.0


def test_html_table():
    izzet_phoenix = domain.DeckStat(
        name=domain.DeckName('Izzet Phoenix'),
        win_rate=domain.WinRate(mean=47.94, lower_bound=44.54, upper_bound=51.35),
        play_rate=9.1,
        total_matches=800,
        example_link='https://www.mtgo.com/decklist/pioneer-challenge-32-2024-04-2612633733#deck_Hexapuss',
        hero_cards=['Arclight Phoenix']
    )
    spirits = domain.DeckStat(
        name=domain.DeckName('Spirits'),
        win_rate=domain.WinRate(mean=57.6, lower_bound=50.95, upper_bound=63.99),
        play_rate=2.69,
        total_matches=80,
        example_link='https://www.mtgo.com/decklist/pioneer-challenge-32-2024-04-2612633733#deck_remf',
        hero_cards=['Mausoleum Wanderer']
    )
    result = service_layer.stats.create_html_table([izzet_phoenix, spirits], colorize=False)

    # just check if this generates a table with 3 rows
    assert result.count('<table class="dimiTable">') == 1  # generate a table
    assert result.count('<tr>') == 3  # contains 3 rows


def test_extract_results(phoenix_tournament, classifier):
    result = stats.extract_results([phoenix_tournament], classifier)
    expected = f'{phoenix_tournament.link}#deck_{phoenix_tournament.players[0].name}'
    assert expected == result[0].link


def test_analyze(izzet_phoenix_result):
    """
    One Izzet Phoenix player went 3-0 with Lightning Axe, Izzet Phoenix,
    one izzet Phoenix player went 1-1 with Fiery Impulse, Izzet Phoenix

    --> analysis ranks:
    100% WR: Lightning Axe, Sample Size: 3 Matches, 60% PR
    80% WR: Izzet Phoenix, Sample Size: 5 Matches, 100% PR
    50% WR: Fiery Impulse, Sample Size 2 Matches, 40% PR
    """
    results = [izzet_phoenix_result]
    stats.analyze_deck(domain.DeckName('Izzet Phoenix'), results)


def test_get_stats(repo):
    decks = get_stats(repo, max_days=None)
    assert 'Izzet Phoenix' in [deck.name for deck in decks]
    assert 'Amalia Combo' in [deck.name for deck in decks]


@pytest.mark.parametrize("deck,score,entries", [
    ("Rakdos Vampires", 0.5, 2),
    ("Amalia Combo", 0.25, 1),
    ("Izzet Phoenix", 0.625, 2)
])
def test_calculate_competition_score(repo, deck, score, entries):
    """
    Make sure competition score is calculated correctly
    The tournament has 5 participants, Vamps got first and last place -> score of 0.5
    Amalia got place 4 --> score == 0.25 (scores from first to last place are: 1, 0.75, 0.5, 0.25, 0)
    Izzet phoenix got two results as rank 2 and 3 --> score = (0.75+0.5)/2 == 0.625
    """
    scores = stats.calculate_competition_score(repo, max_days=None)
    assert scores.result[domain.DeckName(deck)] == domain.CompetitionScore(score=score, number_of_entries=entries)


def test_scores(challenge_64):
    classifier = universal_classifier()
    # todo enhance test classifier with decks from this tournament and convert ct to fixture
    tournament = domain.ClassifiedTournament.from_tournament(challenge_64, classifier)
    score_listing = domain.CompetitionScoreListing.from_tournaments([tournament])

    assert challenge_64.player_count == 74
    assert score_listing.matches_seen == 32
    assert round(score_listing.result[domain.DeckName('Amalia Combo')].score, 2) == 0.58
