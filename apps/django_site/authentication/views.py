from django.http import HttpResponseRedirect, HttpRequest
from django.contrib.auth import logout
from django.urls import reverse_lazy


def logout_view(request: HttpRequest) -> HttpResponseRedirect:
    """View-функция для выхода из аккаунта"""
    logout(request)
    return HttpResponseRedirect(reverse_lazy("authentication:login"))
