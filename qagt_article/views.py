import time

from django.http import (Http404, HttpResponse, HttpResponseForbidden,
                         HttpResponseNotAllowed, HttpResponseNotFound,
                         HttpResponseRedirect)
from django.shortcuts import render
from django.views.decorators.http import (require_GET, require_http_methods,
                                          require_POST)
from QAGT import get_extra, logger
from QAGT.models import *
from qagt_notice.pushplus import make_push

# Create your views here.


def article_page(request, atc_id):
    article = Articles.objects.filter(id=atc_id)
    if not article.exists() or article[0].state <= -4:
        return HttpResponseNotFound("文章不存在！")
    article = article[0]

    if request.method == "POST":
        if request._user.state <= -2:
            return HttpResponseForbidden("您的账号已被限制发言")
        Comments.objects.create(author=request._user,
                                under=article,
                                content=request.POST["comment"],
                                time=int(time.time()))
        if request._user != article.author:
            Notices.objects.get_or_create(
                recipient=article.author,
                title="有人评论了你的文章",
                content=f"用户 {request._user.name} 在你的文章《{article.title}》下发表了评论",
                time=int(time.time()),
                url=f"/article/{article.id}")
            logger.info(f"{request._user} 评论了《{article.title}》",
                        extra=get_extra(request))
            make_push(request, article.author)
        return HttpResponse("Success")

    _comments = article.comments.filter(state__gte=0).order_by("time")
    comment = []
    top = []
    for i in _comments:
        comment.append(i)
        if i.state == 1:
            top.append(comment[-1])
    likes = article.likes.all()
    return render(
        request, "article.html",
        dict(article=article,
             comment=comment,
             top=top,
             likes=likes,
             owner=article.author))


@require_POST
def article_read_count(request):
    try:
        article = Articles.objects.get(id=request.POST["id"])
        article.read_count += 1
        article.save()
        logger.info(f"阅读了《{article}》", extra=get_extra(request))
        return HttpResponse("Success")
    except Articles.DoesNotExist:
        return HttpResponseNotFound("文章不存在！")


def article_write(request):
    if request.method == "POST":
        if request._user.state <= -1:
            return HttpResponseForbidden("您的账号已被限制操作贴子")
        if request.GET["update"] == "true":
            try:
                atc = Articles.objects.get(id=request.GET["id"])
                atc.title = request.POST["title"]
                atc.content = request.POST["content"]
                atc.topic_id = request.POST["topic"] if Topics.objects.filter(
                    id=request.POST["topic"]).exists() else 0
                atc.update_time = int(time.time())
                atc.save()
                logger.info(f"{request._user} 更新了《{atc}》",
                            extra=get_extra(request))
                return HttpResponse(atc.id)
            except Articles.DoesNotExist:
                return HttpResponseNotFound("文章不存在！")
        t = int(time.time())
        Articles.objects.create(
            author=request._user,
            title=request.POST["title"],
            content=request.POST["content"],
            update_time=t,
            create_time=t,
            topic_id=int(request.POST["topic"]) if Topics.objects.filter(
                id=request.POST["topic"]).exists() else 0)
        atc = Articles.objects.get(author=request._user, update_time=t)
        logger.info(f"{request._user} 发表了《{atc}》", extra=get_extra(request))
        return HttpResponse(atc.id)

    if request.GET.get("id") and request.GET["id"].isdigit():
        try:
            data = Articles.objects.get(id=int(request.GET["id"]))
            if request.session["user"] == data.author.id:
                return render(request, "article-write.html", {"data": data})
        except:
            ...

    return render(request, "article-write.html", {"data": None})


def article_delete(request, atc_id):
    if request._user.state <= -1:
        return HttpResponseForbidden("您的账号已被限制操作贴子")
    atc = Articles.objects.get(id=atc_id)
    if atc.author != request._user:
        return HttpResponseForbidden("您不是该文章作者！")
    try:
        atc.state = -5
        atc.save()
        logger.info(f"{request._user} 删除了《{atc}》", extra=get_extra(request))
    except Exception as e:
        return HttpResponseRedirect(f"/article/{atc_id}")
    return HttpResponseRedirect(f"/user/{request._user.id}")


@require_POST
def article_like(request):
    Likes.objects.get_or_create(user=request._user,
                                article_id=request.POST["id"])
    logger.info(
        f"{request._user} 点赞了《{Articles.objects.get(id=request.POST['id'])}》",
        extra=get_extra(request))
    return HttpResponse("Success")


def comment_delete(request):
    if request.method == "POST":
        try:
            comment = Comments.objects.get(id=request.POST["cid"])
            if comment.author == request._user:
                comment.state = -2
                comment.save()
                logger.info(f"{request._user} 删除了评论《{comment}》",
                            extra=get_extra(request))
                return HttpResponse("Success")
            else:
                return HttpResponseForbidden("您不是该评论作者！")
        except Comments.DoesNotExist:
            return HttpResponse("评论不存在！")
    return HttpResponse("请求错误！")


def search_page(request):
    searching = bool(request.GET.get("keyword"))
    articles = []
    page = pages = 0
    if searching:
        page = int(request.GET.get("page") or 1)
        atc_list = Articles.objects.filter(
            title__icontains=request.GET["keyword"],
            state__gte=-3).order_by("-id")
        pages = atc_list.count() // 15 + 1
        articles = atc_list[(page - 1) * 15:page * 15]
    return render(
        request, "search.html", {
            "searching": searching,
            "page": page,
            "pages": pages,
            "articles": articles,
            "keyword": request.GET.get("keyword")
        })


def topic_page(request):
    page = int(request.GET.get("page") or 1)
    topic = request.GET.get("id")
    if type(topic) == int or type(topic) == str and topic.isdigit():
        topic = int(topic)
    else:
        topic = 0

    topics = Topics.objects.filter(state__gte=0).order_by("id")
    topic = Topics.objects.get(id=topic)

    _article = topic.articles.filter(
        state__gte=-1).order_by("-id")[(page - 1) * 15:page * 15]
    _top = topic.articles.filter(state__gte=2)

    article = []
    top = []
    for i in _top:
        i.title = "【置顶】" + i.title
        top.append(i)
    for i in _article:
        if i not in top:
            article.append(i)
    article = top + article
    return render(
        request, "topic.html", {
            "topic": topic,
            "topics": topics,
            "page": page,
            "pages": topic.articles.filter(state__gte=-1).count() // 15 + 1,
            "articles": article
        })


def topic_list(request):
    topics = Topics.objects.filter(state__gte=0).order_by("id")
    return render(request, "topic_list.html", {"topics": topics})
