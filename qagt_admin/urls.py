from django.urls import path

from qagt_admin import views

urlpatterns = [
    path('', views.admin_index, name='admin_index'),
    path('super', views.sadmin_index, name='sadmin_index'),
]
