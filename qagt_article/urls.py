from django.urls import path

from qagt_article import views

urlpatterns = [
    path("<int:atc_id>", views.article_page, name='article_page'),
    path("delete/<int:atc_id>", views.article_delete, name='article_delete'),
    path("read", views.article_read_count, name='article_read_count'),
    path('write', views.article_write, name='article_write'),
    path("comment/delete", views.comment_delete, name='comment_delete'),
    path('search', views.search, name='search'),
]
