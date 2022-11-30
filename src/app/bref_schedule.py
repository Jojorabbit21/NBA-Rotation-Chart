import pandas as pd
import requests
from time import sleep
from bs4 import BeautifulSoup

base_url = 'https://www.basketball-reference.com/leagues/NBA_{}_games-{}.html' # ex) 2023 => 2022-23
base_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'
}

seasons = [
  2019, 2020, 2021, 2022
]

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
            boxscores = soup.select("td.box_score_text > a")
            boxscore_url = []
            for boxscore in boxscores:
                boxscore_url.append(boxscore['href'])
            print(f'{len(boxscores)} games fetched.')
        else:
            print('no datas fetched')
            print(response.status_code)

df = pd.DataFrame(boxscore_url, columns='boxscore_url')
df.to_csv('src/data/schedules/schedules.csv')