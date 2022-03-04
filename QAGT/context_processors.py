from QAGT.models import Users


def global_context(request):
    return {
        "user":
        request.session.get("user", None)
        and Users.objects.get(id=request.session["user"]),
        "logined":
        bool(request.session.get("user", None)),
        "title":
        "QA瓜田"
    }
