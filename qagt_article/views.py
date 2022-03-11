import time

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, HttpResponseNotFound, Http404, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods, require_GET, require_POST

from QAGT.models import *

# Create your views here.


def article_page(request, atc_id):
    article = Articles.objects.get(id=atc_id)
    if article.state <= -4:
        return HttpResponseNotFound("文章不存在！")
    if request.method == "POST":
        if Users.objects.get(id=request.session["user"]).state <= -2:
            return HttpResponseForbidden("您的账号已被限制发言")
        Comments.objects.create(author_id=request.session["user"],
                                under_id=atc_id,
                                content=request.POST["comment"],
                                time=int(time.time()))
        return HttpResponse("Success")

    try:
        _comments = Comments.objects.filter(under=article,
                                            state__gte=0).order_by("time")
        comment = []
        top = []
        for i in _comments:
            comment.append(i)
            if i.state == 1:
                top.append(comment[-1])
        likes = Likes.objects.filter(article=article)
        return render(
            request, "article.html",
            dict(article=article,
                 comment=comment,
                 top=top,
                 likes=likes,
                 owner=article.author))
    except Articles.DoesNotExist:
        return HttpResponseNotFound("文章不存在！")


@require_POST
def article_read_count(request):
    try:
        article = Articles.objects.get(id=request.POST["id"])
        article.read_count += 1
        article.save()
    except Articles.DoesNotExist:
        return HttpResponseNotFound("文章不存在！")
    return HttpResponse("Success")


def article_write(request):
    if request.method == "POST":
        if Users.objects.get(id=request.session["user"]).state <= -1:
            return HttpResponseForbidden("您的账号已被限制操作贴子")
        if request.GET["update"] == "true":
            atc = Articles.objects.get(id=request.GET["id"])
            atc.title = request.POST["title"]
            atc.content = request.POST["content"]
            if Topics.objects.filter(id=request.POST["topic"]).exists():
                atc.topic_id = int(request.POST["topic"])
            atc.update_time = int(time.time())
            atc.save()
            return HttpResponse(atc.id)
        t = int(time.time())
        Articles.objects.create(
            author=Users.objects.get(id=request.session["user"]),
            title=request.POST["title"],
            content=request.POST["content"],
            update_time=t,
            create_time=t,
            topic_id=int(request.POST["topic"]) if Topics.objects.filter(
                id=request.POST["topic"]).exists() else 0)
        return HttpResponse(
            Articles.objects.get(author_id=request.session["user"],
                                 update_time=t).id)

    if request.GET.get("id") and request.GET["id"].isdigit():
        try:
            data = Articles.objects.get(id=int(request.GET["id"]))
            if request.session["user"] == data.author.id:
                return render(request, "article-write.html", {"data": data})
        except:
            ...

    return render(request, "article-write.html", {"data": None})


def article_delete(request, atc_id):
    if Users.objects.get(id=request.session["user"]).state <= -1:
        return HttpResponseForbidden("您的账号已被限制操作贴子")
    atc = Articles.objects.get(id=atc_id)
    if atc.author.id != request.session["user"]:
        return HttpResponseForbidden("您不是该文章作者！")
    try:
        atc.state = -5
        atc.save()
    except Exception as e:
        return HttpResponseRedirect(f"/article/{atc_id}")
    return HttpResponseRedirect(f"/user/{request.session['user']}")


@require_POST
def article_like(request):
    Likes.objects.get_or_create(user=request._user,
                                article_id=request.POST["id"])
    return HttpResponse("Success")


def comment_delete(request):
    if request.method == "POST":
        try:
            comment = Comments.objects.get(id=request.POST["cid"])
            if comment.author_id == request.session["user"]:
                comment.state = -2
                comment.save()
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

    _article = topic.articles.filter(state__gte=-1)[(page - 1) * 15:page * 15]
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
            "page": 1,
            "pages": 1,
            "articles": article
        })


def topic_list(request):
    topics = Topics.objects.filter(state__gte=0).order_by("id")
    return render(request, "topic_list.html", {"topics": topics})
