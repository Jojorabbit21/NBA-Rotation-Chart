import pandas as pd
import numpy as np

import requests
import json
import os

from nba_api.stats.endpoints.boxscoretraditionalv2 import BoxScoreTraditionalV2
from nba_api.stats.endpoints.boxscoreadvancedv2 import BoxScoreAdvancedV2
from nba_api.stats.endpoints.boxscorescoringv2 import BoxScoreScoringV2
from nba_api.stats.endpoints.boxscoredefensive import BoxScoreDefensive
from nba_api.stats.endpoints.boxscorefourfactorsv2 import BoxScoreFourFactorsV2
from nba_api.stats.endpoints.boxscorematchups import BoxScoreMatchups
from nba_api.stats.endpoints.boxscoreplayertrackv2 import BoxScorePlayerTrackV2
from nba_api.stats.endpoints.boxscoremiscv2 import BoxScoreMiscV2
from nba_api.stats.endpoints.boxscoreusagev2 import BoxScoreUsageV2
from nba_api.stats.endpoints.boxscoresummaryv2 import BoxScoreSummaryV2

headers={
    'Accept': 'application/json, text/plain, */*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Connection': 'keep-alive',
    'Host': 'stats.nba.com',
    'Origin': 'https://www.nba.com',
    'Referer': 'https://www.nba.com/',
    'sec-ch-ua': '"Google Chrome";v="87", "\"Not;A\\Brand";v="99", "Chromium";v="87"',
    'sec-ch-ua-mobile': '?1',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-site',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Mobile Safari/537.36',
    'x-nba-stats-origin': 'stats',
    'x-nba-stats-token': 'true'
}

def get_season_schedule(seasons:list=[2021]):
    for season in seasons:
        schedule = f'https://data.nba.net/prod/v1/{season}/schedule.json'
        r = requests.get(schedule)
        j = r.json()

        with open(f'src/raw/schedule_{season}.json', 'w') as file:
            json.dump(j, file, indent=4)

def convert_schedule(seasons:list=[2021]):
    fp = 'src/raw/'
    for season in seasons:
        # Open JSON file
        with open(fp + f'schedule_{season}.json', 'r') as file:
            f = json.load(file)
        f = f['league']['standard']

        columns = [
            'gameId', 'date', 'time', 'hId', 'hScore', 'vId', 'vScore'
        ]
        
        df = pd.DataFrame(0, index=np.arange(len(f)), columns=columns)
        
        for idx, match in enumerate(f):
            df.iloc[idx, 0] = match['gameId']
            df.iloc[idx, 1] = match['startDateEastern']   
            df.iloc[idx, 2] = match['startTimeEastern']      
            df.iloc[idx, 3] = match['hTeam']['teamId']     
            df.iloc[idx, 4] = match['hTeam']['score']    
            df.iloc[idx, 5] = match['vTeam']['teamId']     
            df.iloc[idx, 6] = match['vTeam']['score'] 
        
        df.to_csv(f'src/data/schedules/{season}.csv')
        
        
def get_boxscores(seasons:list=[2021]):
    fp = 'src/data/schedules'
    for season in seasons:
        # Load CSV File
        df = pd.read_csv(fp + f'/{season}.csv')
        
        # Iterate dataframes
        for row in df.itertuples():
            print('gameid : ',row.gameId)
            # Create folder when It doesn't exist.
            fp = f'src/data/boxscores/{row.gameId}'
            if not os.path.isdir(f'src/data/boxscores/{row.gameId}'):
                os.mkdir(fp)
                os.mkdir(fp + '/players')
                os.mkdir(fp + '/team')

            # Fetch Boxscores
            trad = BoxScoreTraditionalV2(game_id=row.gameId, headers=headers).get_data_frames()
            adv = BoxScoreAdvancedV2(game_id=row.gameId, headers=headers).get_data_frames()
            score = BoxScoreScoringV2(game_id=row.gameId, headers=headers).get_data_frames()
            defs = BoxScoreDefensive(game_id=row.gameId, headers=headers).get_data_frames()
            four = BoxScoreFourFactorsV2(game_id=row.gameId, headers=headers).get_data_frames()
            matchup = BoxScoreMatchups(game_id=row.gameId, headers=headers).get_data_frames()
            track = BoxScorePlayerTrackV2(game_id=row.gameId, headers=headers).get_data_frames()
            misc = BoxScoreMiscV2(game_id=row.gameId, headers=headers).get_data_frames()
            usage = BoxScoreUsageV2(game_id=row.gameId, headers=headers).get_data_frames()
            summ = BoxScoreSummaryV2(game_id=row.gameId, headers=headers).get_data_frames()
            
            # Save to .csv
            trad[0].to_csv(fp + '/players/01_traditional.csv')
            trad[1].to_csv(fp + '/team/01_traditional.csv')
            adv[0].to_csv(fp + '/players/02_advanced.csv')
            adv[1].to_csv(fp + '/team/02_advanced.csv')
            score[0].to_csv(fp + '/players/03_scoring.csv')
            score[1].to_csv(fp + '/team/03_scoring.csv')
            defs[0].to_csv(fp + '/players/04_defense.csv')
            defs[1].to_csv(fp + '/team/04_defense.csv')
            four[0].to_csv(fp + '/players/05_fourfactor.csv')
            four[1].to_csv(fp + '/team/05_fourfactor.csv')
            matchup[0].to_csv(fp + '/players/06_matchup.csv')
            matchup[1].to_csv(fp + '/team/06_matchup.csv')
            track[0].to_csv(fp + '/players/07_tracking.csv')
            track[1].to_csv(fp + '/team/07_tracking.csv')
            misc[0].to_csv(fp + '/players/08_misc.csv')
            misc[1].to_csv(fp + '/team/08_misc.csv')
            usage[0].to_csv(fp + '/players/09_usage.csv')
            usage[1].to_csv(fp + '/team/09_usage.csv')
            summ[0].to_csv(fp + '/players/10_summary.csv')
            summ[1].to_csv(fp + '/team/10_summary.csv')

        
        
        
        
        
# Actual Process  
# get_boxscores()

df = BoxScoreTraditionalV2(game_id='12100001', headers=headers).get_normalized_dict()
print(df)