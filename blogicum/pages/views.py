from django.views.generic import TemplateView
from django.shortcuts import render

# Create your views here.


class About(TemplateView):
    template_name = 'pages/about.html'


class Rules(TemplateView):
    template_name = 'pages/rules.html'


def page_not_found(request, exception):
    return render(request, 'pages/404.html', status=404)


def csrf_failure(request, reason=''):
    return render(request, 'pages/403csrf.html', status=403)


def server_failure(request):
    return render(request, 'pages/500.html', status=500)
