from typing import List

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


class WasteNot(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Waste Not')

    def satisfied_by(self, deck: Deck):
        return deck.contains_at_least_three('Waste Not')


class MonoRedAggro(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Mono Red Aggro')

    def satisfied_by(self, deck: Deck):
        return (deck.contains_at_least_three('Monastery Swiftspear') and
                deck.contains_at_least_three('Soul-Scar Mage') and
                deck.contains_at_least(8, 'Mountain'))


class Spirits(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Spirits')

    def satisfied_by(self, deck: Deck):
        return (deck.contains_at_least_three('Supreme Phantom') and
                deck.contains_at_least_three('Mausoleum Wanderer'))


class UWControl(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('UW Control')

    def satisfied_by(self, deck: Deck):
        return (deck.contains_at_least_three("Dovin's Veto") and
                deck.contains_at_least_three('No More Lies') and
                deck.contains_at_least(2, 'Teferi, Hero of Dominaria')
                )


class LotusField(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Lotus Field')

    def satisfied_by(self, deck: Deck):
        return (
            deck.contains_at_least(4, 'Lotus Field') and
            deck.contains_at_least_three('Thespian\'s Stage') and
            deck.contains_at_least_three('Pore Over the Pages')
        )


class SimpleRule(AbstractClassificationRule):
    def __init__(self, name: str, at_least_three_of: List[str]):
        self.name = name
        self.cards = at_least_three_of

    def satisfied_by(self, deck: Deck) -> bool:
        return all([deck.contains_at_least_three(card) for card in self.cards])

    @property
    def deck_name(self) -> DeckName:
        return DeckName(self.name)


def universal_classifier() -> Classifier:
    return Classifier([
        RakdosVampires(),
        IzzetPhoenix(),
        AmaliaCombo(),
        WasteNot(),
        MonoRedAggro(),
        Spirits(),
        UWControl(),
        LotusField(),
        SimpleRule('Auras', ['Ethereal Armor', 'Skrelv, Defector Mite']),
        SimpleRule('Bring to Light', ['Bring to Light']),
        SimpleRule('Boros Heroic', [
            'Favored Hoplite',
            'Monastery Swiftspear',
            'Illuminator Virtuoso'
        ]),
        SimpleRule('Boros Convoke', ['Venerated Loxodon', 'Knight-Errant of Eos']),


    ])
