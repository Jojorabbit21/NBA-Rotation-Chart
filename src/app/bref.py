import pandas as pd
import numpy as np
np.set_printoptions(suppress=True, formatter={'float_kind':'{:f}'.format})
import requests
import re
import os
import sys
import math
import sqlite3
sys.path.append('.')
import datetime
from time import sleep
from bs4 import BeautifulSoup
from unidecode import unidecode
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns

base_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Connection': 'keep-alive',
    'X-Frame-Options': 'SAMEORIGIN',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-US,en;q=0.9',
    'Referer': 'https://www.basketball-reference.com/'
}

team_list_bref = [
    'ATL', 
    'BOS', 
    'BRK', 
    'CHO', 
    'CLE', 
    'CHI', 
    'DAL', 
    'DEN', 
    'DET',
    'GSW', 
    'HOU', 
    'IND', 
    'LAC', 
    'LAL', 
    'MEM', 
    'MIA', 
    'MIL', 
    'MIN', 
    'NOP',
    'NYK', 
    'OKC', 
    'ORL', 
    'PHI', 
    'PHO', 
    'POR', 
    'SAC', 
    'SAS', 
    'TOR', 
    'UTA', 
    'WAS'
]

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

def open_db(dbname):
    db_path = f'src/data/db/{dbname}.sqlite3'
    conn = sqlite3.connect(db_path)
    return conn

def load_player_list():
    cur = open_db('static')
    df = pd.read_sql('SELECT * FROM players_bref', cur)
    return df

def get_player_info(playername:str, season:str):
    player_list = load_player_list()
    if 'Jr.' in playername or 'Sr.' in playername:
        playername = playername.replace('.', '')
    playername = unidecode(playername)
    search = player_list[(player_list['Player'] == playername) & (player_list['To'] >= int(season))]
    # if len(search) > 1:
    #     raise ValueError('Too many results.')
    return search

