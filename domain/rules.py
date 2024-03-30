
from domain.model import Deck, AbstractClassificationRule, Classifier, DeckName


class RakdosVampires(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Rakdos Vampires')

    def satisfied_by(self, deck: Deck):
        contains_sorin, contains_ripper = False, False
        for card in deck.main:
            if card.name == 'Vein Ripper' and card.quantity >= 3:
                contains_ripper = True
            if card.name == 'Sorin, Imperious Bloodlord' and card.quantity >= 3:
                contains_sorin = True
        return contains_ripper and contains_sorin


class IzzetPhoenix(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Izzet Phoenix')

    def satisfied_by(self, deck: Deck):
        return any([card.name == 'Arclight Phoenix' and card.quantity >= 3 for card in deck.main])


def universal_classifier() -> Classifier:
    return Classifier([RakdosVampires(), IzzetPhoenix()])
