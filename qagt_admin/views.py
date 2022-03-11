import time

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, HttpResponseNotFound, Http404, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from QAGT.models import *

# Create your views here.


def admin_index(request):
    if request.method == "POST":
        if request.GET["operation"] == "article-state":
            atc = Articles.objects.get(id=request.POST["atc_id"])
            atc.state = int(request.POST["state"])
            atc.save()
        elif request.GET["operation"] == "article-topic":
            atc = Articles.objects.get(id=request.POST["atc_id"])
            if Topics.objects.filter(id=request.POST["topic"]).exists():
                atc.topic_id = int(request.POST["topic"])
            atc.save()
        elif request.GET["operation"] == "comment-state":
            comments = Comments.objects.filter(under=request.POST["atc_id"],
                                               state__gte=0).order_by("time")
            comment = comments[int(request.POST["floor"]) - 1]
            comment.state = int(request.POST["state"])
            comment.save()
        return HttpResponseRedirect(request.path)
    return render(request, "admin.html")


def sadmin_index(request):
    if request.method == "POST":
        if request.GET["operation"] == "user-state":
            user = Users.objects.get(id=request.POST["uid"])
            user.state = int(request.POST["state"])
            user.save()
        if request.GET["operation"] == "user-tags":
            user = Users.objects.get(id=request.POST["uid"])
            user.tags = request.POST["tags"]
            user.save()
        return HttpResponseRedirect(request.path)
    return render(request, "sadmin.html")