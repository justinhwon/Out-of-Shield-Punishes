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

from .models import Framedata, Meleeoos, Meleeframedata

# Create your views here.
'''
class HomeView(generic.ListView):
    template_name = 'matchups/home.html'
    context_object_name = 'character_list'

    def get_queryset(self):
        """
        Return all characters ordered alphabetically.
        """
        nameDicts = Framedata.objects.order_by('character').values('character').distinct()
        return nameDicts
'''
class HomeView(generic.TemplateView):
    template_name = 'matchups/home.html'

class HomeMeleeView(generic.ListView):
    template_name = 'matchups/homemelee.html'
    context_object_name = 'character_list'

    def get_queryset(self):
        """
        Return all characters ordered alphabetically.
        """
        nameDicts = Meleeframedata.objects.order_by('character').values('character').distinct()
        return nameDicts

class SitemapView(generic.TemplateView):
    template_name = 'matchups/sitemap.xml'

class CreditView(generic.TemplateView):
    template_name = 'matchups/credits.html'

class AboutView(generic.TemplateView):
    template_name = 'matchups/about.html'

class PrivacyView(generic.TemplateView):
    template_name = 'matchups/privacypolicy.html'

class CookieView(generic.TemplateView):
    template_name = 'matchups/cookiepolicy.html'

class TermsView(generic.TemplateView):
    template_name = 'matchups/termsconditions.html'

