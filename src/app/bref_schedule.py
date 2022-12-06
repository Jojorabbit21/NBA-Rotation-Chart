import pandas as pd
import numpy as np
np.set_printoptions(suppress=True, formatter={'float_kind':'{:f}'.format})
import requests
import re
import os
import sys
import math
sys.path.append('.')
import datetime
from time import sleep
from bs4 import BeautifulSoup
from unidecode import unidecode

base_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Connection': 'keep-alive',
    'X-Frame-Options': 'SAMEORIGIN',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.basketball-reference.com/'
}

full_to_abbr = {
    'Atlanta Hawks': 'ATL',
    'Boston Celtics': 'BOS',
    'Brooklyn Nets': 'BKN',
    'Charlotte Hornets': 'CHA',
    'Cleveland Cavaliers': 'CLE',
    'Chicago Bulls': 'CHI',
    'Dallas Mavericks': 'DAL',
    'Denver Nuggets': 'DEN',
    'Detroit Pistons': 'DET',
    'Golden State Warriors': 'GSW',
    'Houston Rockets': 'HOU',
    'Indiana Pacers': 'IND',
    'Los Angeles Clippers': 'LAC',
    'Los Angeles Lakers': 'LAL',
    'Memphis Grizzlies': 'MEM',
    'Miami Heat': 'MIA',
    'Milwaukee Bucks': 'MIL',
    'Minnesota Timberwolves': 'MIN',
    'New Orleans Pelicans': 'NOP',
    'New York Knicks': 'NYK',
    'Oklahoma City Thunder': 'OKC',
    'Orlando Magic': 'ORL',
    'Philadelphia 76ers': 'PHI',
    'Phoenix Suns': 'PHO',
    'Portland Trail Blazers': 'POR',
    'Sacramento Kings': 'SAC',
    'San Antonio Spurs': 'SAS',
    'Toronto Raptors': 'TOR',
    'Utah Jazz': 'UTA',
    'Washington Wizards': 'WAS'
}

def load_player_list():
    return pd.read_csv('src/data/static/players_bref.csv')

def get_player_info(playername:str):
    player_list = load_player_list()
    playername = unidecode(playername)
    search = player_list[player_list['Player'] == playername]
    # if len(search) > 1:
    #     raise ValueError('Too many results.')
    return search

