"""

https://census.daybreakgames.com/s:dgc/get/mtgo/tournament_cover_page?event_id=12623669&c:join=type:tournament_final_ranking^on:event_id^to:tournamentid^list:1^inject_at:final_rank,type:tournament_win_loss^on:event_id^to:tournamentid^list:1^inject_at:winloss,type:tournament_player_count^on:event_id^to:tournamentid^inject_at:player_count,type:tournament_brackets_by_id^to:tournamentid^on:event_id^rawList:1^inject_at:brackets,type:qualifying_round_standings^on:event_id^to:tournamentid^list:1^inject_at:standings,type:tournament_decklist_by_id^on:event_id^to:tournamentid^rawList:1^inject_at:decklists


get decklists
https://census.daybreakgames.com/s:dgc/get/global/game_server_status?game_code=mtgo&c:limit=1000


https://www.mtgo.com/decklists?filter=Pioneer
--> get html containing lots of class="decklists-link"
like               "/decklist/pioneer-preliminary-2024-03-2812623669"
https://www.mtgo.com/decklist/pioneer-preliminary-2024-03-2812623669

from there we somehow make a request to

https://census.daybreakgames.com/s:dgc/get/mtgo/tournament_cover_page?event_id=12623669&c:join=type:tournament_final_ranking^on:event_id^to:tournamentid^list:1^inject_at:final_rank,type:tournament_win_loss^on:event_id^to:tournamentid^list:1^inject_at:winloss,type:tournament_player_count^on:event_id^to:tournamentid^inject_at:player_count,type:tournament_brackets_by_id^to:tournamentid^on:event_id^rawList:1^inject_at:brackets,type:qualifying_round_standings^on:event_id^to:tournamentid^list:1^inject_at:standings,type:tournament_decklist_by_id^on:event_id^to:tournamentid^rawList:1^inject_at:decklists


"""

import requests
from bs4 import BeautifulSoup


def fetch_mtgo_urls():
    url = "https://www.mtgo.com/decklists"
    data = requests.get(url).text
    soup = BeautifulSoup(data, features='html.parser')
    decklists = [decklist.get('href') for decklist in soup.find_all(class_='decklists-link')]
    return ['https://www.mtgo.com'+decklist for decklist in decklists if 'pioneer' in decklist]


def fetch_tournament(mtgo_url: str) -> dict:
    """
    url like https://www.mtgo.com/decklist/pioneer-preliminary-2024-03-2812623669
    :param mtgo_url:
    :return:
    """
    query_base = 'https://census.daybreakgames.com/'
    r = requests.get(mtgo_url)
    url = None
    for line in r.text.split('\n'):
        if 'window.MTGO.decklists.query' in line:
            url = query_base + line.strip().split(' = ')[1].strip("'").strip("';")
    if url is None:
        raise NotImplementedError
    else:
        return requests.get(url).json()


if __name__ == '__main__':
    tournament_urls = fetch_mtgo_urls()[:5]
    for url in tournament_urls:
        tournament = fetch_tournament(url)
        print(f'fetched tournament with {tournament["tournament_cover_page_list"][0]["player_count"]["players"]} players')
