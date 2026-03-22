from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from CineReserve.views import home_view, login_view, movies_view, register_view

urlpatterns = [
    path("", home_view, name="home"),
    path("login/", login_view, name="login-page"),
    path("register/", register_view, name="register-page"),
    path("movies/", movies_view, name="movies-page"),
    path("admin/", admin.site.urls),
    path("api/movies/", include("movies.urls")),
    path("api/auth/", include("users.urls")),
    path("api/auth/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
