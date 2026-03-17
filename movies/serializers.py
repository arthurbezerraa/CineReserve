from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from .models import Movie, Session

class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = [
            'id',
            'title', 
            'description', 
            'genre', 
            'release_date', 
            'created_at', 
            'updated_at'
            ]

class SessionSerializer(serializers.ModelSerializer):
    movie_id = serializers.IntegerField(source="movie.id", read_only=True)
    movie_title = serializers.CharField(source="movie.title", read_only=True)

    class Meta:
        model = Session
        fields = [
            'id',
            'movie_id',
            'movie_title', 
            'room_number', 
            'start_time', 
            'end_time', 
            'created_at', 
            'updated_at'
            ]
        read_only_fields = ['id', 'movie_id', 'movie_title', 'created_at', 'updated_at']

    def validate(self, attrs):
        if self.instance is not None:
            movie = self.instance.movie
            room_number = attrs.get("room_number", self.instance.room_number)
            start_time = attrs.get("start_time", self.instance.start_time)
            end_time = attrs.get("end_time", self.instance.end_time)
            is_active = attrs.get("is_active", self.instance.is_active)
        else:
            movie = self.context.get("movie")
            room_number = attrs.get("room_number")
            start_time = attrs.get("start_time")
            end_time = attrs.get("end_time")
            is_active = attrs.get("is_active", True)

        if movie is None:
            return attrs

        session = Session(
            movie=movie,
            room_number=room_number,
            start_time=start_time,
            end_time=end_time,
            is_active=is_active,
        )

        if self.instance is not None:
            session.pk = self.instance.pk

        try:
            session.clean()
        except DjangoValidationError as exc:
            if hasattr(exc, "message_dict"):
                raise serializers.ValidationError(exc.message_dict)
            raise serializers.ValidationError(exc.messages)

        return attrs
