import time

from QAGT.settings import DEBUG, QAGT_SERVER


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
    }
