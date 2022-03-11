import hashlib
import os
import time

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, HttpResponseNotFound, Http404, HttpResponseNotAllowed
from django.views.decorators.http import require_http_methods, require_GET, require_POST
from QAGT.models import *
from QAGT.settings import STATIC_ROOT, STATICFILES_DIRS, QAGT_SERVER

thisDir = os.path.dirname(os.path.abspath(__file__))
signs = []

infos = {"上次数据更新时间戳": 0}
start_info = {"time": int(time.time()), "request_cnt": 0}


def get_md5(s):
    m = hashlib.md5()
    m.update(s.encode('utf-8'))
    return m.hexdigest()


def format_time(s=time.time()):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(s))


def dashboard(request):
    global infos
    infos["注册用户数"] = Users.objects.all().count()
    infos["文章数"] = Articles.objects.all().count()
    infos["评论数"] = Comments.objects.all().count()
    infos["本次服务器启动时间"] = format_time(start_info["time"])
    t = int(time.time() - start_info["time"])
    infos[
        "本次启动稳定运行时长"] = f"{t // 86400}天{t % 86400 // 3600}小时{t % 3600 // 60}分钟{t % 60}秒"
    infos["本次启动后总请求数"] = start_info["request_cnt"]
    return render(request, "dashboard.html", {"data": infos})


def search(request):
    user = int(request.GET.get("user") or 0)
    return HttpResponse("搜索功能暂未开放")


def index(request):
    page = int(request.GET.get("page") or 1)
    _article = Articles.objects.filter(
        state__gte=0).order_by("-id")[(page - 1) * 15:page * 15]
    _top = Articles.objects.filter(state__gte=3).order_by("-id")
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
        request, "index.html", {
            "articles": article,
            "page": page,
            "pages": Articles.objects.filter(state__gte=0).count() // 15 + 1,
            "footer": True
        })


def article_write(request):
    if request.method == "POST":
        if Users.objects.get(id=request.session["user"]).state <= -1:
            return HttpResponseForbidden("您的账号已被限制操作贴子")
        if request.GET["update"] == "true":
            atc = Articles.objects.get(id=request.GET["id"])
            atc.title = request.POST["title"]
            atc.content = request.POST["content"]
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
        )
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
def image_upload(request):
    file = request.FILES["file"]
    if file.size > 1024 * 1024 * 5:
        return HttpResponse("文件过大！", status=400)
    name = f"{request.session['user']}_{time.time()}.{file.name.split('.')[-1]}"
    if QAGT_SERVER == "PRODUCTION":
        path = f"{STATIC_ROOT}/article_images/{name}"
    else:
        path = f"{STATICFILES_DIRS[0]}/article_images/{name}"
    with open(path, 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)
    return HttpResponse(name)


