def global_context(request):
    return {
        # "user": {
        #     "id": 1,
        #     "name": "admin",
        #     "introduction": "I am admin"
        # },
        "user": request.session.get("user", None),
        "logined": bool(request.session.get("user", None)),
        "title": "QA瓜田"
    }
