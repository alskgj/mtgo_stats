from typing import List

from domain.model import Deck, AbstractClassificationRule, Classifier, DeckName, CardType, Card


def deck_contains_at_least_three(deck: Deck, card_name: str) -> bool:
    return any([card.name == card_name and card.quantity >= 3 for card in deck.main])


class RedAggro(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Red Aggro')

    def satisfied_by(self, deck: Deck):
        return (deck.contains_at_least_three('Monastery Swiftspear') and
                (
                    deck.contains_at_least(2, 'Kumano Faces Kakkazan') or
                    deck.contains_at_least_three('Viashino Pyromancer')
                ))


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


class ProftsPhoenix(AbstractClassificationRule):
    @property
    def deck_name(self) -> DeckName:
        return DeckName('Profts Phoenix!')

    def satisfied_by(self, deck: Deck):
        return (deck.contains_at_least(1, "Proft's Eidetic Memory") and
                deck.contains_at_least(3, "Arclight Phoenix"))


class SimpleRule(AbstractClassificationRule):
    def __init__(self, name: str, key_cards: List[str]):
        self.name = name
        self.cards = key_cards

    def satisfied_by(self, deck: Deck) -> bool:
        return all([deck.contains_at_least_three(card) for card in self.cards])

    @property
    def deck_name(self) -> DeckName:
        return DeckName(self.name)


class RakdosVampires(AbstractClassificationRule):

    _name = DeckName('Rakdos Vampires')

    @property
    def deck_name(self) -> DeckName:
        return self._name

    def satisfied_by(self, deck: Deck):
        if not (deck.contains_at_least_three('Vein Ripper') and
                deck.contains_at_least_three('Sorin, Imperious Bloodlord')):
            return False
        self._name = DeckName(f'Rakdos Vampires')
        return True


def universal_classifier() -> Classifier:
    return Classifier([
        RedAggro(),
        RakdosVampires(),
        SimpleRule('Rakdos Vampires (Lili)', ['Vein Ripper', 'Sorin, Imperious Bloodlord',
                                              'Liliana of the Veil']),
        SimpleRule('Rakdos Vampires (Archfiend)', ['Vein Ripper', 'Sorin, Imperious Bloodlord',
                                                   'Archfiend of the Dross']),
        SimpleRule('Rakdos Vampires', ['Vein Ripper', 'Sorin, Imperious Bloodlord']),
        SimpleRule('Izzet Phoenix', ['Arclight Phoenix']),
        SimpleRule('Grixis Phoenix', ['Arclight Phoenix', 'Fatal Push']),
        SimpleRule('Amalia Combo', ['Amalia Benavides Aguirre', 'Wildgrowth Walker']),
        SimpleRule('Waste Not', ['Waste Not']),
        SimpleRule('Spirits', ['Supreme Phantom', 'Mausoleum Wanderer']),
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
        SimpleRule('Stormwing', ['Stormwing Entity']),
        SimpleRule('Niv-Mizzet, Supreme', ['Niv-Mizzet, Supreme']),
        SimpleRule('Elves, Supreme', ['Leaf-Crowned Visionary']),
        SimpleRule('Boros Vehicles', ['Veteran Motorist', 'Toolcraft Exemplar']),
        SimpleRule('Adventures', ['Lucky Clover']),
        SimpleRule('Omnath Pile', ['Omnath, Locus of Creation']),
    ])
