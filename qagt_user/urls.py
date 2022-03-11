from django.urls import path

from . import views

urlpatterns = [
    path("<int:user_id>", views.user_page, name='user_page'),
    path('login', views.user_login, name='user_login'),
    path('logout', views.user_logout, name='user_logout'),
    path('edit', views.edit_information, name='edit_information'),
]
