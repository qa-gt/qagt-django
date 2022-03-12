import time

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from QAGT.models import *
from QAGT import get_extra, logger
from .pushplus import make_push


def make_notice(request):
    if request.POST["at"] == "article":
        cmt = Comments.objects.get(id=request.POST["cid"])
        atc = cmt.under
        Notices.objects.get_or_create(
            recipient=cmt.author,
            title="有人@你",
            content=f"用户 {request._user.name} 在文章《{atc.title}》的评论区@了你",
            time=int(time.time()),
            url=f"/article/{atc.id}")
        logger.info(f"{request._user} 在文章《{atc}》的评论区@了{cmt.author}",
                    extra=get_extra(request))
        make_push(request, cmt.author)
    return HttpResponse("Success")