def make_notice(request):
    # to = request.GET["to"]
    # at = request.GET["at"]
    # if at == "article":
    #     notices.add(
    #         to,
    #         f"{request.session['user']['name']}在文章：{articles.get(request.GET['atc'])['title']}下提到了你",
    #         f"/article/{request.GET['atc']}")
    return HttpResponse("Success")


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
        return render(
            request, "article.html",
            dict(article=article,
                 comment=comment,
                 top=top,
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





@require_POST
def report_article(request, atc_id):
    if Reports.objects.filter(reporter_id=request.session["user"],
                              article_id=atc_id).count():
        return HttpResponse("您已经举报过该文章")
    Reports.objects.create(reporter_id=request.session["user"],
                           article_id=atc_id,
                           time=int(time.time()))
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


def report_list(request):
    if request.method == "POST":
        try:
            report = Reports.objects.get(id=request.GET["id"])
            report.state = -1 if request.GET["operation"] == "accept" else 1
            report.operator_id = request.session["user"]
            report.operate_time = int(time.time())
            report.save()
        except Reports.DoesNotExist:
            return HttpResponseNotFound("举报不存在！")
        return HttpResponseRedirect(request.path)
    return render(request, "report_list.html",
                  {"reports": Reports.objects.filter(state=0)})


def admin_index(request):
    if request.method == "POST":
        if request.GET["type"] == "article":
            atc = Articles.objects.get(id=request.POST["atc_id"])
            atc.state = int(request.POST["state"])
            atc.save()
        if request.GET["type"] == "comment":
            comments = Comments.objects.filter(under=request.POST["atc_id"],
                                               state__gte=0).order_by("time")
            comment = comments[int(request.POST["floor"]) - 1]
            comment.state = int(request.POST["state"])
            comment.save()
        return HttpResponseRedirect(request.path)
    return render(request, "admin.html")


#@app.route("/admin/hidded-atc")
def admin_hiddedatc(request):
    if not request.session["user"]["admin"]:
        raise HttpResponseForbidden
    _data = mysql.run_code(
        "SELECT `id`, `title`, `from`, `hide` FROM articles WHERE `hide`>=1 ORDER BY `id` DESC LIMIT 200;"
    )
    data = []
    for i in _data:
        data.append({
            "id": i[0],
            "title": i[1],
            "from": users.get_by_id(i[2]),
            "hide": i[3]
        })
    return render(request, "admin_hiddedatc.html", {"data": data})


#@app.route("/admin/top-atc", methods=["POST"])
def admin_topatc(request):
    if not request.session["user"]["admin"]:
        raise HttpResponseForbidden
    try:
        atc_id = int(request.POST["id"])
        mysql.update("articles", {"top": 1}, {"id": atc_id})
        # flash("置顶成功！")
    except Exception as e:
        ...
        # flash(f"置顶失败！\n<br />\n{e}")
    return HttpResponseRedirect("/admin")


#@app.route("/admin/untop-atc", methods=["POST"])
def admin_untopatc(request):
    if not request.session["user"]["admin"]:
        raise HttpResponseForbidden
    try:
        atc_id = int(request.POST["id"])
        mysql.update("articles", {"top": 0}, {"id": atc_id})
        # flash("取消置顶成功！")
    except Exception as e:
        ...
        # flash(f"取消置顶失败！\n<br />\n{e}")
    return HttpResponseRedirect("/admin")


#@app.route("/admin/top-cmt", methods=["POST"])
def admin_topcmt(request):
    if not request.session["user"]["admin"]:
        raise HttpResponseForbidden
    try:
        atc_id = int(request.POST["atc_id"])
        cmt_floor = int(request.POST["cmt_floor"])
        cmt_id = mysql.select("comments", ["id"],
                              {"under": atc_id})[cmt_floor - 1][0]
        mysql.update("comments", {"top": 1}, {"id": cmt_id})
        # flash("置顶成功！")
    except Exception as e:
        ...
        # flash(f"置顶失败！\n<br />\n{e}")
    return HttpResponseRedirect("/admin")


#@app.route("/admin/untop-cmt", methods=["POST"])
def admin_untopcmt(request):
    if not request.session["user"]["admin"]:
        raise HttpResponseForbidden
    try:
        atc_id = int(request.POST["atc_id"])
        cmt_floor = int(request.POST["cmt_floor"])
        cmt_id = mysql.select("comments", ["id"],
                              {"under": atc_id})[cmt_floor - 1][0]
        mysql.update("comments", {"top": 0}, {"id": cmt_id})
        # flash("取消置顶成功！")
    except Exception as e:
        ...
        # flash(f"取消置顶失败！\n<br />\n{e}")
    return HttpResponseRedirect("/admin")


#@app.route("/admin/hide-atc", methods=["POST"])
def admin_hideatc(request):
    if not request.session["user"]["admin"]:
        raise HttpResponseForbidden
    try:
        atc_id = int(request.POST["id"])
        level = int(request.POST["level"])
        mysql.update("articles", {"hide": level}, {"id": atc_id})
        articles.reget(atc_id)
        articles.articles.pop(atc_id)
        # flash("删除成功！")
    except Exception as e:
        ...
        # flash(f"删除失败！\n<br />\n{e}")
    return HttpResponseRedirect("/admin")


#@app.route("/admin/del-atc", methods=["POST"])
def admin_delatc(request):
    if not request.session["user"]["admin"]:
        raise HttpResponseForbidden
    try:
        atc_id = int(request.POST["id"])
        mysql.delete("articles", {"id": atc_id})
        articles.cnt -= 1
        articles.articles.pop(atc_id)
        # flash("删除成功！")
    except Exception as e:
        ...
        # flash(f"删除失败！\n<br />\n{e}")
    return HttpResponseRedirect("/admin")


#@app.route("/admin/del-cmt", methods=["POST"])
def admin_delcmt(request):
    if not request.session["user"]["admin"]:
        raise HttpResponseForbidden
    try:
        atc_id = int(request.POST["atc_id"])
        cmt_floor = int(request.POST["cmt_floor"])
        data = mysql.select("comments", ["id"], {"under": atc_id})
        mysql.delete("comments", {"id": data[cmt_floor - 1][0]})
        # flash("删除成功！")
    except Exception as e:
        ...
    return HttpResponseRedirect("/admin")


def sadmin_index(request):
    if request.session["user"]["admin"] != 2:
        raise HttpResponseForbidden
    return render(request, "sadmin.html")


def sadmin_deluser(request):
    if request.session["user"]["admin"] != 2:
        raise HttpResponseForbidden
    try:
        user_id = int(request.POST["user_id"])
        mysql.update("users", {"password": "封号"}, {"id": user_id})
        users.blacklist.append(user_id)
        users.flush(user_id)
    except Exception as e:
        ...
    return HttpResponseRedirect("/sadmin")


def sadmin_addadmin(request):
    if request.session["user"]["admin"] != 2:
        raise HttpResponseForbidden
    try:
        user_id = int(request.POST["user_id"])
        level = int(request.POST["level"])
        mysql.update("users", {"admin": level}, {"id": user_id})
        users.flush(user_id)
    except Exception as e:
        ...
    return HttpResponseRedirect("/sadmin")


def sadmin_addtag(request):
    if request.session["user"]["admin"] != 2:
        raise HttpResponseForbidden
    try:
        user_id = int(request.POST["user_id"])
        tags = request.POST["tags"]
        mysql.update("users", {"tags": tags}, {"id": user_id})
        users.flush(user_id)
    except Exception as e:
        ...
    return HttpResponseRedirect("/sadmin")


def sadmin_rmdamin(request):
    if request.session["user"]["admin"] != 2:
        raise HttpResponseForbidden
    try:
        user_id = int(request.POST["user_id"])
        mysql.update("users", {"admin": 0}, {"id": user_id})
        users.flush(user_id)
    except Exception as e:
        ...
    return HttpResponseRedirect("/sadmin")


def test(request):
    return HttpResponse("123")


def error_404(request, exception):
    return render(request, "404.html")


def error_500(request):
    return render(request, "500.html")
