import pandas as pd
import numpy as np
import requests
import re
import os
import sys
sys.path.append('.')
from time import sleep
from bs4 import BeautifulSoup

from src.app.findplayer import get_player_info

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

def calculate_minutes(data, playerinfo):
    team_id = playerinfo.loc[:, "TEAM_ID"].item()
    player_id = playerinfo.loc[:, "PERSON_ID"].item()
    player_name = playerinfo.loc[:, "DISPLAY_FIRST_LAST"].item()
    
    mp = data['MinutesPlayed'].to_numpy()
    io = data['Status'].to_numpy()
    arr = np.array([])
    count = 0
    
    '''
    
    it = np.nditer(mp, flags=['f_index'])
    for val in it:
        idx = it.index
        # Break after 48 minutes of regular game time
        count += val
        if count >= 48:
            break
        
        # Divide value into integer and float
        _int = int(val)
        _flt = val - int(val)
        
        # Start
        if idx == 0:
            if io[idx] == 1:
                arr = np.append(arr, np.ones(shape=(_int, )))
            else:
                arr = np.append(arr, np.zeros(shape=(_int, )))
            arr = np.append(arr, [_flt])
        else:
            prev = arr[-1]
            if io[idx] == 1:
                if io[idx-1] == 1:
                    if prev + _flt > 1:
                        extra = 1 - (prev + _flt) # ie) 1 - (0.7 + 0.41) = 0.11
                        arr[-1] = 1
                        arr = np.append(arr, np.ones(shape=(_int, )))
                        arr = np.append(arr, [extra])
                    else:
                        rest = 1 - (prev + _flt) # ie) 1 - (0.35 + 0.45) = 0.2 
                        arr[-1] = 1
                        arr = np.append(arr, np.ones(shape=((_int - 1),)))
                        arr = np.append(arr, [1 - rest])
                else:
                    if _flt > (1 - prev): # (1 - 0.45) => 0.55 - 0.75 => -0.25
                        need = _flt - (1 - prev)
                    else:
                        need = (1 - prev) - _flt  
                    arr[-1] = 1 - prev
                    arr = np.append(arr, np.ones(shape=((_int - 1), )))
                    arr = np.append(arr, [1 - need])
            else:
                if io[idx-1] == 1: # ie) 1-0.65 => 0.35 - 0.55 
                    if _flt > (1 - prev):
                        extra = _flt - (1 - prev)
                    else:
                        extra = (1 - prev) - _flt
                    arr = np.append(arr, np.zeros(shape=((_int - 1), )))
                    arr = np.append(arr, [extra])
                else:
                    if prev + _flt > 1:
                        extra = (prev + _flt) - 1
                    else:
                        extra = 1 - (prev + _flt)
                    arr[-1] = 0
                    arr = np.append(arr, np.zeros(shape=(_int - 1, )))
                    arr = np.append(arr, [extra])'''
    
    for i in range(len(mp)):
        a = round(mp[i], 2)
        b = round(mp[i+1], 2)
        if a + b > 12:
            to_sum = (12 - a) - b
        elif a + b < 12:
            to_minus = 12 - (a + b)
        
            
        
                   
    print(player_name)    
    print(arr)
    print(len(arr))
    # if not os.path.isdir(f'src/data/teamdashplayers/{team_id}'):
    #     os.mkdir(f'src/data/teamdashplayers/{team_id}')
    # if not os.path.isdir(f'src/data/teamdashplayers/{team_id}/{player_id}'):
    #     os.mkdir(f'src/data/teamdashplayers/{team_id}/{player_id}')
    # df = pd.DataFrame(arr)
    # df.to_csv(f'src/data/teamdashplayers/{team_id}/{player_id}/{player_id}.csv', mode='a')
                
        
    

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

    df = pd.DataFrame(data=boxscore_url, columns=['boxscore_url'])
    df.to_csv(f'src/data/schedules/bref_{season}.csv')

def bref_scrape_chart(url:str):
    response = requests.get(url, headers=base_header)
    html = response.text
    soup = BeautifulSoup(html, 'lxml')
    
    date = url.split('/')[-1:][0]
    date = re.findall("[0-9]", date)
    date = "".join(date)
    away_team = full_to_abbr[soup.select_one('#content > div.scorebox > div:nth-child(1) > div:nth-child(1) > strong > a').text]
    home_team = full_to_abbr[soup.select_one('#content > div.scorebox > div:nth-child(2) > div:nth-child(1) > strong > a').text]
    filename = f'{date}_{away_team}@{home_team}'
    
    if not os.path.isdir(filename):
        os.mkdir(filename)
        os.mkdir(filename + "/" + away_team)
        os.mkdir(filename + "/" + home_team)

    table = soup.select_one('#content > div.plusminus > div')
    table_width = re.findall("\:([0-9]*)\w", table['style'])[0]

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
        player_info = get_player_info(player_name)
        bars = away_bar[idx].select('div')
        actual_width = int(table_width) - 1 - len(bars)        
        status = []; minute = []; margin = []
        for rows in bars:
            time_width = int(re.findall("\:([0-9]*)\w",rows['style'])[0])
            actual_minute = round(time_width / actual_width, 2)
            actual_minute = round(48 * actual_minute, 2)
            try:
                if rows['class'][0] == 'minus' or rows['class'][0] == 'plus':
                    status.append(1)
                    margin.append(int(rows.text))
            except:
                status.append(0)
                margin.append(0)
            finally:
                minute.append(actual_minute)
        df = pd.DataFrame(data=[minute, margin, status])
        df = df.T
        df.columns = ['MinutesPlayed', 'ScoreMargin', 'Status']
        df.to_csv(f'{filename}/{away_team}/{player_name}.csv')
        calculate_minutes(df, player_info)
        
    home_length = len(home_player)
    print('Creating Home Players timetable...')
    for idx in range(0, home_length):
        player_name = re.findall("(.*)\s\(", home_player[idx].text)[0]
        player_info = get_player_info(player_name)
        bars = home_bar[idx].select('div')
        actual_width = int(table_width) - 1 - len(bars)        
        status = []; minute = []; margin = []
        for rows in bars:
            time_width = int(re.findall("\:([0-9]*)\w",rows['style'])[0])
            actual_minute = round(time_width / actual_width, 2)
            actual_minute = round(48 * actual_minute, 2)
            try:
                if rows['class'][0] == 'minus' or rows['class'][0] == 'plus':
                    status.append(1)
                    margin.append(int(rows.text))
            except:
                status.append(0)
                margin.append(0)
            finally:
                minute.append(actual_minute)
        df = pd.DataFrame(data=[minute, margin, status])
        df = df.T
        df.columns = ['MinutesPlayed', 'ScoreMargin', 'Status']
        df.to_csv(f'{filename}/{home_team}/{player_name}.csv')
        calculate_minutes(df, player_info)


bref_scrape_chart('https://www.basketball-reference.com/boxscores/plus-minus/202211280BOS.html')