def calculate_minutes(data, playerinfo, match_info:list):
    player_name = playerinfo.loc[:, "Player"].item()
    
    date = match_info[0]
    team = match_info[1]
    against = match_info[2]
    
    arr_mp = data['MinutesPlayed'].to_numpy(dtype=np.float64)
    arr_io = data['Status'].to_numpy(dtype=np.int32)    
    
    # Integrate consecutive playing times
    for _, i in enumerate(arr_mp):
        if _ < len(arr_mp) - 1:
            if arr_io[_] == arr_io[_+1]:
                arr_mp[_] = arr_mp[_] + arr_mp[_ + 1]
                arr_mp = np.delete(arr_mp, _+1)
                arr_io = np.delete(arr_io, _+1)
    
    # Convert to stacked-timestamp
    for _, i in enumerate(arr_mp):
        if _ < len(arr_mp) - 1:
            a = datetime.timedelta(seconds=round(i,0))
            m = (a.seconds // 60) % 60
            s = a.seconds - (m * 60)
            arr_mp[_] = a.seconds
    for _, i in enumerate(arr_mp):
        if _ < len(arr_mp) - 1:
            arr_mp[_ + 1] += i
            
    # Sanitize Extra/Short time 
    if arr_mp[-1] > 2880:
        extra = arr_mp[-1] - 2880
        arr_mp[-1] = arr_mp[-1] - extra
    elif arr_mp[-1] < 2880:
        need = 2880 - arr_mp[-1]
        arr_mp[-1] = arr_mp[-1] + need
        
    # time = []
    # for i in arr_mp:
    #     a = datetime.timedelta(seconds=i)
    #     time.append(str(a))
    # print(time)
    
    min_arr = np.zeros(shape=(49,))
    min_count = 0
    for _, i in enumerate(arr_mp):
        if _ == 0:
            duration = datetime.timedelta(seconds=i)
            duration_m = (duration.seconds // 60) % 60
            duration_s = duration.seconds - (duration_m * 60)
            # print(f'({arr_io[_]}) 0:00:00 ~ {str(duration)} / {str(duration)} play/rest')
            if arr_io[_] == 1:
                for tick in range(0, duration_m):
                    min_arr[tick] = 60
            if duration_s > 0:
                min_arr[duration_m] = duration_s
                min_count = duration_m
            else:
                min_count = duration_m - 1
        else:
            last_pos = min_count
            duration = datetime.timedelta(seconds= i - arr_mp[_-1])
            duration_m = (duration.seconds // 60) % 60
            duration_s = duration.seconds - (duration_m * 60)
            start = datetime.timedelta(seconds=arr_mp[_-1])
            if min_arr[last_pos] > 0: # when float exist
                x = 60 - min_arr[last_pos] # need to fill up rest of minute
                if x > duration_s:
                    duration_s = 60 - (x - duration_s)
                    duration_m -= 1
                elif x == duration_s:
                    duration_s = 0 
                elif x < duration_s:
                    duration_s = duration_s - x
                if arr_io[_] == 1:
                    min_arr[last_pos] = 60 - min_arr[last_pos]
            last_pos += 1
            for tick in range(last_pos, (last_pos + duration_m)):
                if arr_io[_] == 1:
                    min_arr[tick] = 60
                # else:
                #     min_arr[tick] = 0
            # print(f'({arr_io[_]}) {str(start)} ~ {str(duration + start)} / {str(duration)} play/rest')
            if _ < len(arr_mp) - 1:
                if duration_s > 0:
                    min_arr[last_pos + duration_m] = duration_s
                    min_count += (duration_m + 1)
                else:
                    min_count += duration_m
        # print(min_arr)
    min_arr = np.delete(min_arr, -1)
    
    def fun(e):
        return e / 60
    
    vectorize = np.vectorize(fun)
    min_arr = vectorize(min_arr)
    
    m_info = [player_name, date, team, against]
    m_df = pd.DataFrame([m_info], columns=['PlayerName', 'Date', 'Team', 'Opp'])
    df = pd.DataFrame([min_arr])
    df = pd.concat([m_df, df], axis=1)
    
    parent = f'src/data/teamdashplayers/'
    if os.path.isdir(parent + str(player_name)):
        df.to_csv(parent + str(player_name) + "/" + f'{player_name}.csv', mode='a', header=None)
    else:
        os.mkdir(parent + str(player_name))
        df.to_csv(parent + str(player_name) +  "/" +  f'{player_name}.csv', mode='w')
            
def bref_scrape_schedule(seasons:list=[2022]):
    base_url = 'https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html' # ex) 2023 => 2022-23
    boxscore_url = []
    for season in seasons:
        if season == 2020:
            months = [
            'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june', 'july', 'october-2020'
            ]
        else:
            months = [
            'october', 'november', 'december', 'january', 'february', 'march', 'april', 'may', 'june', 'july'
            ]
        for month in months:
            sleep(1)
            url = base_url.format(season, month)
            print(url)
            response = requests.get(url=url, headers=base_header)
            if response.status_code == 200:
                html = response.text
                soup = BeautifulSoup(html, 'lxml')
                table = soup.select_one('table#schedule')
                boxscores = table.select("tbody > tr > td:nth-child(7) > a")
                for boxscore in boxscores:
                    boxscore_url.append(boxscore['href'])
                print(f'{len(boxscores)} games fetched.')
            else:
                print('no datas fetched')
                print(response.status_code)
    fetched = pd.DataFrame(0, index=np.zeros(shape=(len(boxscore_url), )), columns=['fetched'])
    df = pd.DataFrame(data=boxscore_url, columns=['boxscore_url'])
    df = pd.concat([df, fetched], axis=1)
    season = f'{int(season)-1}{season[-2:]}'
    df.to_csv(f'src/data/schedules/bref_{season}.csv')

def bref_scrape_chart(url:str, season):
    response = requests.get(url, headers=base_header)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    
    date = url.split('/')[-1:][0]
    date = re.findall("[0-9]", date)
    date = "".join(date)
    away_team = full_to_abbr[soup.select_one('#content > div.scorebox > div:nth-child(1) > div:nth-child(1) > strong > a').text]
    home_team = full_to_abbr[soup.select_one('#content > div.scorebox > div:nth-child(2) > div:nth-child(1) > strong > a').text]
    filename = f'{date}_{away_team}@{home_team}'
    
    table = soup.select_one('#content > div.plusminus > div')
    table_width = re.findall("\W([0-9]*)\w", table['style'])[0]

    away_table = soup.select_one('#content > div.plusminus > div > div:nth-child(1)')
    home_table = soup.select_one('#content > div.plusminus > div > div:nth-child(2)')

    away_player = away_table.select('div.player')
    away_bar = away_table.select('div.player-plusminus')
    home_player = home_table.select('div.player')
    home_bar = home_table.select('div.player-plusminus')

    away_length = len(away_player)
    print('Creating Away Players timetable...')
    for idx in range(0, away_length):
        player_name = re.findall("(.*)\s\(", away_player[idx].text)[0]
        print(player_name)
        player_info = get_player_info(player_name)
        bars = away_bar[idx].select('div')
        actual_width = int(table_width) - 1
        status = np.zeros(shape=(len(bars),), dtype=np.int16)
        minute = np.zeros(shape=(len(bars),), dtype=np.float64)
        margin = np.zeros(shape=(len(bars),), dtype=np.int16)
        for i, rows in enumerate(bars):
            if rows['style'][0] != 'width:-1px;':
                time_width = int(re.findall("\W([0-9]*)\w",rows['style'])[0]) + 1
                actual_minute = time_width / actual_width
                actual_minute = round(2880 * actual_minute, 1)
                try:
                    if rows['class'][0] == 'minus' or rows['class'][0] == 'plus' or rows['class'][0] == 'even':
                        status[i] = 1
                        margin[i] = int(rows.text)
                except:
                        status[i] = 0
                        margin[i] = 0
                finally:
                    minute[i] = actual_minute
        df = pd.DataFrame(data=[
            minute, 
            # margin, 
            status
            ])
        df = df.T
        df.columns = [
            'MinutesPlayed', 
            # 'ScoreMargin', 
            'Status'
            ]        
        if not os.path.isdir(f'src/data/boxscores/{season}'):
            os.mkdir(f'src/data/boxscores/{season}')
        if not os.path.isdir(f'src/data/boxscores/{season}/{filename}'):
            os.mkdir(f'src/data/boxscores/{season}/{filename}')
        if not os.path.isdir(f'src/data/boxscores/{season}/{filename}/{away_team}'):
            os.mkdir(f'src/data/boxscores/{season}/{filename}/{away_team}')
        df.to_csv(f'src/data/boxscores/{season}/{filename}/{away_team}/{player_name}.csv')
        match_info = [date, away_team, home_team]
        calculate_minutes(df, player_info, match_info)
        
    home_length = len(home_player)
    print('Creating Home Players timetable...')
    for idx in range(0, home_length):
        player_name = re.findall("(.*)\s\(", home_player[idx].text)[0]
        print(player_name)
        player_info = get_player_info(player_name)
        bars = home_bar[idx].select('div')
        actual_width = int(table_width) - 1
        status = np.zeros(shape=(len(bars),), dtype=np.int16)
        minute = np.zeros(shape=(len(bars),), dtype=np.float64)
        margin = np.zeros(shape=(len(bars),), dtype=np.int16)
        for i, rows in enumerate(bars):
            if rows['style'][0] != 'width:-1px;':
                time_width = int(re.findall("\W([0-9]*)\w",rows['style'])[0]) + 1
                actual_minute = time_width / actual_width
                actual_minute = round(2880 * actual_minute, 1)
                try:
                    if rows['class'][0] == 'minus' or rows['class'][0] == 'plus':
                        status[i] = 1
                        margin[i] = int(rows.text)
                except:
                        status[i] = 0
                        margin[i] = 0
                finally:
                    minute[i] = actual_minute
        df = pd.DataFrame(data=[
            minute, 
            # margin, 
            status
            ])
        df = df.T
        df.columns = [
            'MinutesPlayed', 
            # 'ScoreMargin', 
            'Status'
            ]
    
        if not os.path.isdir(f'src/data/boxscores/{season}'):
            os.mkdir(f'src/data/boxscores/{season}')
        if not os.path.isdir(f'src/data/boxscores/{season}/{filename}'):
            os.mkdir(f'src/data/boxscores/{season}/{filename}')
        if not os.path.isdir(f'src/data/boxscores/{season}/{filename}/{home_team}'):
            os.mkdir(f'src/data/boxscores/{season}/{filename}/{home_team}')
        df.to_csv(f'src/data/boxscores/{season}/{filename}/{home_team}/{player_name}.csv')
        match_info = [date, home_team, away_team]
        calculate_minutes(df, player_info, match_info)



# For test
# bref_scrape_chart('https://www.basketball-reference.com/boxscores/plus-minus/202110200DET.html', '202223')

season = '202122'
bref_base = 'https://www.basketball-reference.com/boxscores/plus-minus/'
filepath = 'src/data/schedules/bref.com/'
filelist = os.listdir(filepath)
for file in filelist:
    df = pd.read_csv(filepath + file)
    for row in df.itertuples():
        if row.fetched == 0:
            boxscore_url = str(row.boxscore_url).split("/")[-1]
            url = bref_base + boxscore_url
            print(url)
            bref_scrape_chart(url=url, season=season)
            df.iloc[row.Index, -1] = 1
            df.to_csv(filepath + file, index=False)
            sleep(1.5)

# ---------* Sanitize BBref player list names  
# player_list = pd.read_csv('src/data/static/players_bref.csv')
# for row in player_list.itertuples():
#     name = unidecode(row.Player)
#     player_list.iloc[row.Index, 0] = name
# player_list.to_csv('src/data/static/players_bref.csv')