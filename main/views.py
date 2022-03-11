import os
import time

from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from QAGT.models import *
from QAGT.settings import STATIC_ROOT, STATICFILES_DIRS, QAGT_SERVER

thisDir = os.path.dirname(os.path.abspath(__file__))

infos = {"上次数据更新时间戳": 0}
start_info = {"time": int(time.time()), "request_cnt": 0}


def format_time(s=time.time()):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(s))


def dashboard(request):
    global infos
    infos["注册用户数"] = Users.objects.all().count()
    infos["文章数"] = Articles.objects.all().count()
    infos["评论数"] = Comments.objects.all().count()
    infos["本次服务器启动时间"] = format_time(start_info["time"])
    t = int(time.time() - start_info["time"])
    infos[
        "本次启动稳定运行时长"] = f"{t // 86400}天{t % 86400 // 3600}小时{t % 3600 // 60}分钟{t % 60}秒"
    infos["本次启动后总请求数"] = start_info["request_cnt"]
    return render(request, "dashboard.html", {"data": infos})


def index(request):
    page = int(request.GET.get("page") or 1)
    _article = Articles.objects.filter(
        state__gte=0).order_by("-id")[(page - 1) * 15:page * 15]
    _top = Articles.objects.filter(state__gte=3).order_by("-id")
    article = []
    top = []
    for i in _top:
        i.title = "【置顶】" + i.title
        top.append(i)
    for i in _article:
        if i not in top:
            article.append(i)
    article = top + article
    return render(
        request, "index.html", {
            "articles": article,
            "page": page,
            "pages": Articles.objects.filter(state__gte=0).count() // 15 + 1,
            "footer": True
        })


@require_POST
def image_upload(request):
    file = request.FILES["file"]
    if file.size > 1024 * 1024 * 5:
        return HttpResponse("文件过大！", status=400)
    name = f"{request.session['user']}_{time.time()}.{file.name.split('.')[-1]}"
    if QAGT_SERVER == "PRODUCTION":
        path = f"{STATIC_ROOT}/article_images/{name}"
    else:
        path = f"{STATICFILES_DIRS[0]}/article_images/{name}"
    with open(path, 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)
    return HttpResponse(name)


def error_404(request, exception):
    return render(request, "404.html")


def error_500(request):
    return render(request, "500.html")
