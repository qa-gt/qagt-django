from django.urls import path

from . import views

urlpatterns = [
    path("article/<int:atc_id>", views.report_article, name='report_article'),
    path("list", views.report_list, name='report_list'),
]
