import random
import re
import string

from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect

from QAGT.models import *


def random_str(length=32):
    return ''.join(
        random.choice(string.ascii_letters + string.digits)
        for _ in range(length))


class LoginRequired:
    requires_list = {
        "GET": [
            "/article/write", "/article/delete/", "/user/logout", "/user/edit",
            "/notice/", "/admin/", "/report/"
        ],
        "POST": [
            "/article/^[0-9]", "/article/write", "/article/delete/",
            "/article/like", "/user/edit", "/notice/", "/admin/", "/report/"
        ]
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # 检查是否已经登录
        if request.session.get("user", None):
            # 已经登录，检查是否被封号
            request.__setattr__("_user",
                                Users.objects.get(id=request.session["user"]))
            if request._user.state == -3:
                request.session.pop("user")
                return HttpResponseRedirect("/")
        else:
            # 未登录，正则检查本次请求是否需要登录
            for i in self.requires_list[request.method]:
                if re.match(i, request.path):
                    if request.method == "GET":
                        return HttpResponseRedirect("/user/login?next=" + (
                            request.headers.get("Referer") or request.path))
                    elif request.method == "POST":
                        return HttpResponseForbidden("请先登录")

        # 设置客户端key
        if not request.session.get("key", None):
            request.session["key"] = random_str(16)

        response = self.get_response(request)

        if request.session.get(
                "user") and request.method == "GET" and request.path in ["/"]:
            request._user.notices.filter(state=0).update(state=1)

        # 如果客户端cookie中没有key则设置
        if not request.COOKIES.get("key", None):
            response.set_cookie("key", request.session["key"])

        return response
