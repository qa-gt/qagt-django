from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect


def make_notice(request):
    # to = request.GET["to"]
    # at = request.GET["at"]
    # if at == "article":
    #     notices.add(
    #         to,
    #         f"{request.session['user']['name']}在文章：{articles.get(request.GET['atc'])['title']}下提到了你",
    #         f"/article/{request.GET['atc']}")
    return HttpResponse("Success")
