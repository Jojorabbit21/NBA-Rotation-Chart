from django.shortcuts import render
from rest_framework import status
from rest_framework import viewsets
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http.response import HttpResponse
from .models import PlayerIndex
from .serializers import PlayerSerializer
# Create your views here.

class PlayerViewSet(viewsets.ModelViewSet):
    queryset = PlayerIndex.objects.using('players').filter(playername='Kevin Durant')
    serializer_class = PlayerSerializer