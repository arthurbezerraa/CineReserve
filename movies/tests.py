from datetime import timedelta

from django.core.management import call_command
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Movie, Session


class SeedMoviesCommandTests(APITestCase):
    def test_seed_movies_creates_five_movies_and_three_sessions_each(self):
        call_command("seed_movies")

        self.assertEqual(Movie.objects.count(), 5)
        self.assertEqual(Session.objects.count(), 15)

        for movie in Movie.objects.all():
            self.assertGreaterEqual(movie.sessions.count(), 3)

    def test_seed_movies_is_idempotent(self):
        call_command("seed_movies")
        call_command("seed_movies")

        self.assertEqual(Movie.objects.count(), 5)
        self.assertEqual(Session.objects.count(), 15)


class SessionModelTests(APITestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Interstellar",
            description="Explorers travel through a wormhole in space.",
            genre="Sci-Fi",
            duration_minutes=169,
            release_date="2014-11-07",
        )

    def test_session_cannot_overlap_another_active_session_in_same_room(self):
        now = timezone.now()
        Session.objects.create(
            movie=self.movie,
            room_number=1,
            start_time=now + timedelta(hours=1),
            end_time=now + timedelta(hours=3),
        )

        conflicting_session = Session(
            movie=self.movie,
            room_number=1,
            start_time=now + timedelta(hours=2),
            end_time=now + timedelta(hours=4),
        )

        with self.assertRaises(ValidationError):
            conflicting_session.full_clean()


class MovieSessionListViewTests(APITestCase):
    def setUp(self):
        self.movie = Movie.objects.create(
            title="Arrival",
            description="A linguist communicates with aliens.",
            genre="Sci-Fi",
            duration_minutes=116,
            release_date="2016-11-11",
        )
        self.other_movie = Movie.objects.create(
            title="Blade Runner 2049",
            description="A new blade runner uncovers a secret.",
            genre="Sci-Fi",
            duration_minutes=164,
            release_date="2017-10-06",
        )

    def test_list_sessions_returns_active_sessions_for_movie(self):
        now = timezone.now()
        active_session = Session.objects.create(
            movie=self.movie,
            room_number=3,
            start_time=now + timedelta(hours=2),
            end_time=now + timedelta(hours=4),
            is_active=True,
        )
        Session.objects.create(
            movie=self.movie,
            room_number=4,
            start_time=now + timedelta(hours=5),
            end_time=now + timedelta(hours=7),
            is_active=False,
        )

        response = self.client.get(
            reverse("movie-sessions", kwargs={"movie_id": self.movie.pk})
        )
        results = response.data["results"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], active_session.id)
        self.assertEqual(results[0]["movie_id"], self.movie.id)
        self.assertEqual(results[0]["movie_title"], self.movie.title)

    def test_create_session_uses_movie_from_nested_route(self):
        now = timezone.now()

        response = self.client.post(
            reverse("movie-sessions", kwargs={"movie_id": self.movie.pk}),
            {
                "room_number": 7,
                "start_time": (now + timedelta(days=1)).isoformat(),
                "end_time": (now + timedelta(days=1, hours=2)).isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Session.objects.count(), 1)
        self.assertEqual(Session.objects.get().movie, self.movie)

    def test_create_session_rejects_overlapping_session_in_same_room(self):
        now = timezone.now()
        Session.objects.create(
            movie=self.movie,
            room_number=7,
            start_time=now + timedelta(days=1),
            end_time=now + timedelta(days=1, hours=2),
        )

        response = self.client.post(
            reverse("movie-sessions", kwargs={"movie_id": self.other_movie.pk}),
            {
                "room_number": 7,
                "start_time": (now + timedelta(days=1, hours=1)).isoformat(),
                "end_time": (now + timedelta(days=1, hours=3)).isoformat(),
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Session.objects.count(), 1)
