from typing import List

import domain
from adapters.repository import AbstractRepository
from domain import rules
from domain.stats import extract_results, ResultHandler


def get_stats(repo: AbstractRepository, max_days=14) -> List[domain.DeckStat]:
    tournaments = list(repo.get_tournament_ids(max_days))
    all_tournaments = [repo.get(t) for t in tournaments]
    results = extract_results(all_tournaments, rules.universal_classifier())
    rh = ResultHandler(results)

    # display stats
    return rh.fetch_stats()


HTML_STYLE_HEADER = """<style>
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
</style>
"""


def _table(data: str):
    return '<table class="dimiTable">\n' + data + '\n</table>'


def _body(data: str):
    return '<tbody>\n' + data + '\n</tbody>'


def _head():
    return """<thead>
  <tr>
    <th>#</th>
    <th>Deck</th>
    <th>Play Rate%</th>
    <th>Win Rate%</th>
    <th class="dimiOpt">[Lower, Upper]</th>
    <th class="dimiOpt"># Matches</th>
  </tr>
</thead>
"""


def _row(n, deck: domain.DeckStat) -> str:
    return f'''  <tr>
    <td>{n}</td>
    <td>{deck.name}</td>
    <td>{deck.play_rate}</td>
    <td>{deck.win_rate.mean}</td>
    <td class="dimiOpt">[{deck.win_rate.lower_bound}%, {deck.win_rate.upper_bound}%]</td>
    <td class="dimiOpt">{deck.total_matches}</td>
  </tr>'''


def create_html_table(stats: List[domain.DeckStat]) -> str:
    rows = "\n".join([_row(i+1, stat) for i, stat in enumerate(stats)])
    return HTML_STYLE_HEADER+_table(_head()+_body(rows))
