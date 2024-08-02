from typing import List

from .model import Deck, AbstractClassificationRule, Classifier, DeckName, CardType


def deck_contains_at_least_three(deck: Deck, card_name: str) -> bool:
    return any([card.name == card_name and card.quantity >= 3 for card in deck.main])


class UWControl(AbstractClassificationRule):
    def heroes(self):
        return ["Dovin's Veto", 'No More Lies']

    @property
    def deck_name(self) -> DeckName:
        return DeckName('UW Control')

    def satisfied_by(self, deck: Deck):
        return ((deck.contains_at_least_three("Dovin's Veto") or
                deck.contains_at_least_three('No More Lies')) and
                sum([card.quantity for card in deck.main if card.type == CardType.creature]) < 3
                )


class RakdosLegacy(AbstractClassificationRule):
    def heroes(self):
        return ['Fable of the Mirror-Breaker', 'Bloodtithe Harvester']

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
    def heroes(self):
        return ['Sheoldred, the Apocalypse']

    @property
    def deck_name(self) -> DeckName:
        return DeckName('MonoB Midrange')

    def satisfied_by(self, deck: Deck):
        return (
            deck.contains_at_least(3, 'Sheoldred, the Apocalypse') and
            deck.contains_at_least(6, 'Swamp')
        )


class UBControl(AbstractClassificationRule):
    def heroes(self):
        return ['Watery Grave']

    @property
    def deck_name(self) -> DeckName:
        return DeckName('UB Control')

    def satisfied_by(self, deck: Deck):
        return (
            deck.contains_at_least(4, 'Watery Grave') and
            sum([card.quantity for card in deck.main if card.type == CardType.creature]) <= 4
        )


class MonoBControl(AbstractClassificationRule):
    def heroes(self):
        return ['Swamp']

    @property
    def deck_name(self) -> DeckName:
        return DeckName('MonoB Control')

    def satisfied_by(self, deck: Deck):
        return (
            sum([card.quantity for card in deck.main if card.type == CardType.creature]) <= 4 and
            deck.contains_at_least(10, 'Swamp')
        )


class IzzetControl(AbstractClassificationRule):

    def heroes(self):
        return ['Narset, Parter of Veils', 'Steam Vents']

    @property
    def deck_name(self) -> DeckName:
        return DeckName('MonoB Control')

    def satisfied_by(self, deck: Deck):
        return (
            deck.maindeck_creatures <= 5 and
            deck.contains_at_least(3, 'Narset, Parter of Veils') and
            deck.contains_at_least(4, 'Steam Vents')
        )