def MatchupSearchView(request):
    try:
        shieldChar = request.GET['Your Character']
        attackChar = request.GET['Opponent Character']
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
            if move.move in ("Jab 1", "Jab", "F-Tilt", "U-Tilt", "D-Tilt", "F-Smash", "D-Smash", "Jab 1 ", "Jab ", "F-Tilt ", "U-Tilt ", "D-Tilt ", "F-Smash ", "D-Smash ", "F-Smash (early)", "D-Smash (early)"):
                moveName = move.move
                moveStartupComplete = move.startup
                moveStartupFrame = int(re.findall(r'\d+', moveStartupComplete)[0])
                moveFrame = moveStartupFrame + 11
                shieldCharMoves.append([moveName, moveFrame, moveStartupFrame, moveStartupComplete])
            # aerials add 3 frames
            elif move.move in ("F-Air", "F-Air ", "N-Air", "N-Air ", "B-Air", "B-Air ", "D-Air", "D-Air ", "U-Air", "U-Air ", "Z-Air", "Z-Air ", "N-Air (either Dragon)", "N-Air (Ramram)", "N-Air (Megawatt)"):
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
                # some up-b are not attacks (e.g. teleport), so just skip
                if not move.startup:
                    continue
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
        for move in attackCharData:
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
        
        punishList = []
        #if at start there are unpunishable moves
        if shieldCharMoves[0][1] + attackCharMoves[0][1] > 0:
            punishOptions = []
            punishableMoves = []
            # pop from attackCharMoves until punishable
            while shieldCharMoves[0][1] + attackCharMoves[0][1] > 0:
                punishableMoves.append(attackCharMoves.pop(0))
            punishList.append([punishOptions, punishableMoves])
        
        # end loop when no moves remain
        while shieldCharMoves or attackCharMoves:
            punishOptions = []
            punishableMoves = []

            # if there remains a move that cannot punish anything, just end
            if not attackCharMoves:
                break

            # move CANNOT be punished OOS if frame disadvantage + startup > 0
            # move CAN be punished OOS if frame disadvantage + startup <= 0

            # pop from shieldCharMoves until attackCharMove cannot be punished
            while shieldCharMoves and shieldCharMoves[0][1] + attackCharMoves[0][1] <= 0:
                punishOptions.append(shieldCharMoves.pop(0))

            # if no more shieldCharMoves, only attackCharMoves left so put all 
            # remaining attackCharMoves into punishable moves and finish up
            if not shieldCharMoves:
                while attackCharMoves:
                    punishableMoves.append(attackCharMoves.pop(0))
                punishList.append([punishOptions, punishableMoves])
                break
                
            # current attackCharMove is not punishable by shieldCharMove
            # pop from attackCharMove until it CAN be punished by shieldCharMove
            while attackCharMoves and shieldCharMoves[0][1] + attackCharMoves[0][1] > 0:
                punishableMoves.append(attackCharMoves.pop(0))
            
            # punishOptions is now the limit of what moves can punish current punishableMoves
            # punishableMoves is the limit of what moves can be punished by current punishOptions

            punishList.append([punishOptions, punishableMoves])


        """ # better solution (space/readability-wise) just using lists as stacks
        i, j = 0, 0

        # if currently there are unpunishable moves, make a list of those and update i,j
        if shieldCharMoves[i][1] + attackCharMoves[j][1] > 0:
            punishOptions = []
            punishableMoves = []
            # push j until j CAN be punished by i
            while shieldCharMoves[i][1] + attackCharMoves[j][1] > 0:
                punishableMoves.append(attackCharMoves[j])
                j+=1
            punishList.append([punishOptions, punishableMoves])

        # end loop when no moves remain
        while i < len(shieldCharMoves) or j < len(attackCharMoves):
            punishOptions = []
            punishableMoves = []

            # if there remains a move that cannot punish anything, just end
            if j >= len(attackCharMoves):
                break

            # move CANNOT be punished OOS if frame disadvantage + startup > 0
            # move CAN be punished OOS if frame disadvantage + startup <= 0

            # push i until j CANNOT be punished by i
            while shieldCharMoves[i][1] + attackCharMoves[j][1] <= 0:
                punishOptions.append(shieldCharMoves[i])
                i += 1
                # finish up if i at end of OOS move list
                if i >= len(shieldCharMoves):
                    break

            # if i > max length, only j left so put all remaining j into punishable moves
            # and finish up
            if i >= len(shieldCharMoves):
                while j < len(attackCharMoves):
                    punishableMoves.append(attackCharMoves[j])
                    j += 1
                punishList.append([punishOptions, punishableMoves])
                break
                

            # current j is not punishable by i
            # push j until j CAN be punished by i
            while shieldCharMoves[i][1] + attackCharMoves[j][1] > 0:
                punishableMoves.append(attackCharMoves[j])
                j += 1
                if j >= len(attackCharMoves):
                    break
            
            # punishOptions is now the limit of what moves can punish current punishableMoves
            # punishableMoves is the limit of what moves can be punished by current punishOptions

            punishList.append([punishOptions, punishableMoves])
        """

        # Now get the opposite (shield safety of shieldChar's moves)
        try:
            shieldChar = request.GET['Opponent Character']
            attackChar = request.GET['Your Character']
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
                if move.move in ("Jab 1", "Jab", "F-Tilt", "U-Tilt", "D-Tilt", "F-Smash", "D-Smash", "Jab 1 ", "Jab ", "F-Tilt ", "U-Tilt ", "D-Tilt ", "F-Smash ", "D-Smash ", "F-Smash (early)", "D-Smash (early)"):
                    moveName = move.move
                    moveStartupComplete = move.startup
                    moveStartupFrame = int(re.findall(r'\d+', moveStartupComplete)[0])
                    moveFrame = moveStartupFrame + 11
                    shieldCharMoves.append([moveName, moveFrame, moveStartupFrame, moveStartupComplete])
                # aerials add 3 frames
                elif move.move in ("F-Air", "F-Air ", "N-Air", "N-Air ", "B-Air", "B-Air ", "D-Air", "D-Air ", "U-Air", "U-Air ", "Z-Air", "Z-Air ", "N-Air (either Dragon)", "N-Air (Ramram)", "N-Air (Megawatt)"):
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
                    # some up-b are not attacks (e.g. teleport), so just skip
                    if not move.startup:
                        continue
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
            for move in attackCharData:
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
            
            safeList = []
            #if at start there are unpunishable moves
            if shieldCharMoves[0][1] + attackCharMoves[0][1] > 0:
                punishOptions = []
                punishableMoves = []
                # pop from attackCharMoves until punishable
                while shieldCharMoves[0][1] + attackCharMoves[0][1] > 0:
                    punishableMoves.append(attackCharMoves.pop(0))
                safeList.append([punishOptions, punishableMoves])
            
            # end loop when no moves remain
            while shieldCharMoves or attackCharMoves:
                punishOptions = []
                punishableMoves = []

                # if there remains a move that cannot punish anything, just end
                if not attackCharMoves:
                    break

                # move CANNOT be punished OOS if frame disadvantage + startup > 0
                # move CAN be punished OOS if frame disadvantage + startup <= 0

                # pop from shieldCharMoves until attackCharMove cannot be punished
                while shieldCharMoves and shieldCharMoves[0][1] + attackCharMoves[0][1] <= 0:
                    punishOptions.append(shieldCharMoves.pop(0))

                # if no more shieldCharMoves, only attackCharMoves left so put all 
                # remaining attackCharMoves into punishable moves and finish up
                if not shieldCharMoves:
                    while attackCharMoves:
                        punishableMoves.append(attackCharMoves.pop(0))
                    safeList.append([punishOptions, punishableMoves])
                    break
                    
                # current attackCharMove is not punishable by shieldCharMove
                # pop from attackCharMove until it CAN be punished by shieldCharMove
                while attackCharMoves and shieldCharMoves[0][1] + attackCharMoves[0][1] > 0:
                    punishableMoves.append(attackCharMoves.pop(0))
                
                # punishOptions is now the limit of what moves can punish current punishableMoves
                # punishableMoves is the limit of what moves can be punished by current punishOptions

                safeList.append([punishOptions, punishableMoves])

        # Return all moves from each char
        return render(request, 'matchups/matchup.html', {
            'punishList': punishList,
            'safeList': safeList,
            'shieldChar': request.GET['Your Character'],
            'attackChar': request.GET['Opponent Character'],
        })

