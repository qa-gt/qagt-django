import hashlib

from django.shortcuts import render

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, HttpResponseNotFound, Http404, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from QAGT.models import *

# Create your views here.


def get_md5(s):
    m = hashlib.md5()
    m.update(s.encode('utf-8'))
    return m.hexdigest()


def user_login(request):
    if request.method == "POST":
        name = request.POST.get("name")
        password = request.POST.get("password")
        if name and password:
            try:
                user = Users.objects.get(name=name)
                if request.session.get(
                        "user") and request.session["user"] == user.id:
                    user.password = password
                    user.save()
                if user.state <= -3:
                    return HttpResponse("用户已被封禁")
                elif user.password == password:
                    request.session["user"] = user.id
                    return HttpResponse("Success")
                else:
                    return HttpResponse("密码错误")
            except Users.DoesNotExist as e:
                user = Users(name=name, password=password)
                user.save()
                request.session["user"] = user.id
                return HttpResponse("Success")
        else:
            return HttpResponse("用户名或密码不能为空")
    return render(request, "login.html")


def user_logout(request):
    if request.session.get("user"):
        del request.session["user"]
    return HttpResponseRedirect("/")


def user_page(request, user_id):
    if not Users.objects.filter(id=user_id).exists():
        raise Http404("用户不存在")
    user = Users.objects.get(id=user_id)
    page = int(request.GET.get("page") or 1)
    _article = Articles.objects.filter(
        state__gte=-3, author=user).order_by("-id")[(page - 1) * 15:page * 15]
    _top = Articles.objects.filter(state__gte=1, author=user)
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
        request, "user_page.html",
        dict(owner=user,
             articles=article,
             page=page,
             pages=Articles.objects.filter(state__gte=-3, author=user).count()
             // 15 + 1))


def edit_information(request):
    if request.method == "POST":
        values = request.POST.dict()
        if values["sex"] not in ["男", "女"]:
            values["sex"] = "保密"
        if values.get("real_name"):
            values["real_name_md5"] = get_md5(values["real_name"])
        user = Users.objects.get(id=request.session["user"])
        for i, j in values.items():
            user.__setattr__(i, j)
        user.save()
        return HttpResponseRedirect("/user/edit")
    else:
        return render(request, "edit_information.html")
