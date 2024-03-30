import pytest

from domain import rules
from domain.model import Tournament, Classifier
from domain.tournaments import TournamentHandler


def test_play_rate_calculations(small_tournament: Tournament):
    classifier = Classifier(rules=[rules.IzzetPhoenix(), rules.RakdosVampires()])
    play_rates = small_tournament.play_rates(classifier)
    assert play_rates == {'Izzet Phoenix': 0.33, 'Rakdos Vampires': 0.67}


def test_only_one_deck_play_rate_calculations(phoenix_tournament: Tournament):
    classifier = Classifier(rules=[rules.IzzetPhoenix(), rules.RakdosVampires()])
    play_rates = phoenix_tournament.play_rates(classifier)
    assert play_rates == {'Izzet Phoenix': 1}


@pytest.mark.parametrize("input_tournaments,win_rate", [
    (['small_tournament'], {'Izzet Phoenix': 100.0, 'Rakdos Vampires': 50.0}),
    (['small_tournament', 'small_tournament'], {'Izzet Phoenix': 100.0, 'Rakdos Vampires': 50.0}),
    (['small_tournament', 'phoenix_tournament'], {'Izzet Phoenix': 66.67, 'Rakdos Vampires': 50.0}),
])
def test_win_rate_calculations(input_tournaments, win_rate, request):
    # resolve tournament fixtures
    input_tournaments = [request.getfixturevalue(tournament) for tournament in input_tournaments]

    classifier = Classifier(rules=[rules.IzzetPhoenix(), rules.RakdosVampires(), rules.AmaliaCombo()])
    assert TournamentHandler(input_tournaments, classifier).win_rates() == win_rate


@pytest.mark.parametrize("input_tournaments,play_rate", [
    (['small_tournament'], {'Izzet Phoenix': 33.33, 'Rakdos Vampires': 66.67}),
    (['small_tournament', 'small_tournament'], {'Izzet Phoenix': 33.33, 'Rakdos Vampires': 66.67}),
    (['small_tournament', 'phoenix_tournament'], {'Izzet Phoenix': 60.0, 'Rakdos Vampires': 40.0}),
])
def test_play_rates_calculations(input_tournaments, play_rate, request):
    # resolve tournament fixtures
    input_tournaments = [request.getfixturevalue(tournament) for tournament in input_tournaments]

    classifier = Classifier(rules=[rules.IzzetPhoenix(), rules.RakdosVampires(), rules.AmaliaCombo()])
    assert TournamentHandler(input_tournaments, classifier).play_rates() == play_rate


def test_old_tournaments_calculations(phoenix_tournament, old_small_tournament):
    classifier = Classifier(rules=[rules.IzzetPhoenix(), rules.RakdosVampires(), rules.AmaliaCombo()])

    assert TournamentHandler([old_small_tournament], classifier).play_rates(max_days=14) == {}
    mixed_tournament = TournamentHandler([phoenix_tournament, old_small_tournament], classifier)
    assert mixed_tournament.play_rates(max_days=14) == {'Izzet Phoenix': 100.0}
