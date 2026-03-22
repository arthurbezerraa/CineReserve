from django.shortcuts import redirect, render


def home_view(request):
    return redirect("login-page")


def login_view(request):
    return render(request, "auth/login.html")


def register_view(request):
    return render(request, "auth/register.html")


def movies_view(request):
    return render(request, "movies/list.html")
