from domain.stats import ResultHandler


def test_win_rate_calculations(izzet_phoenix_result, rakdos_vampires_result):
    assert ResultHandler.calculate_win_rate([izzet_phoenix_result]).mean == 100.0
    assert ResultHandler.calculate_win_rate([rakdos_vampires_result]).mean == 50.0

    # 3 izzet phoenix wins, 1 rakdos vampire win, 1 rakdos vampire loss --> 80% WR
    assert ResultHandler.calculate_win_rate([izzet_phoenix_result, rakdos_vampires_result]).mean == 80.0


def test_play_rate_calculations(izzet_phoenix_result, rakdos_vampires_result):
    rh = ResultHandler([izzet_phoenix_result, rakdos_vampires_result])
    assert rh.calculate_play_rate(izzet_phoenix_result.deck_name) == 50.0
    assert rh.calculate_play_rate(rakdos_vampires_result.deck_name) == 50.0