def calculate_minutes(data, playerinfo, match_info:list):
    player_name = playerinfo.loc[:, "Player"].item()
    
    date = match_info[0]
    team = match_info[1]
    against = match_info[2]
    
    '''
        ???????????????????????? ????????????,??????????????? ???????????? numpy ?????????
        arr_mp = Minutes Played
        arr_io = In / Out
    '''
    arr_mp = data['MinutesPlayed'].to_numpy(dtype=np.float64)
    arr_io = data['Status'].to_numpy(dtype=np.int32)    
    
    '''
        BBRef ??? ???????????? ??????????????? ?????????????????? ????????? ????????? ????????? ??????????????? ????????? ??? ??????.
        ??? ??????????????? ????????? 0-48??? ????????? ?????? ?????? ????????? ????????? ??????????????? ???????????? ????????? ????????????.
    '''
    for _, i in enumerate(arr_mp):
        if _ < len(arr_mp) - 1:
            # ?????? ????????? ???????????? ????????? ????????????.
            if arr_io[_] == arr_io[_+1]:
                arr_mp[_] = arr_mp[_] + arr_mp[_ + 1]
                arr_mp = np.delete(arr_mp, _+1)
                # arr_io ??? ?????? ??? ???????????? ??? ????????? ??????
                arr_io = np.delete(arr_io, _+1)
    
    '''
        ??????????????? ???????????????????????? ???????????? ??????
        ?????? ???????????? ????????? ?????? ??????????????????/???????????? ????????? ????????? ???????????? ????????? ?????????????????? ???????????? ?????????.
        ?????? ?????? ?????????????????? ???????????? ??? ['00:00', '07:30'], ['07:30', '08:30'] ?????? ???????????? ???????????? ['00:00', '07:30'], ['07:30','16:00']
        ??? ?????? ???????????? ??????
    '''
    for _, i in enumerate(arr_mp):
        if _ < len(arr_mp) - 1:
            a = datetime.timedelta(seconds=round(i,0))
            m = (a.seconds // 60) % 60
            s = a.seconds - (m * 60)
            arr_mp[_] = a.seconds
    for _, i in enumerate(arr_mp):
        if _ < len(arr_mp) - 1:
            arr_mp[_ + 1] += i
    
    '''
        ????????? ???????????? ?????? ????????? ???????????? ??????????????? ?????????, ?????? ???????????? ????????? ?????? 2880??? ????????????.
        ????????? ????????? ???????????? ???????????? ???????????? ????????? ???/????????? ????????? ????????? ?????? ??? 2880??? ????????? ???????????????
        ????????? ????????? ?????? 2880??? ???????????? ????????? ????????? ??? ??????.
    '''
    for _, i in enumerate(arr_mp):
        d = i / arr_mp[-1]
        d = round(d * 2880, 0)
        arr_mp[_] = d
    
    '''
        48?????? ?????? ???????????? ????????? ???????????? ??? ?????? ????????? ????????? ????????????.
        ?????? ?????? 0:00?????? 5:40?????? ?????? ?????? ???????????? 1,2,3,4,5?????? ?????? ??????????????? 60??? ??????(1???=60??? ?????????),
        6?????? 42?????? ??????????????? 42??? ??????. 
    '''
    min_arr = np.zeros(shape=(49,))
    min_count = 0
    for _, i in enumerate(arr_mp):
        # ??? ????????? ??????, ?????? ????????? ?????? ????????? ????????? ??????
        if _ == 0:
            '''
                ?????? ????????? ?????????????????? ??????
                - duration_m = ?????? ??????(5??? 40?????? ?????? 5)
                - duration_s = ?????? ??????(5??? 40?????? ?????? 40)
            '''
            duration = datetime.timedelta(seconds=i)
            duration_m = (duration.seconds // 60) % 60
            duration_s = duration.seconds - (duration_m * 60)
            # ?????? ?????? ????????? ????????? ????????? ??????
            if arr_io[_] == 1:
                # ?????? ?????? ?????? 60?????? ??????
                for tick in range(0, duration_m):
                    min_arr[tick] = 60
            # ?????? ???????????? ????????? ??????
            if duration_s > 0:
                # ?????? ?????? ????????? ?????? ????????? ?????? ?????? ????????? ??????
                # ?????? ?????? 5???40?????? ?????? 0-4????????? 60, 5??? 42??? ?????? ??????
                min_arr[duration_m] = duration_s
                # min_count ??? ????????? ?????? ????????? ?????? ????????? ??????.
                min_count = duration_m
            else:
                min_count = duration_m - 1
        else:
            # ?????? ????????? ?????? ????????? ????????? ?????????
            last_pos = min_count
            # ?????? ?????? = ?????? ?????? ????????? ??????????????? - ?????? ?????? ????????? ???????????????
            duration = datetime.timedelta(seconds= i - arr_mp[_-1])
            duration_m = (duration.seconds // 60) % 60
            duration_s = duration.seconds - (duration_m * 60)
            if min_arr[last_pos] > 0: # ?????? ????????? ????????? ??????
                x = 60 - min_arr[last_pos] # ????????? ???????????? ????????? ?????? ?????????
                '''
                    ???????????? ?????????????????? ????????? ????????? ???????????? ??? ??????????????? ?????? ????????? ????????? ????????? ???????????? ????????? ?????????.
                    ?????? 5???40?????? ?????? 7???30?????? ???????????? ??????[0:4]??? 60, ??????[5]??? 40??? ??????.
                    ????????? 7???30?????? ??????????????? ????????? ??? ??????[5]??? 40?????? 60?????? ??? 20??? ???????????? ?????? ??????[6]?????? ???????????? ????????????
                    ????????? ????????? ??? ????????? ????????? 48??? ???????????? ??????. ????????? ?????? ??????????????? ????????? ????????? ??? ?????? ?????? ????????? ????????? ?????????
                    ?????? ?????? ?????? ????????? ?????? ????????? ??????????????? ???.
                '''
                if x > duration_s: # x?????? ?????? ???????????? ??? ??????
                    duration_s = 60 - (x - duration_s) # ???????????? ?????? > ???????????? ?????? ???????????? ????????? ?????????-?????? ????????? 60?????? ??????
                    duration_m -= 1 # ??? ?????? ?????? ?????? (????????? ???????????? ????????? ?????????.)
                elif x == duration_s: # ???????????? ???????????? ?????? ????????? ?????????
                    duration_s = 0 
                elif x < duration_s: # ???????????? ?????? ???????????? ????????? ???????????? ?????? ???????????? ????????? ???
                    duration_s = duration_s - x
                if arr_io[_] == 1: # ?????? ?????? ????????? ??????????????? ???????????? ?????? ????????? ???????????? ???????????? ?????? ??????????????? ????????? ??????
                    min_arr[last_pos] = 60 - min_arr[last_pos]
            last_pos += 1
            # ?????? ????????? ?????? ?????? ????????? ?????? 60?????? ??????
            for tick in range(last_pos, (last_pos + duration_m)):
                if arr_io[_] == 1:
                    min_arr[tick] = 60
            # ????????? ???????????? ?????? ?????? ????????? ???????????? ?????????. 
            # ????????? ?????????????????? ???????????? ????????? ???????????? ????????? ????????? ???????????? ???????????? ?????????.
            if _ < len(arr_mp) - 1:
                if duration_s > 0:
                    min_arr[last_pos + duration_m] = duration_s
                    min_count += (duration_m + 1)
                else:
                    min_count += duration_m
    min_arr = np.delete(min_arr, -1)
    
    # ???????????? 60?????? ?????? ????????? ??????
    # vectorize??? ?????? ????????? ??? ?????? ?????????
    def fun(e):
        return e / 60
    vectorize = np.vectorize(fun)
    min_arr = vectorize(min_arr)
    
    m_info = [player_name, date, team, against]
    m_df = pd.DataFrame([m_info], columns=['PlayerName', 'Date', 'Team', 'Opp'])
    df = pd.DataFrame([min_arr])
    columns = []
    for i in range(0, 48):
        columns.append(f'min_{i}')
    df.columns = columns
    df = pd.concat([m_df, df], axis=1)
    
    # DB??? ??????
    # conn = open_db('players')
    # df.to_sql('players', con=conn, if_exists='append', index=False)
    # conn.close()
    
    # Return
    bs_arr = []
    for _, i in enumerate(arr_mp):
        bs_arr.append(arr_mp[_])
        bs_arr.append(arr_io[_])
    return bs_arr
    
def bref_scrape_schedule(seasons:list=[2022]):
    '''
    Data Structure:
    __________________________________________________________________________________________________
    date       | visitor | home | visitor_score | home_score | status   | stage   | url
    --------------------------------------------------------------------------------------------------
    2022-10-19 | MIL     | LAL  | 130           | 119        | finished | regular | 202210180BOS.html
    --------------------------------------------------------------------------------------------------
    '''
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
                df = pd.read_html(html)[0]
                df = df[df['Date', 'Visitor/Neutral', 'Home/Neutral', 'PTS', 'PTS.1']]
                # WIP
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

def bref_scrape_chart(url:str, season:str):
    '''
    Basketball-Reference ??? Boxscore > Plus-minus ??????????????? ????????? ????????? ??????/????????? ???????????? ???????????? ??????.
    ????????? ???:??? ??? ???????????? ?????? ????????? ???????????????????????? ??????????????? ????????? ?????? ???????????? ????????? ????????? ?????????, ????????? ???????????? ??????????????? ?????? ??? ??????.
    ???????????? ??? ????????? ????????? ??? ???????????? ????????? ????????? ????????? ????????? ?????? ???, 2880??? ?????? ???:?????? ?????????. (48min = 2880sec) ??????????????? ???????????? ?????????.
    '''
    response = requests.get(url, headers=base_header)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    # url?????? ????????? ??????
    date = url.split('/')[-1:][0]
    date = re.findall("[0-9]", date)
    date = "".join(date)
    # ??? ????????? ?????????.
    away_team = full_to_abbr[soup.select_one('#content > div.scorebox > div:nth-child(1) > div:nth-child(1) > strong > a').text]
    home_team = full_to_abbr[soup.select_one('#content > div.scorebox > div:nth-child(2) > div:nth-child(1) > strong > a').text]
    # Sqlite3 ????????? ???
    filename = f'{date}_{away_team}@{home_team}'
    # ????????????????????? ???????????? ????????????
    table = soup.select_one('#content > div.plusminus > div')
    # ???????????? ????????? ????????????
    table_width = re.findall("\W([0-9]*)\w", table['style'])[0]
    # ?????????/??? ????????? ????????? ??????
    away_table = soup.select_one('#content > div.plusminus > div > div:nth-child(1)')
    home_table = soup.select_one('#content > div.plusminus > div > div:nth-child(2)')
    away_player = away_table.select('div.player')
    away_bar = away_table.select('div.player-plusminus')
    home_player = home_table.select('div.player')
    home_bar = home_table.select('div.player-plusminus')
    info_arr = []
    data_arr = []
    away_length = len(away_player)
    print('Creating Away Players timetable...')
    for idx in range(0, away_length):
        arr = []
        player_name = re.findall("(.*)\s\(", away_player[idx].text)[0]
        player_info = get_player_info(player_name, season)
        bars = away_bar[idx].select('div')
        # ????????? border-left ??? 1px??? ???????????? ?????? 1??? ?????????.
        actual_width = int(table_width) - 1
        status = np.zeros(shape=(len(bars),), dtype=np.int16)
        minute = np.zeros(shape=(len(bars),), dtype=np.float64)
        margin = np.zeros(shape=(len(bars),), dtype=np.int16)
        for i, rows in enumerate(bars):
            # ??? ?????? ??? ????????? ?????????.
            time_width = int(re.findall("\W([0-9]*)\w",rows['style'])[0]) + 1
            # ????????????/??????????????? ??? ????????? ??????
            actual_minute = time_width / actual_width
            # ratio * 2880?????? ???????????? ?????????.
            actual_minute = round(2880 * actual_minute, 1)
            try:
                # class ?????? minus, plus, even ??? ????????? on court ?????? class ??? ????????? off court ??????.
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
        match_info = [date, away_team, home_team]
        results = calculate_minutes(df, player_info, match_info)
        arr.append(player_name)
        arr.append(len(results))
        info_arr.append(arr)
        data_arr.append(results)
        
    home_length = len(home_player)
    print('Creating Home Players timetable...')
    for idx in range(0, home_length):
        arr = []
        player_name = re.findall("(.*)\s\(", home_player[idx].text)[0]
        player_info = get_player_info(player_name, season)
        bars = home_bar[idx].select('div')
        actual_width = int(table_width) - 1
        status = np.zeros(shape=(len(bars),), dtype=np.int16)
        minute = np.zeros(shape=(len(bars),), dtype=np.float64)
        margin = np.zeros(shape=(len(bars),), dtype=np.int16)
        for i, rows in enumerate(bars):
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
        match_info = [date, home_team, away_team]
        results = calculate_minutes(df, player_info, match_info)
        arr.append(player_name)
        arr.append(len(results))
        info_arr.append(arr)
        data_arr.append(results)
    
    # ?????????????????? ?????????????????? ???????????? DB??? Insert
    info_df = pd.DataFrame(info_arr, columns=['Player', 'Length'])
    data_df = pd.DataFrame(data_arr)
    df = pd.concat([info_df, data_df], axis=1)
    conn = open_db('boxscore')
    df.to_sql(filename, conn, if_exists='append')
    conn.close()
    
def bref_scrape_pbp(url:str, season):
    response = requests.get(url, headers=base_header)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    
    # url?????? ????????? ??????
    date = url.split('/')[-1:][0]
    date = re.findall("[0-9]", date)
    date = "".join(date)
    away = full_to_abbr[soup.select_one('#content > div.scorebox > div:nth-child(1) > div:nth-child(1) > strong > a').text]
    home = full_to_abbr[soup.select_one('#content > div.scorebox > div:nth-child(2) > div:nth-child(1) > strong > a').text]
    away_score = soup.select_one('#content > div.scorebox > div:nth-child(1) > div.scores > div').text
    home_score = soup.select_one('#content > div.scorebox > div:nth-child(2) > div.scores > div').text
    total_score = f'{away_score}-{home_score}'
    info_df = [date, season, away, home]
    info_df = pd.DataFrame([info_df], columns=['Date', 'Season', 'Away', 'Home'])
    
    # Drop multiindex
    df = pd.read_html(html)[0]
    df = df.loc[:, '1st Q']
    df = df.loc[:, ['Time','Score']]
    
    # Cut off overtime
    try:
        end_reg = df[df['Score'] == 'End of 4th quarter'].index.values[0]
        df = df.iloc[:end_reg+1, :]
    except:
        pass
    
    # Clear Jumpballs and duplicates
    debris = df[df['Score'].str.contains('Jump ball')]
    df = df.drop(labels=debris.index)
    
    # Drop useless rows
    debris = df[(df['Time'] == 'Time') | (df['Time'] == '2nd Q') | (df['Time'] == '3rd Q') | (df['Time'] == '4th Q')]
    df = df.drop(labels=debris.index)
    
    # Reset indices and cut dataframe into four quarters
    df.reset_index(drop=True, inplace=True)
    end_1 = df[df['Score'] == 'End of 1st quarter'].index.values[0]
    end_2 = df[df['Score'] == 'End of 2nd quarter'].index.values[0]
    end_3 = df[df['Score'] == 'End of 3rd quarter'].index.values[0]
    try:
        end_4 = df[df['Score'] == 'End of 4th quarter'].index.values[0]
    except:
        end_4 = None
    
    df_1 = df.iloc[1:end_1, :]
    df_2 = df.iloc[end_1+1:end_2, :]
    df_3 = df.iloc[end_2+1:end_3, :]
    if end_4 is not None:
        df_4 = df.iloc[end_3+1:end_4, :]
    else:
        df_4 = df.iloc[end_3+1:, :]
    
    # Transform into minute matrix
    min_arr = list(range(0, 49))
    for _, li in enumerate([df_1, df_2, df_3, df_4]):
        debris = li[(li['Time'] == '0:00.0') | (li['Score'].str.contains('of')) | (li['Score'].str.contains('Q'))]
        li = li.drop(labels=debris.index)
        li = li.drop_duplicates(keep="last", ignore_index=True)
        for row in li.itertuples():
            time = int(row.Time.split(":")[0])
            target = (((12 * _) + 12) - time) - 1
            min_arr[target] = row.Score
    min_arr[48] = total_score
    data_df = pd.DataFrame([min_arr])
    df = pd.concat([info_df, data_df], axis=1)
    df.rename(columns={48: 'Final'}, inplace=True)
    
    # Save it into database
    conn = open_db('teamboxscore')
    df.to_sql('teamboxscore', con=conn, if_exists='append')
    df.to_sql('teamboxscore', con=conn, if_exists='append')
    df.to_csv(f"src/data/pbp/teamboxscore.csv", mode="a", header=False)
    conn.close()
    
def remove_duplicate_matrix(file):
    df = pd.read_csv(file)
    df.drop_duplicates(subset='Date', keep='first', inplace=True)
    df.to_csv(file)
    
def create_roaster(team, season):
    url = f'https://www.basketball-reference.com/teams/{team}/{season}.html'
    team_df = pd.DataFrame(data=[[team, season]], columns=['Team', 'Season'])
    df = pd.read_html(url)[0]
    df['Player'] = df['Player'].map(lambda x: get_player_info(x, season=season).loc[:, "Player"].item())
    df = df.T
    df = df.loc[['Player'], :]
    df.index = [0]
    df = pd.concat([team_df, df], axis=1)
    conn = open_db('static')
    df.to_sql('roaster', conn, if_exists='append')
        
def get_roaster(team, season):
    conn = open_db('static')
    df = pd.read_sql('SELECT * FROM roaster_bref', con=conn)
    df = df[(df['Team'] == team) & (df['Season'] == season)]
    return df

def load_player_matrix(playername):
    conn = open_db('players')
    df = pd.read_sql(f'SELECT * FROM "{playername}"', con=conn)
    return df



# ---------* For test
# bref_scrape_chart('https://www.basketball-reference.com/boxscores/plus-minus/202202040UTA.html', '2022')

# ---------* Fetch data and reshape into time matrix
# season = '2022'
# # bref_base = 'https://www.basketball-reference.com/boxscores/pbp/'
# bref_base = 'https://www.basketball-reference.com/boxscores/plus-minus/'
# filepath = 'src/data/schedules/bref.com/'
# # filelist = os.listdir(filepath)
# # for file in tqdm(filelist):
# df = pd.read_csv("src/data/schedules/bref.com/bref_202122.csv")
# for row in df.itertuples():
#     if row.fetched == 0:
#         boxscore_url = str(row.boxscore_url).split("/")[-1]
#         url = bref_base + boxscore_url
#         print(url)
#         bref_scrape_chart(url=url, season=season)
#         # bref_scrape_pbp(url, season=season)
#         sleep(2)

# ---------* Remove duplicates
# filepath = 'src/data/teamdashplayers'
# filelist = os.listdir(filepath)
# for folder in filelist:
#     path = filepath + f'/{folder}/{folder}.csv'
#     remove_duplicate_matrix(path)
#     print(f'{folder} duplicated rows are dropped')

# ---------* Get 48 minutes means
# test_df = pd.read_csv('src/data/teamdashplayers/Giannis Antetokounmpo/Giannis Antetokounmpo.csv')
# test_df = test_df.loc[:, '0':]
# print(test_df.mean())

# ---------* Sanitize BBref player list names  
# player_list = pd.read_csv('src/data/static/players_bref.csv')
# for row in player_list.itertuples():
#     name = unidecode(row.Player)
#     player_list.iloc[row.Index, 0] = name
# player_list.to_csv('src/data/static/players_bref.csv')

# ---------* Create Roaster by seasons
# season = 2021
# for _, team in tqdm(enumerate(team_list_bref)):
#     print(_, team)
#     create_roaster(team=team,season=season)

# ---------* Get Roaster
# d = get_roaster('BOS', 2021)
# print(d)

# conn = open_db('players')
# cur = conn.cursor()

# TABLE_PARAM = "{TABLE_PARAM}"
# DROP_TABLE_SQL = f'DROP TABLE `{TABLE_PARAM}`;'
# GET_TABLES_SQL = f"SELECT name FROM sqlite_schema WHERE type='table';"

# cur.execute(GET_TABLES_SQL)
# tables = cur.fetchall()

# for row in tables:
#     sql = DROP_TABLE_SQL.replace(TABLE_PARAM, row[0])
#     print(sql)
#     cur.execute(sql)
# cur.close()