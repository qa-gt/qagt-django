import time

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseNotFound
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from QAGT.models import *
from QAGT import get_extra, logger


@require_POST
def report_article(request, atc_id):
    Reports.objects.get_or_create(reporter=request._user,
                                  article_id=atc_id,
                                  time=int(time.time()))
    logger.info(f"{request._user} 举报了文章ID={atc_id}", extra=get_extra(request))
    return HttpResponse("Success")


def report_list(request):
    if request.method == "POST":
        try:
            report = Reports.objects.get(id=request.GET["id"])
            report.state = -1 if request.GET["operation"] == "accept" else 1
            report.operator_id = request.session["user"]
            report.operate_time = int(time.time())
            report.save()
            logger.info(f"{request._user} 操作了举报：{report}",
                        extra=get_extra(request))
        except Reports.DoesNotExist:
            return HttpResponseNotFound("举报不存在！")
        return HttpResponseRedirect(request.path)
    return render(request, "report_list.html",
                  {"reports": Reports.objects.filter(state=0)})
