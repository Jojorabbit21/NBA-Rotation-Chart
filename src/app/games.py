import pandas as pd

from nba_api.stats.endpoints.leaguegamelog import LeagueGameLog

df = LeagueGameLog(season='2021-22').get_data_frames()[0]
print(df)