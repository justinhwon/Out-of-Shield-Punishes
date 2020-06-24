from django.shortcuts import get_object_or_404, render

# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.urls import reverse
from django.template import loader
from django.views import generic
from django import forms


from django.db.models import Avg
import math
import re

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

def MatchupSearchView(request):
    try:
        shieldCharData = Framedata.objects.filter(character=request.GET['Shielding Character'])
        attackCharData = Framedata.objects.filter(character=request.GET['Attacking Character'])
    except:
        # Error if character names not chosen correctly
        raise Http404("Character name does not exist. Please choose a name from the dropdown.")
    else:
        # get all shield character moves and calculate their first frame OOS
        # [name, frame oos, first frame not oos, frame data]
        shieldCharMoves = []
        for move in shieldCharData:
            # moves that require dropping shield add 11 frames
            if move.move in ("Jab 1", "Jab", "F-Tilt", "U-Tilt", "D-Tilt", "F-Smash", "D-Smash", "Jab 1 ", "Jab ", "F-Tilt ", "U-Tilt ", "D-Tilt ", "F-Smash ", "D-Smash "):
                moveName = move.move
                moveStartupComplete = move.startup
                moveStartupFrame = int(re.findall(r'\d+', moveStartupComplete)[0])
                moveFrame = moveStartupFrame + 11
                shieldCharMoves.append([moveName, moveFrame, moveStartupFrame, moveStartupComplete])
            # aerials add 3 frames
            elif move.move in ("F-Air", "F-Air ", "N-Air", "N-Air ", "B-Air", "B-Air ", "D-Air", "D-Air ", "Z-Air", "Z-Air "):
                moveName = move.move
                moveStartupComplete = move.startup
                moveStartupFrame = int(re.findall(r'\d+', moveStartupComplete)[0])
                moveFrame = moveStartupFrame + 3
                shieldCharMoves.append([moveName, moveFrame, moveStartupFrame, moveStartupComplete])
            # grabs add 4 frames
            elif move.move in ("Grab", "Grab "):
                moveName = move.move
                moveStartupComplete = move.startup
                moveStartupFrame = int(re.findall(r'\d+', moveStartupComplete)[0])
                moveFrame = moveStartupFrame + 4
                shieldCharMoves.append([moveName, moveFrame, moveStartupFrame, moveStartupComplete])
            # Dash attacks add 12 frames (11 shield drop + 1 to start dash)
            elif move.move in ("Dash Attack", "Dash Attack "):
                moveName = move.move
                moveStartupComplete = move.startup
                moveStartupFrame = int(re.findall(r'\d+', moveStartupComplete)[0])
                moveFrame = moveStartupFrame + 12
                shieldCharMoves.append([moveName, moveFrame, moveStartupFrame, moveStartupComplete])
            # Up-B and Upsmash are instantaneous
            elif "(Up-B)" in move.move or move.move in ("U-Smash", "U-Smash "):
                moveName = move.move
                moveStartupComplete = move.startup
                moveStartupFrame = int(re.findall(r'\d+', moveStartupComplete)[0])
                moveFrame = moveStartupFrame
                shieldCharMoves.append([moveName, moveFrame, moveStartupFrame, moveStartupComplete])

        # get all attack character moves and parse their frame advantage
        # [name, frame advantage]
        attackCharMoves = []
        for move in shieldCharData:
            # don't include grab and make sure advantage number exists
            if move.move not in ("Grab", "Grab ") and move.advantage:
                moveName = move.move
                moveAdvantage = int(re.findall(r'[+-]?\d+', move.advantage)[0])
                attackCharMoves.append([moveName, moveAdvantage])

        # Return all moves from each char
        return render(request, 'matchups/matchup.html', {
            'shieldFrame': shieldCharMoves,
            'attackFrame': attackCharMoves,
            'shieldCharData': shieldCharData,
            'attackCharData': attackCharData,
        })
