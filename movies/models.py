from django.core.exceptions import ValidationError
from django.db import models

# Create your models here.

class Movie(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    genre = models.CharField(max_length=50)
    duration_minutes = models.IntegerField()
    release_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Filme"
        verbose_name_plural = "Filmes"

class Session(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='sessions')
    room_number = models.IntegerField()
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.movie.title} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"

    def clean(self):
        super().clean()

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError(
                {"end_time": "O horario de termino deve ser posterior ao horario de inicio."}
            )

        if (
            not self.is_active
            or self.room_number is None
            or not self.start_time
            or not self.end_time
        ):
            return

        conflicting_sessions = Session.objects.filter(
            room_number=self.room_number,
            is_active=True,
            start_time__lt=self.end_time,
            end_time__gt=self.start_time,
        )

        if self.pk:
            conflicting_sessions = conflicting_sessions.exclude(pk=self.pk)

        if conflicting_sessions.exists():
            raise ValidationError(
                "Ja existe uma sessao ativa cadastrada nessa sala durante esse horario."
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Sessão"
        verbose_name_plural = "Sessões"
        ordering = ['start_time']
