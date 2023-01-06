from django.db import models

# Create your models here.

#### PLAYER LOG DB ####
class PlayerIndex(models.Model):
    index = models.IntegerField(blank=True, null=True, primary_key=True)
    playername = models.TextField(db_column='PlayerName', blank=True, null=True)  # Field name made lowercase.
    date = models.TextField(db_column='Date', blank=True, null=True)  # Field name made lowercase.
    team = models.TextField(db_column='Team', blank=True, null=True)  # Field name made lowercase.
    opp = models.TextField(db_column='Opp', blank=True, null=True)  # Field name made lowercase.
    min_0 = models.FloatField(blank=True, null=True)
    min_1 = models.FloatField(blank=True, null=True)
    min_2 = models.FloatField(blank=True, null=True)
    min_3 = models.FloatField(blank=True, null=True)
    min_4 = models.FloatField(blank=True, null=True)
    min_5 = models.FloatField(blank=True, null=True)
    min_6 = models.FloatField(blank=True, null=True)
    min_7 = models.FloatField(blank=True, null=True)
    min_8 = models.FloatField(blank=True, null=True)
    min_9 = models.FloatField(blank=True, null=True)
    min_10 = models.FloatField(blank=True, null=True)
    min_11 = models.FloatField(blank=True, null=True)
    min_12 = models.FloatField(blank=True, null=True)
    min_13 = models.FloatField(blank=True, null=True)
    min_14 = models.FloatField(blank=True, null=True)
    min_15 = models.FloatField(blank=True, null=True)
    min_16 = models.FloatField(blank=True, null=True)
    min_17 = models.FloatField(blank=True, null=True)
    min_18 = models.FloatField(blank=True, null=True)
    min_19 = models.FloatField(blank=True, null=True)
    min_20 = models.FloatField(blank=True, null=True)
    min_21 = models.FloatField(blank=True, null=True)
    min_22 = models.FloatField(blank=True, null=True)
    min_23 = models.FloatField(blank=True, null=True)
    min_24 = models.FloatField(blank=True, null=True)
    min_25 = models.FloatField(blank=True, null=True)
    min_26 = models.FloatField(blank=True, null=True)
    min_27 = models.FloatField(blank=True, null=True)
    min_28 = models.FloatField(blank=True, null=True)
    min_29 = models.FloatField(blank=True, null=True)
    min_30 = models.FloatField(blank=True, null=True)
    min_31 = models.FloatField(blank=True, null=True)
    min_32 = models.FloatField(blank=True, null=True)
    min_33 = models.FloatField(blank=True, null=True)
    min_34 = models.FloatField(blank=True, null=True)
    min_35 = models.FloatField(blank=True, null=True)
    min_36 = models.FloatField(blank=True, null=True)
    min_37 = models.FloatField(blank=True, null=True)
    min_38 = models.FloatField(blank=True, null=True)
    min_39 = models.FloatField(blank=True, null=True)
    min_40 = models.FloatField(blank=True, null=True)
    min_41 = models.FloatField(blank=True, null=True)
    min_42 = models.FloatField(blank=True, null=True)
    min_43 = models.FloatField(blank=True, null=True)
    min_44 = models.FloatField(blank=True, null=True)
    min_45 = models.FloatField(blank=True, null=True)
    min_46 = models.FloatField(blank=True, null=True)
    min_47 = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'player_index'
        app_label = 'players'

#### STATIC DB ####
class PlayersBref(models.Model):
    index = models.IntegerField(blank=True, null=True, primary_key=True)
    player = models.TextField(db_column='Player', blank=True, null=True)  # Field name made lowercase.
    from_field = models.IntegerField(db_column='From', blank=True, null=True)  # Field name made lowercase. Field renamed because it was a Python reserved word.
    to = models.IntegerField(db_column='To', blank=True, null=True)  # Field name made lowercase.
    pos = models.TextField(db_column='Pos', blank=True, null=True)  # Field name made lowercase.
    ht = models.TextField(db_column='Ht', blank=True, null=True)  # Field name made lowercase.
    wt = models.FloatField(db_column='Wt', blank=True, null=True)  # Field name made lowercase.
    birth_date = models.TextField(db_column='Birth Date', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    colleges = models.TextField(db_column='Colleges', blank=True, null=True)  # Field name made lowercase.
    player_additional = models.TextField(db_column='Player-additional', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'players_bref'
        app_label = 'static'

class RoasterBref(models.Model):
    index = models.IntegerField(blank=True, null=True, primary_key=True)
    team = models.TextField(db_column='Team', blank=True, null=True)  # Field name made lowercase.
    season = models.IntegerField(db_column='Season', blank=True, null=True)  # Field name made lowercase.
    number_0 = models.TextField(db_column='0', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_1 = models.TextField(db_column='1', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_2 = models.TextField(db_column='2', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_3 = models.TextField(db_column='3', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_4 = models.TextField(db_column='4', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_5 = models.TextField(db_column='5', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_6 = models.TextField(db_column='6', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_7 = models.TextField(db_column='7', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_8 = models.TextField(db_column='8', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_9 = models.TextField(db_column='9', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_10 = models.TextField(db_column='10', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_11 = models.TextField(db_column='11', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_12 = models.TextField(db_column='12', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_13 = models.TextField(db_column='13', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_14 = models.TextField(db_column='14', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_15 = models.TextField(db_column='15', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_16 = models.TextField(db_column='16', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_17 = models.TextField(db_column='17', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_18 = models.TextField(db_column='18', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_19 = models.TextField(db_column='19', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_20 = models.TextField(db_column='20', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_21 = models.TextField(db_column='21', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_22 = models.TextField(db_column='22', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_23 = models.TextField(db_column='23', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_24 = models.TextField(db_column='24', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_25 = models.TextField(db_column='25', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_26 = models.TextField(db_column='26', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_27 = models.TextField(db_column='27', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_28 = models.TextField(db_column='28', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_29 = models.TextField(db_column='29', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_30 = models.FloatField(db_column='30', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_31 = models.FloatField(db_column='31', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_32 = models.FloatField(db_column='32', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_33 = models.FloatField(db_column='33', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_34 = models.FloatField(db_column='34', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_35 = models.FloatField(db_column='35', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.
    number_36 = models.FloatField(db_column='36', blank=True, null=True)  # Field renamed because it wasn't a valid Python identifier.

    class Meta:
        managed = False
        db_table = 'roaster_bref'
        app_label = 'static'

class TeamsBref(models.Model):
    index = models.IntegerField(blank=True, null=True, primary_key=True)
    teamid = models.IntegerField(db_column='teamId', blank=True, null=True)  # Field name made lowercase.
    abbreviation = models.TextField(blank=True, null=True)
    teamname = models.TextField(db_column='teamName', blank=True, null=True)  # Field name made lowercase.
    simplename = models.TextField(db_column='simpleName', blank=True, null=True)  # Field name made lowercase.
    location = models.TextField(blank=True, null=True)
    conference = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'teams_bref'
        app_label = 'static'