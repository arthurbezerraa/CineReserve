from django.urls import path
from .views import MovieListView, MovieDetailView, MovieSessionListView

urlpatterns = [
    path('', MovieListView.as_view(), name='movie-list'),
    path('<int:pk>/', MovieDetailView.as_view(), name='movie-detail'),
    path('<int:movie_id>/sessions/', MovieSessionListView.as_view(), name='movie-sessions'),
]