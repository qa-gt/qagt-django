import time

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from QAGT.models import *


@require_POST
def report_article(request, atc_id):
    if request._user.reports.filter(article_id=atc_id).exists():
        return HttpResponse("您已经举报过该文章")
    Reports.objects.create(reporter_id=request.session["user"],
                           article_id=atc_id,
                           time=int(time.time()))
    return HttpResponse("Success")


def report_list(request):
    if request.method == "POST":
        try:
            report = Reports.objects.get(id=request.GET["id"])
            report.state = -1 if request.GET["operation"] == "accept" else 1
            report.operator_id = request.session["user"]
            report.operate_time = int(time.time())
            report.save()
        except Reports.DoesNotExist:
            return HttpResponseNotFound("举报不存在！")
        return HttpResponseRedirect(request.path)
    return render(request, "report_list.html",
                  {"reports": Reports.objects.filter(state=0)})
