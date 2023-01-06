from rest_framework import serializers
from .models import PlayerIndex

class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerIndex
        fields = ('index', 'playername', 'date', 'team', 'opp',)