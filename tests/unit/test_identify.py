from domain.model import Classifier
import domain.rules as rules


def test_decks_are_identified_correctly(rakdos_vampires, izzet_phoenix, classifier: Classifier):
    assert classifier.classify(rakdos_vampires) == 'Rakdos Vampires'
    assert classifier.classify(izzet_phoenix) == 'Izzet Phoenix'
