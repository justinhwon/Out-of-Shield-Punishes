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
        shieldChar = request.GET['Shielding Character']
        attackChar = request.GET['Attacking Character']
        shieldCharData = Framedata.objects.filter(character=shieldChar)
        attackCharData = Framedata.objects.filter(character=attackChar)
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
            #don't include other moves

        # once list is complete, sort by frame oos (least to greatest)
        shieldCharMoves.sort(key = lambda x: x[1])

        # get all attack character moves and parse their frame advantage
        # [name, frame advantage]
        attackCharMoves = []
        for move in shieldCharData:
            # don't include grab and make sure advantage number exists
            if move.move not in ("Grab", "Grab ") and move.advantage:
                moveName = move.move
                # get the highest value advantage number
                moveAdvantage = max(list(map(int, re.findall(r'[+-]?\d+', move.advantage))))
                attackCharMoves.append([moveName, moveAdvantage, move.advantage])
        
        # once list is complete, sort by frame advantage (greatest to least)
        attackCharMoves.sort(key = lambda x: x[1], reverse=True)

        # now create lists of which attackChar moves are punishable by which shieldChar moves on shield
        # keep building solution starting from fastest shieldChar moves
        #while i < range(len(attackCharMoves)) or j < range(shieldCharMoves):
            # move cannot be punished oos if frame disadvantage + startup > 0
            #if shieldCharMoves[0] + attackCharMoves[i] > 0:

        # Return all moves from each char
        return render(request, 'matchups/matchup.html', {
            'shieldChar': shieldChar,
            'attackChar': attackChar,
            'shieldFrame': shieldCharMoves,
            'attackFrame': attackCharMoves,
            'shieldCharData': shieldCharData,
            'attackCharData': attackCharData,
        })
