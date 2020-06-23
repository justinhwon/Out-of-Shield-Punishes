from django.shortcuts import get_object_or_404, render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.template import loader
from django.views import generic
from django import forms


from django.db.models import Avg
import math

from .models import Framedata

# Create your views here.
class HomeView(generic.ListView):
    template_name = 'matchups/home.html'
    context_object_name = 'character_list'

    def get_queryset(self):
        """
        Return all characters ordered alphabetically.
        """
        nameDicts = Framedata.objects.order_by('character').values('character').distinct()
        return nameDicts

class CreditView(generic.TemplateView):
    template_name = 'matchups/credits.html'

class AboutView(generic.TemplateView):
    template_name = 'matchups/about.html'