"""

https://census.daybreakgames.com/s:dgc/get/mtgo/tournament_cover_page?event_id=12628968&c:join=
type:tournament_final_ranking^on:event_id^to:tournamentid^list:1^inject_at:final_rank,
type:tournament_win_loss^on:event_id^to:tournamentid^list:1^inject_at:winloss,
type:tournament_player_count^on:event_id^to:tournamentid^inject_at:player_count,
type:tournament_brackets_by_id^to:tournamentid^on:event_id^rawList:1^inject_at:brackets,
type:qualifying_round_standings^on:event_id^to:tournamentid^list:1^inject_at:standings,
type:tournament_decklist_by_id^on:event_id^to:tournamentid^rawList:1^inject_at:decklists

"""

q1 = """
https://census.daybreakgames.com/s:dgc/get/mtgo/tournament_cover_page?event_id=12628968&c:join=
type:tournament_final_ranking^on:event_id^to:tournamentid^list:1^inject_at:final_rank,
type:qualifying_round_standings^on:event_id^to:tournamentid^list:1^inject_at:standings
"""

"""
type:tournament_win_loss^on:event_id^to:tournamentid^list:1^inject_at:winloss,
type:tournament_player_count^on:event_id^to:tournamentid^inject_at:player_count,
type:tournament_brackets_by_id^to:tournamentid^on:event_id^rawList:1^inject_at:brackets,
type:qualifying_round_standings^on:event_id^to:tournamentid^list:1^inject_at:standings,
type:tournament_decklist_by_id^on:event_id^to:tournamentid^rawList:1^inject_at:decklists
"""

def reassemble(data):
    return data.strip().replace('\n', '')

print(reassemble(q1))
