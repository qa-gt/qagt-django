from django.http import HttpResponseForbidden


class TestServerChecker:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.COOKIES.get("qagtyyds", None) != "qagtyyds":
            return HttpResponseForbidden("就你这个大**还想访问我的测试网站？")
        return self.get_response(request)
