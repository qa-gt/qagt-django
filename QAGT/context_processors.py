import time

from .settings import DEBUG, QAGT_SERVER
from .models import *


def global_context(request):
    return {
        "user":
        request._user if hasattr(request, '_user') else None,
        "logined":
        bool(request.session.get("user", None)),
        "title":
        "QA瓜田",
        "format_time":
        lambda x: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x))
        if type(x) == int else "未知时间",
        "QAGT_SERVER":
        QAGT_SERVER,
        "notice":
        Notices.objects.filter(recipient=request._user).order_by("-id")[:10]
        if hasattr(request, '_user') else [],
    }
