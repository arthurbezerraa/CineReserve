from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from movies.models import Movie, Session


MOVIES_DATA = [
    {
        "title": "Duna: Parte Dois",
        "description": "Paul Atreides se une aos Fremen para buscar vinganca e mudar o destino de Arrakis.",
        "genre": "Sci-Fi",
        "duration_minutes": 166,
        "release_date": "2024-02-29",
    },
    {
        "title": "Oppenheimer",
        "description": "A historia do fisico J. Robert Oppenheimer durante o Projeto Manhattan.",
        "genre": "Drama",
        "duration_minutes": 180,
        "release_date": "2023-07-20",
    },
    {
        "title": "Barbie",
        "description": "Barbie parte em uma jornada pelo mundo real para descobrir quem realmente e.",
        "genre": "Comedy",
        "duration_minutes": 114,
        "release_date": "2023-07-20",
    },
    {
        "title": "Divertida Mente 2",
        "description": "Novas emocoes chegam a mente de Riley enquanto ela entra na adolescencia.",
        "genre": "Animation",
        "duration_minutes": 96,
        "release_date": "2024-06-14",
    },
    {
        "title": "Batman",
        "description": "Bruce Wayne investiga uma serie de crimes enquanto Gotham mergulha no caos.",
        "genre": "Action",
        "duration_minutes": 176,
        "release_date": "2022-03-03",
    },
]

SESSION_START_HOURS = [13, 16, 19]


class Command(BaseCommand):
    help = "Popula o banco com 5 filmes e pelo menos 3 sessoes por filme."

    @transaction.atomic
    def handle(self, *args, **options):
        base_date = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        created_movies = 0
        created_sessions = 0

        for index, movie_data in enumerate(MOVIES_DATA, start=1):
            movie, movie_created = Movie.objects.update_or_create(
                title=movie_data["title"],
                defaults=movie_data,
            )
            created_movies += int(movie_created)

            for day_offset, hour in enumerate(SESSION_START_HOURS):
                start_time = base_date + timedelta(days=index + day_offset, hours=hour)
                end_time = start_time + timedelta(minutes=movie.duration_minutes)

                _, session_created = Session.objects.update_or_create(
                    movie=movie,
                    room_number=index,
                    start_time=start_time,
                    defaults={
                        "end_time": end_time,
                        "is_active": True,
                    },
                )
                created_sessions += int(session_created)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed concluida: {Movie.objects.count()} filmes no total e "
                f"{Session.objects.count()} sessoes no total. "
                f"Criados agora: {created_movies} filmes e {created_sessions} sessoes."
            )
        )