class SimpleRule(AbstractClassificationRule):
    def heroes(self):
        return self.cards

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
        SimpleRule('Gruul Show-Off', ['Slickshot Show-Off', 'Questing Druid']),
        SimpleRule('Wizard Show-Off', ['Slickshot Show-Off', "Wizard's Lightning"]),
        SimpleRule('Boros Show-Off', ['Slickshot Show-Off', 'Sacred Foundry']),
        SimpleRule('Rakdos Vampires', ['Vein Ripper', 'Sorin, Imperious Bloodlord']),
        SimpleRule('Izzet Phoenix', ['Arclight Phoenix', 'Fiery Impulse']),
        SimpleRule('Izzet Phoenix', ['Arclight Phoenix', 'Lightning Axe']),
        SimpleRule('Grixis Phoenix', ['Arclight Phoenix', 'Fatal Push']),
        SimpleRule('Amalia Combo', ['Amalia Benavides Aguirre', 'Wildgrowth Walker']),
        SimpleRule('Waste Not', ['Waste Not']),
        SimpleRule('Spirits', ['Supreme Phantom', 'Mausoleum Wanderer']),
        UWControl(),
        SimpleRule('Lotus Field', ['Lotus Field']),
        RakdosLegacy(),
        MonoBMidrange(),
        MonoBControl(),
        UBControl(),
        IzzetControl(),
        SimpleRule('Auras', ['Ethereal Armor']),
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
        SimpleRule('Green Creature Ramp', ['Cavalier of Thorns', 'Elvish Mystic', 'Llanowar Elves']),
        SimpleRule('Gruul Ramp', [
            'Escape to the Wilds', 'Wolfwillow Haven', 'Radha, Heart of Keld', 'World Breaker'
        ]),
        SimpleRule('Blue Tempo', ['Curious Obsession', 'Wizard\'s Retort', 'Lofty Denial']),
        SimpleRule('Angels', ['Resplendent Angel', 'Giada, Font of Hope', 'Bishop of Wings']),
        SimpleRule('Humans', ['Thalia\'s Lieutenant', 'Thalia, Guardian of Thraben']),
        SimpleRule('Rogues', ['Soaring Thought-Thief', 'Thieves\' Guild Enforcer']),
        SimpleRule('Elder Deep-Fiend Pile', ['Elder Deep-Fiend']),
        SimpleRule('Lotleth Troll Combo', ['Lotleth Troll']),
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
        SimpleRule('Golgari Control', ['Liliana of the Veil', 'Glimpse the Core', 'Up the Beanstalk']),
        SimpleRule('Spell Queller Tempo', ['Spell Queller']),
        SimpleRule('Pack Rats', ['Pack Rat']),
        SimpleRule('Lukka', ['Lukka, Coppercoat Outcast']),
        SimpleRule('Bard Class', ['Bard Class']),
        SimpleRule('Rakdos Legacy', ['Fable of the Mirror-Breaker', 'Graveyard Trespasser']),
        SimpleRule('Gruul Aggro', ['The Huntsman\'s Redemption', 'Kumano Faces Kakkazan']),
        SimpleRule('Gruul Aggro', ['Burning-Tree Emissary', 'Gleeful Demolition', 'Reckless Bushwhacker']),
        SimpleRule('Leyline of the Guildpact', ['Leyline of the Guildpact']),
        SimpleRule('Reenact the Crime', ['Reenact the Crime']),
        SimpleRule('Coveted Falcon', ['Coveted Falcon']),
        SimpleRule('Colossification', ['Colossification']),
        SimpleRule('Collected Company', ['Collected Company']),
        SimpleRule('Triskaidekaphile', ['Triskaidekaphile']),
        SimpleRule('Metalwork Colossus', ['Metalwork Colossus']),
        SimpleRule('Training Grounds Proft', ['Training Grounds', "Proft's Eidetic Memory"]),
        SimpleRule('Collector\'s Cage', ["Collector's Cage"]),
        SimpleRule('Soulflayer', ['Soulflayer']),
        SimpleRule('MonoB Control', ['Thoughtseize', 'Liliana of the Veil', 'Invoke Despair']),
        SimpleRule('Portal to Phyrexia', ['Portal to Phyrexia']),
        SimpleRule('The Book of Exalted Deeds', ['The Book of Exalted Deeds']),
        SimpleRule('Jace & Valki', ['Valki, God of Lies', 'Jace Reawakened']),
        SimpleRule('Ghired, Mirror of the Wilds', ['Ghired, Mirror of the Wilds']),
        SimpleRule('Slogurk Combo', ['Slogurk, the Overslime']),
        SimpleRule('Vannifar Combo', ['Prime Speaker Vannifar']),
        SimpleRule('Beseech the Mirror', ['Beseech the Mirror']),
        SimpleRule('Corpses of the Lost', ['Corpses of the Lost']),
        SimpleRule('Red Aggro', ['Eidolon of the Great Revel', 'Kumano Faces Kakkazan']),
        SimpleRule('White Cats', ['Regal Caracal', 'Kutzil\'s Flanker']),
        SimpleRule('Aftermath Spelunking', ['Aftermath Analyst', 'Spelunking']),
        SimpleRule('Profts Duelist', ['Duelist of the Mind', "Proft's Eidetic Memory"]),
        SimpleRule('Freestrider Crimes', ['Freestrider Lookout']),
        SimpleRule('Dragons', ['Orator of Ojutai', "Silumgar's Scorn"]),
        SimpleRule('WB Midrange', ['Caustic Bronco', "Wedding Announcement"]),
        SimpleRule('W Aggro', ['Adeline, Resplendent Cathar', "Thalia's Lieutenant"]),
        SimpleRule('Golgari Midrange', ['Reckoner Bankbuster', "Pillage the Bog"]),
        SimpleRule('MonoW Control', ['The Wandering Emperor', "Settle the Wreckage"]),
        SimpleRule('Cavalcade Aggro', ['Cavalcade of Calamity']),
        SimpleRule('Aetherworks Marvel', ['Aetherworks Marvel']),
        SimpleRule('MonoB', ['Gifted Aetherborn']),
        SimpleRule('Nine Lives', ['Nine Lives']),
        SimpleRule('Enigma Jewel', ['The Enigma Jewel']),
        SimpleRule('Mill', ['Fraying Sanity']),
        SimpleRule('Edgar\'s Awakening', ['Edgar\'s Awakening']),
        SimpleRule('Goblins', ['Hobgoblin Bandit Lord']),
        SimpleRule('Gruul Aggro', ['Burning-Tree Emissary']),

    ])
