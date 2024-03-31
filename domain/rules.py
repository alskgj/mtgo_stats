from typing import List

from domain.model import Deck, AbstractClassificationRule, Classifier, DeckName, CardType


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


class RedAggro(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Red Aggro')

    def satisfied_by(self, deck: Deck):
        return (deck.contains_at_least_three('Monastery Swiftspear') and
                deck.contains_at_least(2, 'Kumano Faces Kakkazan'))


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
        return ((deck.contains_at_least_three("Dovin's Veto") or
                deck.contains_at_least_three('No More Lies')) and
                sum([card.quantity for card in deck.main if card.type == CardType.creature]) < 3
                )


class LotusField(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Lotus Field')

    def satisfied_by(self, deck: Deck):
        return (
            deck.contains_at_least(4, 'Lotus Field')
        )


class RakdosLegacy(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Rakdos Legacy')

    def satisfied_by(self, deck: Deck):
        return (
            deck.contains_at_least(3, 'Bloodtithe Harvester') and
            not deck.contains_at_least(1, 'Vein Ripper') and
            deck.contains_at_least_three('Fable of the Mirror-Breaker')
        )


class MonoBMidrange(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('MonoB Midrange')

    def satisfied_by(self, deck: Deck):
        return (
            deck.contains_at_least(3, 'Sheoldred, the Apocalypse') and
            deck.contains_at_least(6, 'Swamp')
        )


class IzzetTiTi(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Izzet TiTi')

    def satisfied_by(self, deck: Deck):
        return (
            deck.contains_at_least(2, 'Thing in the Ice') and
            deck.contains_at_least(4, 'Narset, Parter of Veils') and
            not deck.contains_at_least(1, 'Arclight Phoenix')
        )


class UBControl(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('UB Control')

    def satisfied_by(self, deck: Deck):
        return (
            deck.contains_at_least(4, 'Watery Grave') and
            sum([card.quantity for card in deck.main if card.type == CardType.creature]) <= 4
        )


class MonoBControl(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('MonoB Control')

    def satisfied_by(self, deck: Deck):
        return (
            sum([card.quantity for card in deck.main if card.type == CardType.creature]) <= 4 and
            deck.contains_at_least(10, 'Swamp')
        )


class IzzetControl(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('MonoB Control')

    def satisfied_by(self, deck: Deck):
        return (
            deck.maindeck_creatures <= 5 and
            deck.contains_at_least(3, 'Narset, Parter of Veils') and
            deck.contains_at_least(4, 'Steam Vents')
        )


class GolgariMidrange(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Golgari Midrange')

    def satisfied_by(self, deck: Deck):
        return (
            deck.maindeck_creatures >= 12 and
            deck.contains_at_least(4, 'Overgrown Tomb')
        )


class MemeDeck(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Meme')

    def satisfied_by(self, deck: Deck):
        return (
            sum([card.quantity for card in deck.main if card.type == CardType.land]) == 60
        )


class SimpleRule(AbstractClassificationRule):
    def __init__(self, name: str, key_cards: List[str]):
        self.name = name
        self.cards = key_cards

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
        RedAggro(),
        Spirits(),
        UWControl(),
        LotusField(),
        RakdosLegacy(),
        MonoBMidrange(),
        IzzetTiTi(),
        MemeDeck(),
        MonoBControl(),
        UBControl(),
        IzzetControl(),
        SimpleRule('Auras', ['Ethereal Armor', 'Skrelv, Defector Mite']),
        SimpleRule('Bring to Light', ['Bring to Light']),
        SimpleRule('Boros Heroic', [
            'Favored Hoplite', 'Monastery Swiftspear', 'Illuminator Virtuoso'
        ]),
        SimpleRule('Boros Convoke', ['Venerated Loxodon', 'Knight-Errant of Eos']),
        SimpleRule('Enigmatic Fires', ['Enigmatic Incarnation']),
        SimpleRule('UW Control', ['Memory Deluge', 'Dovin\'s Veto', 'Supreme Verdict']),
        SimpleRule('Izzet Creativity', [
            'Torrential Gearhulk', 'Magma Opus', 'Indomitable Creativity'
        ]
                   ),
        SimpleRule('Greasefang', ['Greasefang, Okiba Boss', 'Parhelion II']),
        SimpleRule('Creativity', ['Indomitable Creativity']),
        SimpleRule('Ensoul Artifact', ['Ensoul Artifact']),
        SimpleRule('Quintorius Combo', ['Quintorius Kand']),
        SimpleRule('Transmogrify', ['Transmogrify']),
        SimpleRule('Green Devotion', [
            'Nykthos, Shrine to Nyx', 'Kiora, Behemoth Beckoner', 'Cavalier of Thorns']),
        SimpleRule('Selesnya Company', [
            'Collected Company', 'Prosperous Innkeeper', 'Selfless Spirit'
        ]),
        SimpleRule('UB Archfiend', ['Archfiend of the Dross', 'Metamorphic Alteration']),
        SimpleRule('Green Creature Ramp', ['Castle Garenbrig']),
        SimpleRule('Gruul Ramp', [
            'Escape to the Wilds', 'Wolfwillow Haven', 'Radha, Heart of Keld', 'World Breaker'
        ]),
        SimpleRule('Blue Tempo', ['Curious Obsession', 'Wizard\'s Retort', 'Lofty Denial']),
        SimpleRule('Angels', ['Resplendent Angel', 'Giada, Font of Hope', 'Bishop of Wings']),
        SimpleRule('Humans', ['Thalia\'s Lieutenant', 'Thalia, Guardian of Thraben']),
        SimpleRule('Rogues', ['Soaring Thought-Thief', 'Thieves\' Guild Enforcer']),
        SimpleRule('Elder Deep-Fiend Pile', ['Elder Deep-Fiend']),
        SimpleRule('Lotleth Troll Combo', ['Lotleth Troll']),
        GolgariMidrange(),
        SimpleRule('Boros Burn', [
            'Monastery Swiftspear', 'Boros Charm', 'Lightning Helix', 'Skewer the Critics'
        ]),
        SimpleRule('Gruul Aggro', ['Reckless Stormseeker', 'Elvish Mystic']),
        SimpleRule('Merfolk', ['Vodalian Hexcatcher']),
        SimpleRule('Jeskai Ascendancy', ['Jeskai Ascendancy']),
        SimpleRule('Izzet Drakes', ['Crackling Drake', 'Ledger Shredder']),
        SimpleRule('Gruul Madness', ['Burning-Tree Emissary', 'Hazoret the Fervent']),
        SimpleRule('Adventures', ['Lucky Clover']),
    ])
