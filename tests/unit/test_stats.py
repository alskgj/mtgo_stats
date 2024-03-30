from domain import rules
from domain.model import Tournament, Classifier


def test_win_rate_calculations(small_tournament: Tournament):
    classifier = Classifier(rules=[rules.IzzetPhoenix(), rules.RakdosVampires()])
    win_rates = small_tournament.win_rates(classifier)
    assert win_rates == {'Izzet Phoenix': 100.0, 'Rakdos Vampires': 50.0}


def test_play_rate_calculations(small_tournament: Tournament):
    classifier = Classifier(rules=[rules.IzzetPhoenix(), rules.RakdosVampires()])
    play_rates = small_tournament.play_rates(classifier)
    assert play_rates == {'Izzet Phoenix': 0.33, 'Rakdos Vampires': 0.67}
