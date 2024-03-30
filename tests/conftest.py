import pytest

from domain.model import Deck, Card, Rarity, Color, CardType, Tournament, TournamentParticipant


@pytest.fixture
def rakdos_vampires() -> Deck:
    return Deck(main=[
        Card(
            name='Vein Ripper',
            cost=6,
            id=1,
            rarity=Rarity.rare,
            colors=[Color.black],
            type=CardType.creature,
            quantity=4
        ),
        Card(
            name='Sorin, Imperious Bloodlord',
            cost=3,
            id=2,
            rarity=Rarity.mythic,
            colors=[Color.black],
            type=CardType.creature,
            quantity=4
        ),
    ])


@pytest.fixture
def izzet_phoenix() -> Deck:
    return Deck(main=[
        Card(
            name='Arclight Phoenix',
            cost=4,
            id=3,
            rarity=Rarity.rare,
            colors=[Color.red],
            type=CardType.creature,
            quantity=4
        ),
    ])


@pytest.fixture
def small_tournament(izzet_phoenix, rakdos_vampires) -> Tournament:
    return Tournament(
        id=1,
        description='Test Tournament',
        format='Pioneer',
        players=[
            TournamentParticipant(name='p2', rank=2, wins=3, losses=0, deck=rakdos_vampires),
            TournamentParticipant(name='p1', rank=1, wins=3, losses=0, deck=izzet_phoenix),
            TournamentParticipant(name='p2', rank=3, wins=0, losses=3, deck=rakdos_vampires),
        ]
    )
