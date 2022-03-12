import time

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.http import (require_GET, require_http_methods,
                                          require_POST)
from QAGT import get_extra, logger
from QAGT.models import *

# Create your views here.


def admin_index(request):
    if request.method == "POST":
        if request.GET["operation"] == "article-state":
            atc = Articles.objects.get(id=request.POST["atc_id"])
            atc.state = int(request.POST["state"])
            atc.save()
            logger.info(f"{request._user.name}修改了文章{atc}状态为{atc.state}",
                        extra=get_extra(request))
        elif request.GET["operation"] == "article-topic":
            atc = Articles.objects.get(id=request.POST["atc_id"])
            if Topics.objects.filter(id=request.POST["topic"]).exists():
                atc.topic_id = int(request.POST["topic"])
            atc.save()
            logger.info(f"{request._user.name}修改了文章{atc}主题为{atc.topic_id}",
                        extra=get_extra(request))
        elif request.GET["operation"] == "comment-state":
            comments = Comments.objects.filter(under=request.POST["atc_id"],
                                               state__gte=0).order_by("time")
            comment = comments[int(request.POST["floor"]) - 1]
            comment.state = int(request.POST["state"])
            comment.save()
            logger.info(
                f"{request._user.name}修改了评论{comment}状态为{comment.state}",
                extra=get_extra(request))
        return HttpResponseRedirect(request.path)
    return render(request, "admin.html")


def sadmin_index(request):
    if request.method == "POST":
        if request.GET["operation"] == "user-state":
            user = Users.objects.get(id=request.POST["uid"])
            user.state = int(request.POST["state"])
            user.save()
            logger.info(f"{request._user.name}修改了用户{user}状态为{user.state}",
                        extra=get_extra(request))
        if request.GET["operation"] == "user-tags":
            user = Users.objects.get(id=request.POST["uid"])
            user.tags = request.POST["tags"]
            user.save()
            logger.info(f"{request._user.name}修改了用户{user}标签为{user.tags}",
                        extra=get_extra(request))
        return HttpResponseRedirect(request.path)
    return render(request, "sadmin.html")