def MeleeMatchupSearchView(request):
    try:
        shieldChar = request.GET['Your Character']
        attackChar = request.GET['Opponent Character']
        shieldCharData = Meleeoos.objects.filter(character=shieldChar)
        attackCharData = Meleeframedata.objects.filter(character=attackChar)
    except:
        # Error if character names not chosen correctly
        raise Http404("Character name does not exist. Please choose a name from the dropdown.")
    else:
        # get all shield character moves and their first frame OOS
        # [name, frame oos, notes]
        shieldCharMoves = []
        for move in shieldCharData:
            moveName = move.move
            moveFrameComplete = move.frame
            moveFrame = int(re.findall(r'\d+', moveFrameComplete)[0])
            moveNotes = move.notes
            shieldCharMoves.append([moveName, moveFrame, moveFrameComplete, moveNotes])

        # once list is complete, sort by frame oos (least to greatest)
        shieldCharMoves.sort(key = lambda x: x[1])

        # get all attack character moves and parse their frame advantage
        # [name, frame advantage, frame advantage full details]
        attackCharMoves = []
        for move in attackCharData:
            # don't include grab and make sure advantage number exists
            if move.move not in ("Grab", "Grab ", "Rapid Jabs Loop", "Pummel") and move.frame_advantage:
                moveName = move.move
                # get the highest value advantage number
                moveAdvantage = max(list(map(int, re.findall(r'[+-]?\d+', move.frame_advantage))))
                attackCharMoves.append([moveName, moveAdvantage, move.frame_advantage])
        
        # once list is complete, sort by frame advantage (greatest to least)
        attackCharMoves.sort(key = lambda x: x[1], reverse=True)

        # now create lists of which attackChar moves are punishable by which shieldChar moves on shield
        # keep building solution starting from fastest shieldChar moves
        
        punishList = []
        #if at start there are unpunishable moves
        if shieldCharMoves[0][1] + attackCharMoves[0][1] > 0:
            punishOptions = []
            punishableMoves = []
            # pop from attackCharMoves until punishable
            while shieldCharMoves[0][1] + attackCharMoves[0][1] > 0:
                punishableMoves.append(attackCharMoves.pop(0))
            punishList.append([punishOptions, punishableMoves])
        
        # end loop when no moves remain
        while shieldCharMoves or attackCharMoves:
            punishOptions = []
            punishableMoves = []

            # if there remains a move that cannot punish anything, just end
            if not attackCharMoves:
                break

            # move CANNOT be punished OOS if frame disadvantage + startup > 0
            # move CAN be punished OOS if frame disadvantage + startup <= 0

            # pop from shieldCharMoves until attackCharMove cannot be punished
            while shieldCharMoves and shieldCharMoves[0][1] + attackCharMoves[0][1] <= 0:
                punishOptions.append(shieldCharMoves.pop(0))

            # if no more shieldCharMoves, only attackCharMoves left so put all 
            # remaining attackCharMoves into punishable moves and finish up
            if not shieldCharMoves:
                while attackCharMoves:
                    punishableMoves.append(attackCharMoves.pop(0))
                punishList.append([punishOptions, punishableMoves])
                break
                
            # current attackCharMove is not punishable by shieldCharMove
            # pop from attackCharMove until it CAN be punished by shieldCharMove
            while attackCharMoves and shieldCharMoves[0][1] + attackCharMoves[0][1] > 0:
                punishableMoves.append(attackCharMoves.pop(0))
            
            # punishOptions is now the limit of what moves can punish current punishableMoves
            # punishableMoves is the limit of what moves can be punished by current punishOptions

            punishList.append([punishOptions, punishableMoves])


        

        # Now get the opposite (shield safety of shieldChar's moves)
        try:
            shieldChar = request.GET['Opponent Character']
            attackChar = request.GET['Your Character']
            shieldCharData = Meleeoos.objects.filter(character=shieldChar)
            attackCharData = Meleeframedata.objects.filter(character=attackChar)
        except:
            # Error if character names not chosen correctly
            raise Http404("Character name does not exist. Please choose a name from the dropdown.")
        else:
            # get all shield character moves and their first frame OOS
            # [name, frame oos, notes]
            shieldCharMoves = []
            for move in shieldCharData:
                moveName = move.move
                moveFrameComplete = move.frame
                moveFrame = int(re.findall(r'\d+', moveFrameComplete)[0])
                moveNotes = move.notes
                shieldCharMoves.append([moveName, moveFrame, moveFrameComplete, moveNotes])

            # once list is complete, sort by frame oos (least to greatest)
            shieldCharMoves.sort(key = lambda x: x[1])

            # get all attack character moves and parse their frame advantage
            # [name, frame advantage, frame advantage full details]
            attackCharMoves = []
            for move in attackCharData:
                # don't include grab and make sure advantage number exists
                if move.move not in ("Grab", "Grab ", "Rapid Jabs Loop", "Pummel") and move.frame_advantage:
                    moveName = move.move
                    # get the highest value advantage number
                    moveAdvantage = max(list(map(int, re.findall(r'[+-]?\d+', move.frame_advantage))))
                    attackCharMoves.append([moveName, moveAdvantage, move.frame_advantage])
            
            # once list is complete, sort by frame advantage (greatest to least)
            attackCharMoves.sort(key = lambda x: x[1], reverse=True)

            # now create lists of which attackChar moves are punishable by which shieldChar moves on shield
            # keep building solution starting from fastest shieldChar moves
            
            safeList = []
            #if at start there are unpunishable moves
            if shieldCharMoves[0][1] + attackCharMoves[0][1] > 0:
                punishOptions = []
                punishableMoves = []
                # pop from attackCharMoves until punishable
                while shieldCharMoves[0][1] + attackCharMoves[0][1] > 0:
                    punishableMoves.append(attackCharMoves.pop(0))
                safeList.append([punishOptions, punishableMoves])
            
            # end loop when no moves remain
            while shieldCharMoves or attackCharMoves:
                punishOptions = []
                punishableMoves = []

                # if there remains a move that cannot punish anything, just end
                if not attackCharMoves:
                    break

                # move CANNOT be punished OOS if frame disadvantage + startup > 0
                # move CAN be punished OOS if frame disadvantage + startup <= 0

                # pop from shieldCharMoves until attackCharMove cannot be punished
                while shieldCharMoves and shieldCharMoves[0][1] + attackCharMoves[0][1] <= 0:
                    punishOptions.append(shieldCharMoves.pop(0))

                # if no more shieldCharMoves, only attackCharMoves left so put all 
                # remaining attackCharMoves into punishable moves and finish up
                if not shieldCharMoves:
                    while attackCharMoves:
                        punishableMoves.append(attackCharMoves.pop(0))
                    safeList.append([punishOptions, punishableMoves])
                    break
                    
                # current attackCharMove is not punishable by shieldCharMove
                # pop from attackCharMove until it CAN be punished by shieldCharMove
                while attackCharMoves and shieldCharMoves[0][1] + attackCharMoves[0][1] > 0:
                    punishableMoves.append(attackCharMoves.pop(0))
                
                # punishOptions is now the limit of what moves can punish current punishableMoves
                # punishableMoves is the limit of what moves can be punished by current punishOptions

                safeList.append([punishOptions, punishableMoves])

        # Return all moves from each char
        return render(request, 'matchups/meleematchup.html', {
            'punishList': punishList,
            'safeList': safeList,
            'shieldChar': request.GET['Your Character'],
            'attackChar': request.GET['Opponent Character'],
        })

