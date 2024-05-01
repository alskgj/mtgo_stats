import domain
import service_layer
from domain.stats import ResultHandler
from service_layer import stats


def test_win_rate_calculations(izzet_phoenix_result, rakdos_vampires_result):
    assert ResultHandler.calculate_win_rate([izzet_phoenix_result]).mean == 100.0
    assert ResultHandler.calculate_win_rate([rakdos_vampires_result]).mean == 50.0

    # 3 izzet phoenix wins, 1 rakdos vampire win, 1 rakdos vampire loss --> 80% WR
    assert ResultHandler.calculate_win_rate([izzet_phoenix_result, rakdos_vampires_result]).mean == 80.0


def test_play_rate_calculations(izzet_phoenix_result, rakdos_vampires_result):
    rh = ResultHandler([izzet_phoenix_result, rakdos_vampires_result])
    assert rh.calculate_play_rate(izzet_phoenix_result.deck_name) == 50.0
    assert rh.calculate_play_rate(rakdos_vampires_result.deck_name) == 50.0


def test_html_table():
    izzet_phoenix = domain.DeckStat(
        name=domain.DeckName('Izzet Phoenix'),
        win_rate=domain.WinRate(mean=47.94, lower_bound=44.54, upper_bound=51.35),
        play_rate=9.1,
        total_matches=800,
        example_link='https://www.mtgo.com/decklist/pioneer-challenge-32-2024-04-2612633733#deck_Hexapuss'
    )
    spirits = domain.DeckStat(
        name=domain.DeckName('Spirits'),
        win_rate=domain.WinRate(mean=57.6, lower_bound=50.95, upper_bound=63.99),
        play_rate=2.69,
        total_matches=80,
        example_link='https://www.mtgo.com/decklist/pioneer-challenge-32-2024-04-2612633733#deck_remf'
    )
    result = service_layer.stats.create_html_table([izzet_phoenix, spirits], colorize=False)
    expected = """
<style>
.dimiTable {
  width: 100%;
  font-size: 18px;
  border: 2px solid black;
}

.dimiTable th {
  border: 2px solid black;
  background-color: #f1c147;
}

/* tablets and smaller -> hide confidence interval + matches */
@media all and (max-width: 800px) {

  td.dimiOpt,
  th.dimiOpt {
    display: none;
    visibility: collapse;
  }
}

/* small devices */
@media all and (max-width: 500px) {
  .dimiTable {
    font-size: 12px;

  }
}

/* tiny devices */
@media all and (max-width: 300px) {
  .dimiTable {
    font-size: 10px;
  }
}

/* Color for rows */
.dup {
  background-color: #91cd9a;
}

.dnormal {
  background-color: #f3e1e4;
}

.ddown {
  background-color: #f79c7e;
}
</style>
<table class="dimiTable">
<thead>
  <tr>
    <th>#</th>
    <th>Archetype</th>
    <th>Play Rate%</th>
    <th>Win Rate%</th>
    <th class="dimiOpt">[Lower, Upper]</th>
    <th class="dimiOpt"># Matches</th>
    <th>Link</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>1</td>
    <td>Izzet Phoenix</td>
    <td>9.1</td>
    <td>47.94</td>
    <td class="dimiOpt">[44.54%, 51.35%]</td>
    <td class="dimiOpt">800</td>
    <td><a href="https://www.mtgo.com/decklist/pioneer-challenge-32-2024-04-2612633733#deck_Hexapuss">Deck</a></td>
  </tr>
  <tr>
    <td>2</td>
    <td>Spirits</td>
    <td>2.69</td>
    <td>57.6</td>
    <td class="dimiOpt">[50.95%, 63.99%]</td>
    <td class="dimiOpt">80</td>
    <td><a href="https://www.mtgo.com/decklist/pioneer-challenge-32-2024-04-2612633733#deck_remf">Deck</a></td>
  </tr>
</tbody>
</table>
    """.strip()

    assert result == expected


def test_extract_results(phoenix_tournament, classifier):
    result = stats.extract_results([phoenix_tournament], classifier)
    expected = f'{phoenix_tournament.link}#deck_{phoenix_tournament.players[0].name}'
    assert expected == result[0].link
