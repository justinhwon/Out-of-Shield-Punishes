from django.urls import path

from . import views

app_name = 'matchups'
urlpatterns = [
    path('', views.HomeView.as_view(), name='homepage'),
    path('credits', views.CreditView.as_view(), name='credits'),
    path('about', views.AboutView.as_view(), name='about')
]