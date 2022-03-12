from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('image-upload', views.image_upload, name='image_upload'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('music-url', views.get_music_url, name='get_music_url'),
]
