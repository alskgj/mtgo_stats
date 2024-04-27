from domain import Classifier


def test_decks_are_identified_correctly(rakdos_vampires, izzet_phoenix, classifier: Classifier):
    assert classifier.classify(rakdos_vampires) == 'Rakdos Vampires'
    assert classifier.classify(izzet_phoenix) == 'Izzet Phoenix'
