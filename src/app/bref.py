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
    db_path = f'src/data/db/{dbname}.db'
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
        데이터프레임에서 출전시간,출전상태을 가져와서 numpy 객체화
        arr_mp = Minutes Played
        arr_io = In / Out
    '''
    arr_mp = data['MinutesPlayed'].to_numpy(dtype=np.float64)
    arr_io = data['Status'].to_numpy(dtype=np.int32)    
    
    '''
        BBRef 는 쿼터별로 출전시간이 나누어져있어 동일한 상태의 블럭이 연속적으로 존재할 수 있다.
        본 프로젝트의 목적은 0-48분 구간의 분당 출전 비율을 구하기 위함이므로 연속되는 블럭을 통합한다.
    '''
    for _, i in enumerate(arr_mp):
        if _ < len(arr_mp) - 1:
            # 다음 요소와 상태값이 같다면 합쳐준다.
            if arr_io[_] == arr_io[_+1]:
                arr_mp[_] = arr_mp[_] + arr_mp[_ + 1]
                arr_mp = np.delete(arr_mp, _+1)
                # arr_io 는 합칠 수 없으므로 뒷 요소를 삭제
                arr_io = np.delete(arr_io, _+1)
    
    '''
        출전시간을 누적출전시간으로 변환하는 과정
        최초 데이터를 가져올 때는 해당출전시간/전체값의 비율을 토대로 계산했기 때문에 특정구간으로 표현되지 않는다.
        예를 들어 타임스탬프로 변환했을 시 ['00:00', '07:30'], ['07:30', '08:30'] 으로 표현되는 데이터를 ['00:00', '07:30'], ['07:30','16:00']
        과 같이 변환하는 과정
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
        원본의 테이블이 간혹 두줄로 표시되는 페이지들이 있는데, 이런 페이지는 마지막 값이 2880을 넘어간다.
        이러한 잘못된 데이터를 교정하는 작업으로 배열의 값/배열의 마지막 요소로 나눈 후 2880을 곱하여 정수화하면
        마지막 배열의 값이 2880을 넘어가지 않도록 다듬을 수 있다.
    '''
    for _, i in enumerate(arr_mp):
        d = i / arr_mp[-1]
        d = round(d * 2880, 0)
        arr_mp[_] = d
    
    '''
        48개의 분에 해당하는 배열을 생성하고 각 분당 출전한 시간을 기록한다.
        예를 들어 0:00부터 5:40까지 코트 위에 있었다면 1,2,3,4,5분은 모두 뛰었으므로 60이 되고(1분=60초 이므로),
        6분은 42초를 뛰었으므로 42가 된다. 
    '''
    min_arr = np.zeros(shape=(49,))
    min_count = 0
    for _, i in enumerate(arr_mp):
        # 첫 요소일 경우, 이전 요소의 값을 생각할 필요가 없음
        if _ == 0:
            '''
                출전 시간을 타임스탬프로 변환
                - duration_m = 분의 정수(5분 40초일 경우 5)
                - duration_s = 초의 정수(5분 40초의 경우 40)
            '''
            duration = datetime.timedelta(seconds=i)
            duration_m = (duration.seconds // 60) % 60
            duration_s = duration.seconds - (duration_m * 60)
            # 만약 해당 시간이 출전한 시간일 경우
            if arr_io[_] == 1:
                # 해당 분의 값을 60으로 설정
                for tick in range(0, duration_m):
                    min_arr[tick] = 60
            # 초의 정수값이 존재할 경우
            if duration_s > 0:
                # 분의 정수 길이에 있는 배열의 값을 초의 정수로 설정
                # 예를 들어 5분40초일 경우 0-4까지는 60, 5가 42가 되기 때문
                min_arr[duration_m] = duration_s
                # min_count 는 루프의 다음 배열의 시작 지점이 된다.
                min_count = duration_m
            else:
                min_count = duration_m - 1
        else:
            # 시작 지점을 이전 요소의 값에서 가져옴
            last_pos = min_count
            # 출전 시간 = 현재 루프 요소의 타임스탬프 - 이전 루프 요소의 타임스탬프
            duration = datetime.timedelta(seconds= i - arr_mp[_-1])
            duration_m = (duration.seconds // 60) % 60
            duration_s = duration.seconds - (duration_m * 60)
            if min_arr[last_pos] > 0: # 초의 정수가 존재할 경우
                x = 60 - min_arr[last_pos] # 얼마를 더하거나 빼줘야 할지 구한다
                '''
                    표기되는 타임스탬프와 시간을 배열로 나타냈을 때 기록되어야 하는 방식이 다르기 때문에 변환하는 과정을 거친다.
                    만약 5분40초를 뛰고 7분30초를 쉬었다면 배열[0:4]는 60, 배열[5]는 40이 된다.
                    여기서 7분30초의 휴식시간을 계산할 때 배열[5]의 40초를 60에서 뺀 20을 고려하지 않고 배열[6]부터 계산하여 기록하면
                    루프가 끝났을 때 배열의 총합이 48을 넘어가게 된다. 그래서 배열 시작지점에 소수가 있다면 그 값을 루프 대상의 값에서 빼주고
                    남은 값은 루프 대상의 소수 자리에 더해주어야 함.
                '''
                if x > duration_s: # x값이 초의 정수보다 클 경우
                    duration_s = 60 - (x - duration_s) # 필요분을 계산 > 필요분이 초의 정수보다 크므로 필요분-초의 정수를 60에서 빼줌
                    duration_m -= 1 # 분 값을 하나 빼줌 (시간의 절대값은 변하지 않는다.)
                elif x == duration_s: # 필요분이 동일하면 초의 정수를 없애줌
                    duration_s = 0 
                elif x < duration_s: # 필요분이 초의 정수보다 작으면 간단하게 초의 정수에서 빼주면 됨
                    duration_s = duration_s - x
                if arr_io[_] == 1: # 해당 루프 배열이 출전시간일 경우에는 직전 배열의 소수값은 출전하지 않은 시간이므로 차분을 기입
                    min_arr[last_pos] = 60 - min_arr[last_pos]
            last_pos += 1
            # 출전 시간일 경우 시간 배열의 값을 60으로 설정
            for tick in range(last_pos, (last_pos + duration_m)):
                if arr_io[_] == 1:
                    min_arr[tick] = 60
            # 배열의 마지막일 경우 다음 배열을 계산하지 않는다. 
            # 배열의 마지막이면서 출전하지 않았을 경우에는 계산할 필요가 없으므로 계산하지 않는다.
            if _ < len(arr_mp) - 1:
                if duration_s > 0:
                    min_arr[last_pos + duration_m] = duration_s
                    min_count += (duration_m + 1)
                else:
                    min_count += duration_m
    min_arr = np.delete(min_arr, -1)
    
    # 절대값을 60초에 대한 비율로 변환
    # vectorize를 통해 배열에 한 번에 적용함
    def fun(e):
        return e / 60
    vectorize = np.vectorize(fun)
    min_arr = vectorize(min_arr)
    
    m_info = [player_name, date, team, against]
    m_df = pd.DataFrame([m_info], columns=['PlayerName', 'Date', 'Team', 'Opp'])
    df = pd.DataFrame([min_arr])
    df = pd.concat([m_df, df], axis=1)
    
    # DB에 저장
    conn = open_db('players')
    df.to_sql(player_name, con=conn, if_exists='append')
    
    # Return
    bs_arr = []
    for _, i in enumerate(arr_mp):
        bs_arr.append(arr_mp[_])
        bs_arr.append(arr_io[_])
    return bs_arr
    
    
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

def bref_scrape_chart(url:str, season:str):
    '''
    Basketball-Reference 의 Boxscore > Plus-minus 페이지에는 선수별 온코트 시간/마진이 테이블로 기록되어 있음.
    정확한 분:초 는 기재되어 있지 않지만 데이터베이스에서 출전시간을 가져와 표로 변환하는 과정을 거치기 때문에, 역으로 변환하면 출전시간을 얻을 수 있음.
    테이블의 총 길이를 구하고 각 출전시간 블럭의 길이를 구해서 비율을 구한 뒤, 2880을 곱해 분:초를 구한다. (48min = 2880sec) 오버타임은 계산하지 않는다.
    '''
    response = requests.get(url, headers=base_header)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    # url에서 날짜를 추출
    date = url.split('/')[-1:][0]
    date = re.findall("[0-9]", date)
    date = "".join(date)
    # 각 팀명을 구한다.
    away_team = full_to_abbr[soup.select_one('#content > div.scorebox > div:nth-child(1) > div:nth-child(1) > strong > a').text]
    home_team = full_to_abbr[soup.select_one('#content > div.scorebox > div:nth-child(2) > div:nth-child(1) > strong > a').text]
    # Sqlite3 테이블 명
    filename = f'{date}_{away_team}@{home_team}'
    # 데이터테이블을 파싱하여 가져온다
    table = soup.select_one('#content > div.plusminus > div')
    # 테이블의 길이를 구해준다
    table_width = re.findall("\W([0-9]*)\w", table['style'])[0]
    # 어웨이/홈 테이블 데이터 저장
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
        print(player_name)
        player_info = get_player_info(player_name, season)
        bars = away_bar[idx].select('div')
        # 테이블 border-left 가 1px로 설정되어 있어 1을 빼준다.
        actual_width = int(table_width) - 1
        status = np.zeros(shape=(len(bars),), dtype=np.int16)
        minute = np.zeros(shape=(len(bars),), dtype=np.float64)
        margin = np.zeros(shape=(len(bars),), dtype=np.int16)
        for i, rows in enumerate(bars):
            # 각 블럭 별 너비를 구한다.
            time_width = int(re.findall("\W([0-9]*)\w",rows['style'])[0]) + 1
            # 블럭너비/테이블너비 로 비율을 구함
            actual_minute = time_width / actual_width
            # ratio * 2880으로 근사치를 구한다.
            actual_minute = round(2880 * actual_minute, 1)
            try:
                # class 명이 minus, plus, even 일 경우는 on court 이고 class 가 없으면 off court 이다.
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
        print(player_name)
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
    
    # 박스스코어별 데이터프레임 생성하여 DB에 Insert
    info_df = pd.DataFrame(info_arr, columns=['Player', 'Length'])
    data_df = pd.DataFrame(data_arr)
    df = pd.concat([info_df, data_df], axis=1)
    conn = open_db('boxscore')
    df.to_sql(filename, conn, if_exists='replace')
    
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

# ---------* Player Search Test

# ---------* For test
# bref_scrape_chart('https://www.basketball-reference.com/boxscores/plus-minus/202112010OKC.html', '2022')

# ---------* Fetch data and reshape into time matrix
season = '2022'
bref_base = 'https://www.basketball-reference.com/boxscores/plus-minus/'
filepath = 'src/data/schedules/bref.com/'
filelist = os.listdir(filepath)
for file in tqdm(filelist):
    df = pd.read_csv(filepath + file)
    for row in df.itertuples():
        if row.fetched == 0:
            boxscore_url = str(row.boxscore_url).split("/")[-1]
            url = bref_base + boxscore_url
            print(url)
            bref_scrape_chart(url=url, season=season)
            sleep(1.5)

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
