from datetime import datetime

import pytest

from domain import rules
from domain.model import Deck, Card, Rarity, Color, CardType, Tournament, TournamentParticipant, Classifier


@pytest.fixture
def rakdos_vampires() -> Deck:
    return Deck(main=[
        Card(
            name='Vein Ripper',
            cost=6,
            colors=[Color.black],
            type=CardType.creature,
            quantity=4
        ),
        Card(
            name='Sorin, Imperious Bloodlord',
            cost=3,
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
            colors=[Color.red],
            type=CardType.creature,
            quantity=4
        ),
        Card(
            name='Lightning Axe',
            cost=4,
            colors=[Color.red],
            type=CardType.creature,
            quantity=4
        ),
    ])


@pytest.fixture
def amalia_combo() -> Deck:
    return Deck(main=[
        Card(
            name='Amalia Benavides Aguirre',
            cost=3,
            colors=[Color.white, Color.black],
            type=CardType.creature,
            quantity=4
        ),
        Card(
            name='Wildgrowth Walker',
            cost=2,
            colors=[Color.green],
            type=CardType.creature,
            quantity=4
        ),
    ])


@pytest.fixture
def phoenix_tournament(izzet_phoenix) -> Tournament:
    return Tournament(
        id=1,
        description='Test Tournament',
        format='Pioneer',
        players=[
            TournamentParticipant(name='p1', rank=1, wins=3, losses=0, deck=izzet_phoenix),
            TournamentParticipant(name='p1', rank=2, wins=0, losses=3, deck=izzet_phoenix),
        ],
        start_time=datetime.fromisoformat('2024-03-30 10:00:00'),
        link='https://www.mtgo.com/decklist/pioneer-challenge-64-2024-03-3012623703'
    )


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
        ],
        start_time=datetime.fromisoformat('2024-03-29 10:00:00'),
        link='https://www.mtgo.com/decklist/pioneer-challenge-64-2024-03-3012623703'
    )


@pytest.fixture
def old_small_tournament(izzet_phoenix, rakdos_vampires) -> Tournament:
    return Tournament(
        id=1,
        description='Test Tournament',
        format='Pioneer',
        players=[
            TournamentParticipant(name='p2', rank=2, wins=3, losses=0, deck=rakdos_vampires),
            TournamentParticipant(name='p1', rank=1, wins=3, losses=0, deck=izzet_phoenix),
            TournamentParticipant(name='p2', rank=3, wins=0, losses=3, deck=rakdos_vampires),
        ],
        start_time=datetime.fromisoformat('1700-03-29 10:00:00'),
        link='https://www.mtgo.com/decklist/pioneer-challenge-64-2024-03-3012623703'
    )


@pytest.fixture
def medium_tournament(izzet_phoenix, rakdos_vampires, amalia_combo) -> Tournament:
    return Tournament(
        id=1,
        description='Test Tournament',
        format='Pioneer',
        players=[
            TournamentParticipant(name='p1', rank=1, wins=3, losses=0, deck=rakdos_vampires),
            TournamentParticipant(name='p2', rank=2, wins=3, losses=0, deck=izzet_phoenix),
            TournamentParticipant(name='p3', rank=3, wins=2, losses=1, deck=izzet_phoenix),
            TournamentParticipant(name='p4', rank=4, wins=1, losses=2, deck=amalia_combo),
            TournamentParticipant(name='p5', rank=5, wins=0, losses=3, deck=rakdos_vampires),
        ],
        start_time=datetime.fromisoformat('2023-03-30 10:00:00'),
        link='https://www.mtgo.com/decklist/pioneer-challenge-64-2024-03-3012623703'
    )


@pytest.fixture
def classifier() -> Classifier:
    return rules.universal_classifier()
