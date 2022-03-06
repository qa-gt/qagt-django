import base64
import hashlib
import re

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect
from django.utils.datastructures import MultiValueDictKeyError

from .models import *
import main.views

signs = []


def get_md5(s):
    m = hashlib.md5()
    m.update(s.encode('utf-8'))
    return m.hexdigest()


def get_base64(s):
    return str(base64.b64encode(s.encode("utf-8")), "utf-8")


def post_check(data, scene, sign, save=True):
    if sign in signs:
        return "签名已存在"
    ans = ""
    for i in data:
        ans += get_md5(get_base64(get_md5(str(i))))
    ans += scene
    if get_md5(ans) != sign:
        return "签名错误"
    if save:
        signs.append(sign)
    return None


class PostCheckV1:
    def __init__(self, get_response):
        self.get_response = get_response

    def process_view(self, request, view_func, view_args, view_kwargs):
        # 统计的临时解决方案
        main.views.start_info['request_cnt'] += 1

        if request.method == "GET":
            return None
        view = view_func.__name__
        result = None
        try:
            if view == "article_write":
                result = post_check([
                    Users.objects.get(id=request.session["user"]).name,
                    request.POST["title"], request.POST["content"]
                ], "article", request.POST["sign"])
            elif view == "article_page":
                result = post_check([
                    Users.objects.get(id=request.session["user"]).name,
                    view_kwargs["atc_id"], request.POST["comment"]
                ], "comment", request.POST["sign"])
            elif view == "user_login":
                result = post_check(
                    [request.POST["name"], request.POST["password"]],
                    "login",
                    request.POST["sign"],
                    save=False)
        except MultiValueDictKeyError:
            return HttpResponseForbidden("缺少sign参数")
        if result:
            return HttpResponseForbidden(result)

    def __call__(self, request):
        response = self.get_response(request)
        return response


class LoginRequired:
    requires_list = {
        "GET": [
            "/django-admin/", "/article/write", "/article/delete/",
            "/user/logout", "/user/edit", "/notice/", "/admin/"
        ],
        "POST": [
            "/django-admin/", "/article/", "/article/write",
            "/article/delete/", "/user/edit", "/notice/", "/report/", "/admin/"
        ]
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.session.get("user", None):
            return None
        for i in self.requires_list[request.method]:
            if re.match(i, request.path):
                return HttpResponseRedirect("/user/login?next=" + request.path)
        return None

    def __call__(self, request):
        response = self.get_response(request)
        return response


class CheckMethod:
    def __init__(self, get_response):
        self.get_response = get_response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if request.method in ["GET", "POST"]:
            return None
        return HttpResponse("请求方法错误: " + request.method, status=405)

    def __call__(self, request):
        response = self.get_response(request)
        return response
