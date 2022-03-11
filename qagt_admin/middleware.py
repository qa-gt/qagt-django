import re

from django.http import HttpResponse, HttpResponseForbidden

from QAGT.models import *


class AdminRequired:
    requires_list = {1: ["/admin", "/report/list"], 2: ["/admin/sadmin"]}

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for i, j in self.requires_list.items():
            if hasattr(request, "_user") and i <= request._user.state:
                continue
            for k in j:
                if re.match(k, request.path):
                    return HttpResponseForbidden("此页面需要更高用户等级访问")

        response = self.get_response(request)

        return response
