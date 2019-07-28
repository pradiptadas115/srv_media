from django.urls import path
from .views import *

urlpatterns = [
    path('',index,name="home"),
    path('equities/',get_equity_data_init,name="get_equities"),
    path('get_equity_value/',get_todays_value,name="get_equity_value"),
]