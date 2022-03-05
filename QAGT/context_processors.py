import time

from QAGT.models import Users
from QAGT.settings import DEBUG, QAGT_SERVER


def global_context(request):
    return {
        "user":
        request.session.get("user", None)
        and Users.objects.get(id=request.session["user"]),
        "logined":
        bool(request.session.get("user", None)),
        "title":
        "QA瓜田",
        "format_time":
        lambda x: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x))
        if type(x) == int else "未知时间",
        "QAGT_SERVER":
        QAGT_SERVER,
    }
