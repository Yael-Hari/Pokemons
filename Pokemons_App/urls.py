from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('add_a_pokemon', views.add_a_pokemon, name='add_a_pokemon'),
    path('query_results', views.query_results, name='query_results'),
]
