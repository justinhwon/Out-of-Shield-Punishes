from django.urls import path

from . import views

app_name = 'matchups'
urlpatterns = [
    path('', views.HomeView.as_view(), name='homepage'),
    path('credits', views.CreditView.as_view(), name='credits'),
    path('about', views.AboutView.as_view(), name='about'),
    path('matchup', views.MatchupSearchView, name='matchup'),
    path('privacypolicy', views.PrivacyView.as_view(), name='privacy'),
    path('termsandconditions', views.TermsView.as_view(), name='terms'),
    path('cookiepolicy', views.CookieView.as_view(), name='cookie'),
]