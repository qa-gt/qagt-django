from django.urls import path

from . import views

urlpatterns = [
    path('search', views.search, name='search'),
    path('', views.index, name='index'),
    path("user/<int:user_id>", views.user_page, name='user_page'),
    path("article/<int:atc_id>", views.article_page, name='article_page'),
    path("article/delete/<int:atc_id>", views.article_delete, name='article_delete'),
    path('dashboard', views.dashboard, name='dashboard'),
    path('user/login', views.user_login, name='user_login'),
    path('user/logout', views.user_logout, name='user_logout'),
    path('article/write', views.article_write, name='article_write'),
    path('image-upload', views.image_upload, name='image_upload'),
    path('notice', views.make_notice, name='make_notice'),
    path('user/edit', views.edit_information, name='edit_information'),
    path('admin', views.admin_index, name='admin_index'),
    path('admin/reports', views.admin_reports, name='admin_reports'),
    path('admin/hidded-atc', views.admin_hiddedatc, name='admin_hiddedatc'),
    path('admin/top-atc', views.admin_topatc, name='admin_topatc'),
    path('admin/untop-atc', views.admin_untopatc, name='admin_untopatc'),
    path('admin/top-cmt', views.admin_topcmt, name='admin_topcmt'),
    path('admin/untop-cmt', views.admin_untopcmt, name='admin_untopcmt'),
    path('admin/hide-atc', views.admin_hideatc, name='admin_hideatc'),
    path('admin/del-atc', views.admin_delatc, name='admin_delatc'),
    path('admin/del-cmt', views.admin_delcmt, name='admin_delcmt'),
    path('sadmin', views.sadmin_index, name='sadmin_index'),
    path('sadmin/del-user', views.sadmin_deluser, name='sadmin_deluser'),
    path('sadmin/add-admin', views.sadmin_addadmin, name='sadmin_addadmin'),
    path('sadmin/add-tag', views.sadmin_addtag, name='sadmin_addtag'),
    path('sadmin/rm-admin', views.sadmin_rmdamin, name='sadmin_rmdamin'),
    path('test', views.test, name='test'),
]
