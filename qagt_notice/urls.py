from django.urls import path

from . import views

urlpatterns = [
    path('make', views.make_notice, name='make_notice'),
]
