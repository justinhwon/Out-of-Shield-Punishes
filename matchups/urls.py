from django.urls import path

from . import views

app_name = 'matchups'
urlpatterns = [
    path('', views.HomeView.as_view(), name='homepage'),
]