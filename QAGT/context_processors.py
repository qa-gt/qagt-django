import time

from QAGT.models import Users


def global_context(request):
    return {
        "user":
        request.session.get("user", None)
        and Users.objects.get(id=request.session["user"]),
        "logined":
        bool(request.session.get("user", None)),
        "title":
        "QA瓜田",
        "format_time": lambda x: time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x))
    }
