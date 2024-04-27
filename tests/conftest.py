from datetime import datetime

import pytest
import domain
import domain.rules

@pytest.fixture
def rakdos_vampires() -> domain.Deck:
    return domain.Deck(main=[
        domain.Card(
            name='Vein Ripper',
            cost=6,
            colors=[domain.Color.black],
            type=domain.CardType.creature,
            quantity=4
        ),
        domain.Card(
            name='Sorin, Imperious Bloodlord',
            cost=3,
            colors=[domain.Color.black],
            type=domain.CardType.creature,
            quantity=4
        ),
    ])


@pytest.fixture
def izzet_phoenix() -> domain.Deck:
    return domain.Deck(main=[
        domain.Card(
            name='Arclight Phoenix',
            cost=4,
            colors=[domain.Color.red],
            type=domain.CardType.creature,
            quantity=4
        ),
        domain.Card(
            name='Lightning Axe',
            cost=4,
            colors=[domain.Color.red],
            type=domain.CardType.creature,
            quantity=4
        ),
    ])


@pytest.fixture
def amalia_combo() -> domain.Deck:
    return domain.Deck(main=[
        domain.Card(
            name='Amalia Benavides Aguirre',
            cost=3,
            colors=[domain.Color.white, domain.Color.black],
            type=domain.CardType.creature,
            quantity=4
        ),
        domain.Card(
            name='Wildgrowth Walker',
            cost=2,
            colors=[domain.Color.green],
            type=domain.CardType.creature,
            quantity=4
        ),
    ])


@pytest.fixture
def phoenix_tournament(izzet_phoenix) -> domain.Tournament:
    return domain.Tournament(
        id=1,
        description='Test domain.Tournament',
        format='Pioneer',
        players=[
            domain.TournamentParticipant(name='p1', rank=1, wins=3, losses=0, deck=izzet_phoenix),
            domain.TournamentParticipant(name='p1', rank=2, wins=0, losses=3, deck=izzet_phoenix),
        ],
        start_time=datetime.fromisoformat('2024-03-30 10:00:00'),
        link='https://www.mtgo.com/decklist/pioneer-challenge-64-2024-03-3012623703'
    )


@pytest.fixture
def small_tournament(izzet_phoenix, rakdos_vampires) -> domain.Tournament:
    return domain.Tournament(
        id=1,
        description='Test domain.Tournament',
        format='Pioneer',
        players=[
            domain.TournamentParticipant(name='p2', rank=2, wins=3, losses=0, deck=rakdos_vampires),
            domain.TournamentParticipant(name='p1', rank=1, wins=3, losses=0, deck=izzet_phoenix),
            domain.TournamentParticipant(name='p2', rank=3, wins=0, losses=3, deck=rakdos_vampires),
        ],
        start_time=datetime.fromisoformat('2024-03-29 10:00:00'),
        link='https://www.mtgo.com/decklist/pioneer-challenge-64-2024-03-3012623703'
    )


@pytest.fixture
def old_small_tournament(izzet_phoenix, rakdos_vampires) -> domain.Tournament:
    return domain.Tournament(
        id=1,
        description='Test domain.Tournament',
        format='Pioneer',
        players=[
            domain.TournamentParticipant(name='p2', rank=2, wins=3, losses=0, deck=rakdos_vampires),
            domain.TournamentParticipant(name='p1', rank=1, wins=3, losses=0, deck=izzet_phoenix),
            domain.TournamentParticipant(name='p2', rank=3, wins=0, losses=3, deck=rakdos_vampires),
        ],
        start_time=datetime.fromisoformat('1700-03-29 10:00:00'),
        link='https://www.mtgo.com/decklist/pioneer-challenge-64-2024-03-3012623703'
    )


@pytest.fixture
def medium_tournament(izzet_phoenix, rakdos_vampires, amalia_combo) -> domain.Tournament:
    return domain.Tournament(
        id=1,
        description='Test domain.Tournament',
        format='Pioneer',
        players=[
            domain.TournamentParticipant(name='p1', rank=1, wins=3, losses=0, deck=rakdos_vampires),
            domain.TournamentParticipant(name='p2', rank=2, wins=3, losses=0, deck=izzet_phoenix),
            domain.TournamentParticipant(name='p3', rank=3, wins=2, losses=1, deck=izzet_phoenix),
            domain.TournamentParticipant(name='p4', rank=4, wins=1, losses=2, deck=amalia_combo),
            domain.TournamentParticipant(name='p5', rank=5, wins=0, losses=3, deck=rakdos_vampires),
        ],
        start_time=datetime.fromisoformat('2023-03-30 10:00:00'),
        link='https://www.mtgo.com/decklist/pioneer-challenge-64-2024-03-3012623703'
    )


@pytest.fixture
def izzet_phoenix_result(izzet_phoenix: domain.Deck) -> domain.Result:
    return domain.Result(
        deck=izzet_phoenix,
        deck_name=domain.DeckName('Izzet Phoenix'),
        wins=3,
        losses=0,
        date=datetime.fromisoformat('2023-03-30 10:00:00')
    )


@pytest.fixture
def rakdos_vampires_result(rakdos_vampires: domain.Deck) -> domain.Result:
    return domain.Result(
        deck=rakdos_vampires,
        deck_name=domain.DeckName('Rakdos Vampires'),
        wins=1,
        losses=1,
        date=datetime.fromisoformat('2023-03-30 10:00:00')
    )


@pytest.fixture
def classifier() -> domain.Classifier:
    return domain.Classifier([
        domain.rules.SimpleRule('Izzet Phoenix', ['Arclight Phoenix']),
        domain.rules.SimpleRule('Rakdos Vampires', ['Vein Ripper']),
    ])
