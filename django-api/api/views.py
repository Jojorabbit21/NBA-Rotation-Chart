from rest_framework import viewsets

from .models import PlayerIndex, PlayersBref, RoasterBref, TeamsBref
from .serializers import PlayerSerializer, StaticPlayerSerializer, StaticRoasterSerializer, StaticTeamsSerializer
# Create your views here.

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = PlayerIndex.objects.using('players').all()
    serializer_class = PlayerSerializer
    filterset_fields = (
            'playername', 
            'date', 
            'team', 
            'opp', 
        )
    
class StaticPlayerViewSet(viewsets.ModelViewSet):
    queryset = PlayersBref.objects.using('static').all()
    serializer_class = StaticPlayerSerializer
    filterset_fields = (
            'player', 
            'from_field', 
            'to', 'pos', 
            'ht', 
            'wt', 
            'birth_date', 
            'colleges', 
            'player_additional', 
        )
    
class StaticRoasterViewSet(viewsets.ModelViewSet):
    queryset = RoasterBref.objects.using('static').all()
    serializer_class = StaticRoasterSerializer
    filterset_fields = (
            'index',
            'team',
            'season',
        )
    
class StaticTeamsViewSet(viewsets.ModelViewSet):
    queryset = TeamsBref.objects.using('static').all()
    serializer_class = StaticTeamsSerializer
    filterset_fields = (
            'teamid', 
            'abbreviation', 
            'teamname', 
            'simplename',
        )