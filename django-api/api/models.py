from django.db import models

# Create your models here.

class Player(models.Model):
    index = models.IntegerField(max_length=1000, primary_key=True)
    PlayerName = models.CharField(max_length=128, verbose_name='Name')
    Date = models.IntegerField(max_length=10, verbose_name='Date')
    Team = models.CharField(max_length=4, verbose_name='Team')
    _0 = models.DecimalField(verbose_name='0')
    _1 = models.DecimalField(verbose_name='0')
    _2 = models.DecimalField(verbose_name='0')
    _3 = models.DecimalField(verbose_name='0')
    _4 = models.DecimalField(verbose_name='0')
    _5 = models.DecimalField(verbose_name='0')
    _6 = models.DecimalField(verbose_name='0')
    _7 = models.DecimalField(verbose_name='0')
    _8 = models.DecimalField(verbose_name='0')
    _9 = models.DecimalField(verbose_name='0')
    _10 = models.DecimalField(verbose_name='0')
    _11 = models.DecimalField(verbose_name='0')
    _12 = models.DecimalField(verbose_name='0')
    _13 = models.DecimalField(verbose_name='0')
    _14 = models.DecimalField(verbose_name='0')
    _15 = models.DecimalField(verbose_name='0')
    _16 = models.DecimalField(verbose_name='0')
    _17 = models.DecimalField(verbose_name='0')
    _18 = models.DecimalField(verbose_name='0')
    _19 = models.DecimalField(verbose_name='0')
    _20 = models.DecimalField(verbose_name='0')
    _21 = models.DecimalField(verbose_name='0')
    _22 = models.DecimalField(verbose_name='0')
    _23 = models.DecimalField(verbose_name='0')
    _24 = models.DecimalField(verbose_name='0')
    _25 = models.DecimalField(verbose_name='0')
    _26 = models.DecimalField(verbose_name='0')
    _27 = models.DecimalField(verbose_name='0')
    _28 = models.DecimalField(verbose_name='0')
    _29 = models.DecimalField(verbose_name='0')
    _30 = models.DecimalField(verbose_name='0')
    _31 = models.DecimalField(verbose_name='0')
    _32 = models.DecimalField(verbose_name='0')
    _33 = models.DecimalField(verbose_name='0')
    _34 = models.DecimalField(verbose_name='0')
    _35 = models.DecimalField(verbose_name='0')
    _36 = models.DecimalField(verbose_name='0')
    _37 = models.DecimalField(verbose_name='0')
    _38 = models.DecimalField(verbose_name='0')
    _39 = models.DecimalField(verbose_name='0')
    _40 = models.DecimalField(verbose_name='0')
    _41 = models.DecimalField(verbose_name='0')
    _42 = models.DecimalField(verbose_name='0')
    _43 = models.DecimalField(verbose_name='0')
    _44 = models.DecimalField(verbose_name='0')
    _45 = models.DecimalField(verbose_name='0')
    _46 = models.DecimalField(verbose_name='0')
    _47 = models.DecimalField(verbose_name='0')

    class Meta:
        app_label = 'players'