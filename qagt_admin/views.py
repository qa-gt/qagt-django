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
        if request.GET["operation"] == "comment-state":
            comments = Comments.objects.filter(under=request.POST["atc_id"],
                                               state__gte=0).order_by("time")
            comment = comments[int(request.POST["floor"]) - 1]
            comment.state = int(request.POST["state"])
            comment.save()
        return HttpResponseRedirect(request.path)
    return render(request, "admin.html")


def admin_hiddedatc(request):
    if not request.session["user"]["admin"]:
        raise HttpResponseForbidden
    _data = mysql.run_code(
        "SELECT `id`, `title`, `from`, `hide` FROM articles WHERE `hide`>=1 ORDER BY `id` DESC LIMIT 200;"
    )
    data = []
    for i in _data:
        data.append({
            "id": i[0],
            "title": i[1],
            "from": users.get_by_id(i[2]),
            "hide": i[3]
        })
    return render(request, "admin_hiddedatc.html", {"data": data})


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