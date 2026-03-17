from django.shortcuts import get_object_or_404
from rest_framework import generics
from .models import Movie, Session
from .serializers import MovieSerializer, SessionSerializer

class MovieListView(generics.ListCreateAPIView):
    serializer_class = MovieSerializer

    def get_queryset(self):
        return Movie.objects.filter(is_active=True)

class MovieDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = MovieSerializer

    def get_queryset(self):
        return Movie.objects.filter(is_active=True)

class MovieSessionListView(generics.ListCreateAPIView):
    serializer_class = SessionSerializer

    def get_movie(self):
        return get_object_or_404(
            Movie,
            pk=self.kwargs["movie_id"],
            is_active=True,
        )

    def get_queryset(self):
        movie = self.get_movie()

        return Session.objects.filter(movie=movie, is_active=True).order_by("start_time")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["movie"] = self.get_movie()
        return context

    def perform_create(self, serializer):
        serializer.save(movie=self.get_movie())
