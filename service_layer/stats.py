from typing import List, Optional

import pydantic

import domain
from adapters.repository import AbstractRepository
from domain import rules, DeckName
from domain.stats import extract_results, ResultHandler


def get_stats(
        repo: AbstractRepository,
        deck: Optional[DeckName] = None,
        cards: Optional[List[str]] = None,
        max_days=14
) -> List[domain.DeckStat]:
    tournaments = list(repo.get_tournament_ids(max_days))
    all_tournaments = [repo.get(t) for t in tournaments]
    results = extract_results(all_tournaments, rules.universal_classifier())
    rh = ResultHandler(results)
    if deck:
        rh.split_deck_by_cards(deck, cards)

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

/* Color for rows */
.dup {
  background-color: #91cd9a;
}

.dnormal {
  background-color: #fffff7;
}

.ddown {
  background-color: #f79c7e;
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
    <th>Archetype</th>
    <th>Play Rate%</th>
    <th>Win Rate%</th>
    <th class="dimiOpt">[Lower, Upper]</th>
    <th class="dimiOpt"># Matches</th>
    <th>Link</th>
  </tr>
</thead>
"""


def _row(n, deck: domain.DeckStat, colorize) -> str:
    row_tag = '  <tr>'
    if deck.win_rate.lower_bound > 50.0:
        color_class = 'dup'
    elif deck.win_rate.upper_bound < 50.0:
        color_class = 'ddown'
    else:
        color_class = 'dnormal'
    if colorize:
        row_tag = f'  <tr class="{color_class}">'
    return f'''{row_tag}
    <td>{n}</td>
    <td>{deck.name}</td>
    <td>{deck.play_rate}</td>
    <td>{deck.win_rate.mean}</td>
    <td class="dimiOpt">[{deck.win_rate.lower_bound}%, {deck.win_rate.upper_bound}%]</td>
    <td class="dimiOpt">{deck.total_matches}</td>
    <td><a href="{deck.example_link}">Deck</a></td>
  </tr>'''


def wrap_html_as_page(body: str):
    """Helper function to get a full html page"""
    return f"""
    <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
        {body}
        </body>
    </html>
    """


def create_html_table(stats: List[domain.DeckStat], colorize: bool) -> str:
    rows = "\n".join([_row(i+1, stat, colorize) for i, stat in enumerate(stats)])
    return HTML_STYLE_HEADER+_table(_head()+_body(rows))


def analyze_deck(deck: DeckName, results: List[domain.Result]) -> domain.DeckAnalysis:
    """
    Analyzes the results of particular deck. For ech card combination played, it tells you how well that
    combination did.
    """
    answer = domain.DeckAnalysis(name=deck, total_wins=0, total_losses=0, cards={})

    highest_wr = 3
    for result in results:
        if result.deck_name != deck:
            continue

        if result.wins > highest_wr:
            highest_wr = result.wins
        answer.total_wins += result.wins
        answer.total_losses += result.losses
        answer.update_cards(result)

    return answer


class Choice(pydantic.BaseModel):
    name: str  # 4x Arclight Phoenix
    win_rate: float  # 49.17 (in percent)
    match_percentage: float  # 80.0 (in percent)
    link: str

    def __str__(self):
        return f'{self.name:40}| {self.win_rate:<10}| {self.match_percentage:<10}| {self.link}'


def display_deck_analysis(analysis: domain.DeckAnalysis):
    """
    Izzet Phoenix, Average Winrate is 49.38%, Loaded 800 Matches

    Card Choice | Win Rate | % of Matches
    =====================================
    4x Arclight Phoenix | 49.38% | 100%
    1x Prismari Command | 50%    | 30%


    """
    deck_wr = round(analysis.total_wins / (analysis.total_losses+analysis.total_wins)*100, 2)
    deck_matches = analysis.total_wins+analysis.total_losses
    title = f'{analysis.name} had an average winrate of {deck_wr}. Loaded {deck_matches} matches.'
    print(title)
    print()
    print(f'{"Card Choice":40}| {"Win Rate":<10}| % of Matches')

    choices: list[Choice] = []

    for card, item in analysis.cards.items():
        card_choice = f'{card[0]}x {card[1]}'
        wr = round(item.total_wins/(item.total_wins+item.total_losses)*100, 2)
        match_percentage = round((item.total_wins+item.total_losses)/deck_matches*100, 2)
        choices.append(Choice(name=card_choice, win_rate=wr, match_percentage=match_percentage, link=item.example_link))

    choices.sort(key=lambda x: x.win_rate, reverse=True)
    for choice in choices:
        if choice.match_percentage >= 10:
            print(choice)


def calculate_competition_score(repo: AbstractRepository, max_days=21) -> domain.CompetitionScoreListing:
    tournament_ids = repo.get_tournament_ids(max_days)
    raw_tournaments = [repo.get(id_) for id_ in tournament_ids]
    classifier = rules.universal_classifier()
    tournaments = [domain.ClassifiedTournament.from_tournament(t, classifier) for t in raw_tournaments]
    return domain.CompetitionScoreListing.from_tournaments(tournaments)