# get out of shield options and shield safety of moves for a specific character
def CharacterView(request):
    try:
        shieldChar = request.GET['Character']
        shieldCharData = Framedata.objects.filter(character=shieldChar)
    except:
        # Error if character names not chosen correctly
        raise Http404("Character name does not exist. Please choose a name from the dropdown.")
    else:
        # get all shield character moves and calculate their first frame OOS
        # [name, frame oos, first frame not oos, frame data]
        shieldCharMoves = []
        for move in shieldCharData:
            # moves that require dropping shield add 11 frames
            if move.move in ("Jab 1", "Jab", "F-Tilt", "U-Tilt", "D-Tilt", "F-Smash", "D-Smash", "Jab 1 ", "Jab ", "F-Tilt ", "U-Tilt ", "D-Tilt ", "F-Smash ", "D-Smash ", "F-Smash (early)", "D-Smash (early)"):
                moveName = move.move
                moveStartupComplete = move.startup
                moveStartupFrame = int(re.findall(r'\d+', moveStartupComplete)[0])
                moveFrame = moveStartupFrame + 11
                shieldCharMoves.append([moveName, moveFrame, moveStartupFrame, moveStartupComplete])
            # aerials add 3 frames
            elif move.move in ("F-Air", "F-Air ", "N-Air", "N-Air ", "B-Air", "B-Air ", "D-Air", "D-Air ", "U-Air", "U-Air ", "Z-Air", "Z-Air ", "N-Air (either Dragon)", "N-Air (Ramram)", "N-Air (Megawatt)"):
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
                # some up-b are not attacks (e.g. teleport), so just skip
                if not move.startup:
                    continue
                moveName = move.move
                moveStartupComplete = move.startup
                moveStartupFrame = int(re.findall(r'\d+', moveStartupComplete)[0])
                moveFrame = moveStartupFrame
                shieldCharMoves.append([moveName, moveFrame, moveStartupFrame, moveStartupComplete])
            #don't include other moves

        # once list is complete, sort by frame oos (least to greatest)
        shieldCharMoves.sort(key = lambda x: x[1])

        # get all attack character (which is same as shielding for character search) moves and parse their frame advantage
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

        # Return all moves from each char
        return render(request, 'matchups/character.html', {
            'oosList': shieldCharMoves,
            'safetyList': attackCharMoves,
            'character': shieldChar,
        })

