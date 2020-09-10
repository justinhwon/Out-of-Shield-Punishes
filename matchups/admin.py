from django.contrib import admin

from .models import Framedata, Meleeframedata, Meleeoos

# Register your models here.
class FramedataAdmin(admin.ModelAdmin):
    list_display = ['character', 'move', 'startup', 'advantage']
class MeleeframedataAdmin(admin.ModelAdmin):
    list_display = ['character', 'move', 'active_hits', 'frame_advantage']
class MeleeoosAdmin(admin.ModelAdmin):
    list_display = ['character', 'move', 'frame', 'notes']

admin.site.register(Framedata, FramedataAdmin)
admin.site.register(Meleeframedata, MeleeframedataAdmin)
admin.site.register(Meleeoos, MeleeoosAdmin)