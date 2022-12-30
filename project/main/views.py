from django.shortcuts import render
from django.conf import settings

import pandas as pd
import sqlite3

# Create your views here.

def open_db(dbname):
    db_path = f'{dbname}.sqlite3'
    conn = sqlite3.connect(db_path)
    return conn

def index(request):
    db = open_db('static')
    df = pd.read_sql('SELECT * FROM teams_bref;', con=db)
    eastern = df[df['conference'] == 'East']
    western = df[df['conference'] == 'West']
    eastern = eastern[['teamName', 'abbreviation']]
    western = western[['teamName', 'abbreviation']]
    context = {
        "eastern": eastern,
        "western": western
    }
    return render(request, 'main/index.html', context)

def team(request, team_name, season=2021):
    db = open_db('static')
    df = pd.read_sql(f'SELECT * FROM roaster_bref WHERE Season = {season} AND Team = "{team_name}"', con=db)
    info_df = pd.read_sql(f'SELECT * FROM teams_bref WHERE abbreviation = "{team_name}"', con=db)
    context = {
        "team": df,
        "info": info_df
    }
    return render(request, 'main/team.html', context)