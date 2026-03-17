from django.contrib import admin
from .models import Movie, Session

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ("title", "genre", "release_date", "is_active")
    list_filter = ("genre", "release_date", "is_active")
    search_fields = ("title", "description")
    ordering = ("title",)


@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ("movie", "room_number", "start_time", "end_time", "is_active")
    list_filter = ("movie", "room_number", "start_time", "end_time", "is_active")
    search_fields = ("movie__title",)
    ordering = ("start_time",)
