import pandas as pd

def load_player_list():
    return pd.read_csv('src/data/players.csv')

def get_player_info(playername:str):
    player_list = load_player_list()
    search = player_list[player_list['DISPLAY_FIRST_LAST'].str.contains(playername, case=False)]
    # if len(search) > 1:
    #     raise ValueError('Too many results.')
    return search