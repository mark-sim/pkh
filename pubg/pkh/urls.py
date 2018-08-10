from django.urls import path

from . import views

app_name = 'pkh'
urlpatterns = [
    path('', views.index, name='index'),
    path('matches/', views.matches, name='matches'),
    path('hierarchy/<slug:matchId>', views.hierarchy, name='hierarchy'),
]