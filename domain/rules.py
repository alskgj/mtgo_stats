
from domain.model import Deck, AbstractClassificationRule, Classifier, DeckName


def deck_contains_at_least_three(deck: Deck, card_name: str) -> bool:
    return any([card.name == card_name and card.quantity >= 3 for card in deck.main])


class RakdosVampires(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Rakdos Vampires')

    def satisfied_by(self, deck: Deck):
        return (deck.contains_at_least_three('Vein Ripper') and
                deck.contains_at_least_three('Sorin, Imperious Bloodlord'))


class IzzetPhoenix(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Izzet Phoenix')

    def satisfied_by(self, deck: Deck):
        return deck.contains_at_least_three('Arclight Phoenix')


class AmaliaCombo(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Amalia Combo')

    def satisfied_by(self, deck: Deck):
        return (deck.contains_at_least_three('Amalia Benavides Aguirre') and
                deck.contains_at_least_three('Wildgrowth Walker'))


def universal_classifier() -> Classifier:
    return Classifier([RakdosVampires(), IzzetPhoenix(), AmaliaCombo()])
