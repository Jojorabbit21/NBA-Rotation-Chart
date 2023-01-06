from rest_framework import serializers
from .models import PlayerIndex, PlayersBref, RoasterBref, TeamsBref

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerIndex
        fields = ('index', 'playername', 'date', 'team', 'opp',)
        
class StaticPlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayersBref
        fields = ('player', 'from_field', 'to', 'pos', 'ht', 'wt', 'birth_date', 'colleges', 'player_additional', )
        
class StaticRoasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoasterBref
        fields = (
            'index',
            'team',
            'season',
            'number_0',
            'number_1',
            'number_2',
            'number_3',
            'number_4',
            'number_5',
            'number_6',
            'number_7',
            'number_8',
            'number_9',
            'number_10',
            'number_11',
            'number_12',
            'number_13',
            'number_14',
            'number_15',
            'number_16',
            'number_17',
            'number_18',
            'number_19',
            'number_20',
            'number_21',
            'number_22',
            'number_23',
            'number_24',
            'number_25',
            'number_26',
            'number_27',
            'number_28',
            'number_29',
            'number_30',
            'number_31',
            'number_32',
            'number_33',
            'number_34',
            'number_35',
            'number_36',
        )
        
class StaticTeamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeamsBref
        fields = ('teamid', 'abbreviation', 'teamname', 'simplename', 'location', 'conference',)
  