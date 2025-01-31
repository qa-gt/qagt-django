"""QAGT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),
    path('user/', include('qagt_user.urls')),
    path('article/', include('qagt_article.urls')),
    path('admin/', include('qagt_admin.urls')),
    path('report/', include('qagt_report.urls')),
    path('notice/', include('qagt_notice.urls')),
    path('', include('main.urls')),
]

handler404 = "main.views.error_404"
handler500 = "main.views.error_500"
handler410 = "main.views.error_410"
