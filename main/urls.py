from django.urls import path

from . import views

urlpatterns = [
    path('search', views.search, name='search'),
    path('', views.index, name='index'),
    path("article/<int:atc_id>", views.article_page, name='article_page'),
    path("article/delete/<int:atc_id>", views.article_delete, name='article_delete'),
    path("article/read", views.article_read_count, name='article_read_count'),
    path("report/article/<int:atc_id>", views.report_article, name='report_article'),
    path("report/list", views.report_list, name='report_list'),
    path("comment/delete", views.comment_delete, name='comment_delete'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('article/write', views.article_write, name='article_write'),
    path('image-upload', views.image_upload, name='image_upload'),
    path('notice', views.make_notice, name='make_notice'),
    path('admin', views.admin_index, name='admin_index'),
    path('admin/hidded-atc', views.admin_hiddedatc, name='admin_hiddedatc'),
    path('sadmin', views.sadmin_index, name='sadmin_index'),
    path('test', views.test, name='test'),
]
