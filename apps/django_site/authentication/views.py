from django.http import HttpResponseRedirect, HttpRequest
from django.views.generic import TemplateView
from django.contrib.auth import logout
from django.urls import reverse_lazy


def logout_view(request: HttpRequest) -> HttpResponseRedirect:
    """View-функция для выхода из аккаунта"""
    logout(request)
    return HttpResponseRedirect(reverse_lazy("authentication:login"))


class PrivacyPolicyTemplateView(TemplateView):
    """Политика конфиденциальности приложения"""

    template_name = "authentication/privacy-policy.html"
