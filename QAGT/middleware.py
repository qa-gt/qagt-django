import base64
import hashlib
import random
import re
import string

import main.views
from django.http import (HttpResponse, HttpResponseForbidden,
                         HttpResponseRedirect)
from django.utils.datastructures import MultiValueDictKeyError

import django.contrib.sessions.middleware
from .models import *

signs = []


def random_str(length=32):
    return ''.join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(length))


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
            elif view == "article_read_count":
                result = post_check(
                    [str(request.POST["id"]), request.session["key"]],
                    "read_count",
                    request.POST["sign"],
                    save=False)
        except MultiValueDictKeyError:
            return HttpResponseForbidden("缺少签名参数")
        if result:
            return HttpResponseForbidden(result)

    def __call__(self, request):
        response = self.get_response(request)
        return response


class LoginRequired:
    requires_list = {
        "GET": [
            "/article/write", "/article/delete/", "/user/logout", "/user/edit",
            "/notice/", "/admin/"
        ],
        "POST": [
            "/article/^[0-9]", "/article/write", "/article/delete/",
            "/user/edit", "/notice/", "/report/", "/admin/"
        ]
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 检查是否已经登录
        if request.session.get("user", None):
            # 已经登录，检查是否被封号
            if Users.objects.get(id=request.session["user"]).state == -3:
                request.session.pop("user")
                return HttpResponseRedirect("/")
        else:
            # 未登录，正则检查本次请求是否需要登录
            for i in self.requires_list[request.method]:
                if re.match(i, request.path):
                    if request.method == "GET":
                        return HttpResponseRedirect(
                            "/user/login?next=" +
                            request.headers.get("Referer") or request.path)
                    elif request.method == "POST":
                        return HttpResponseForbidden("请先登录")

        # 设置客户端key
        if not request.session.get("key", None):
            request.session["key"] = random_str(16)

        response = self.get_response(request)

        # 如果客户端cookie中没有key则设置
        if not request.COOKIES.get("key", None):
            response.set_cookie("key", request.session["key"])

        return response


class CheckMethod:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 检查请求方法
        if request.method not in ["GET", "POST"]:
            return HttpResponse("请求方法错误: " + request.method, status=405)

        # 检查User-Agent头和POST请求的Referer头
        if not request.headers.get("User-Agent") or not any(
                i in request.headers["User-Agent"]
                for i in ['Chrome', 'Safari', 'Mozilla', 'Firefox']):
            return HttpResponseForbidden("请求校验失败")
        if request.method == "POST":
            if not request.headers.get("Referer"):
                return HttpResponseForbidden("请求校验失败")

        # 获取响应数据
        response = self.get_response(request)

        return response