# get out of shield options and shield safety of moves for a specific melee character
def MeleeCharacterView(request):
    try:
        shieldChar = request.GET['Character']
        shieldCharData = Meleeoos.objects.filter(character=shieldChar) #oos data separate from on block
        attackCharData = Meleeframedata.objects.filter(character=shieldChar)
    except:
        # Error if character names not chosen correctly
        raise Http404("Character name does not exist. Please choose a name from the dropdown.")
    else:
        # get all shield character moves and their first frame OOS
        # [name, frame oos, notes]
        shieldCharMoves = []
        for move in shieldCharData:
            moveName = move.move
            moveFrameComplete = move.frame
            moveFrame = int(re.findall(r'\d+', moveFrameComplete)[0])
            moveNotes = move.notes
            shieldCharMoves.append([moveName, moveFrame, moveFrameComplete, moveNotes])

        # once list is complete, sort by frame oos (least to greatest)
        shieldCharMoves.sort(key = lambda x: x[1])

        # get all attack character moves (which is same as shielding for character search) and parse their frame advantage
        # [name, frame advantage, frame advantage full details]
        attackCharMoves = []
        for move in attackCharData:
            # don't include grab and make sure advantage number exists
            if move.move not in ("Grab", "Grab ", "Rapid Jabs Loop", "Pummel") and move.frame_advantage:
                moveName = move.move
                # get the highest value advantage number
                moveAdvantage = max(list(map(int, re.findall(r'[+-]?\d+', move.frame_advantage))))
                attackCharMoves.append([moveName, moveAdvantage, move.frame_advantage])
        
        # once list is complete, sort by frame advantage (greatest to least)
        attackCharMoves.sort(key = lambda x: x[1], reverse=True)

        # Return all moves from each char
        return render(request, 'matchups/meleecharacter.html', {
            'oosList': shieldCharMoves,
            'safetyList': attackCharMoves,
            'character': shieldChar,
        })