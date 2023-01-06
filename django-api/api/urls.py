from django.urls import path, include
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(r'player', views.PlayerViewSet, basename='player')
router.register(r'static/players', views.StaticPlayerViewSet, basename='static/players')
router.register(r'static/roaster', views.StaticRoasterViewSet, basename='static/roaster')
router.register(r'static/teams', views.StaticTeamsViewSet, basename='static/teams')
# router.register(r'team', views.TeamViewSet, basename='team')

urlpatterns = [
  path('', include(router.urls)),
]