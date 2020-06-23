from django.contrib import admin

from .models import Framedata

# Register your models here.
class FramedataAdmin(admin.ModelAdmin):
    list_display = ['character', 'move', 'startup', 'advantage']

admin.site.register(Framedata, FramedataAdmin)