import hashlib
import os
import time

from django.shortcuts import render
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseRedirect, HttpResponseNotFound, Http404, HttpResponseNotAllowed
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


def user_login(request):
    if request.method == "POST":
        name = request.POST.get("name")
        password = request.POST.get("password")
        if name and password:
            try:
                user = Users.objects.get(name=name)
                if user.state <= -3:
                    return HttpResponse("用户已被封禁")
                elif user.password == password:
                    request.session["user"] = user.id
                    return HttpResponse("Success")
                else:
                    return HttpResponse("密码错误")
            except Users.DoesNotExist as e:
                user = Users(name=name, password=password)
                user.save()
                request.session["user"] = user.id
                return HttpResponse("Success")
        else:
            return HttpResponse("用户名或密码不能为空")
    return render(request, "login.html")


def user_logout(request):
    del request.session["user"]
    return HttpResponseRedirect("/")


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
        state__gte=0).order_by("id")[(page - 1) * 15:page * 15]
    _top = Articles.objects.filter(state__gte=3)
    article = []
    top = []
    for i in (_article | _top):
        if i.state >= 3:
            i.title = "【置顶】" + i.title
            if i not in top:
                top.append(i)
        else:
            article.append(i)
    article = top[::-1] + article[::-1]
    return render(
        request, "index.html", {
            "articles": article,
            "page": page,
            "pages": Articles.objects.filter(state__gte=0).count() // 15 + 1,
            "footer": True
        })


def user_page(request, user_id):
    if not Users.objects.filter(id=user_id).exists():
        raise Http404("用户不存在")
    user = Users.objects.get(id=user_id)
    page = int(request.GET.get("page") or 1)
    _article = Articles.objects.filter(
        state__gte=-1, author=user).order_by("id")[(page - 1) * 15:page * 15]
    _top = Articles.objects.filter(state__gte=1, author=user)
    article = []
    top = []
    for i in (_article | _top):
        if i.state >= 1:
            i.title = "【置顶】" + i.title
            if i not in top:
                top.append(i)
        else:
            article.append(i)
    article = top[::-1] + article[::-1]
    return render(
        request, "user_page.html",
        dict(owner=user,
             articles=article,
             page=page,
             pages=Articles.objects.filter(author=user).count() // 15 + 1))


def article_write(request):
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
    if request.method == "POST":
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
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
    atc = Articles.objects.get(id=atc_id)
    if atc.author.id != request.session["user"]:
        return HttpResponseForbidden("您不是该文章作者！")
    try:
        atc.delete()
    except Exception as e:
        ...
    return HttpResponseRedirect(f"/user/{request.session['user']}")


def image_upload(request):
    file = request.FILES["file"]
    if file.size > 1024 * 1024 * 5:
        return HttpResponse("文件过大！")
    name = f"{request.session['user']}_{time.time()}.{file.name.split('.')[-1]}"
    if QAGT_SERVER == "PRODUCTION":
        path = f"{STATIC_ROOT}/article_images/{name}"
    else:
        path = f"{STATICFILES_DIRS[0]}/article_images/{name}"
    with open(path, 'wb+') as f:
        for chunk in file.chunks():
            f.write(chunk)
    return HttpResponse(name)


#@app.route("/notice")
def make_notice(request):
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
    # to = request.GET["to"]
    # at = request.GET["at"]
    # if at == "article":
    #     notices.add(
    #         to,
    #         f"{request.session['user']['name']}在文章：{articles.get(request.GET['atc'])['title']}下提到了你",
    #         f"/article/{request.GET['atc']}")
    return HttpResponse("Success")


def article_page(request, atc_id):
    if request.method == "POST":
        Comments.objects.create(author_id=request.session["user"],
                                under_id=atc_id,
                                content=request.POST["comment"],
                                time=int(time.time()))
        return HttpResponse("Success")

    try:
        article = Articles.objects.get(id=atc_id)
        _comments = Comments.objects.filter(under=article, state__gte=0)
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


def edit_information(request):
    if request.method == "POST":
        values = request.POST.dict()
        if values["sex"] not in ["男", "女"]:
            values["sex"] = "保密"
        if values.get("real_name"):
            values["real_name_md5"] = get_md5(values["real_name"])
        user = Users.objects.get(id=request.session["user"])
        for i, j in values.items():
            user.__setattr__(i, j)
        user.save()
        return HttpResponseRedirect("/user/edit")
    else:
        return render(request, "edit_information.html")


def report_article(atc_id):
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
    mysql.insert(
        "reports", {
            "from": request.session["user"]["id"],
            "atc_id": atc_id,
            "time": int(time.time())
        })
    # flash("举报成功！")
    return HttpResponseRedirect("/article/%d" % atc_id)


#@app.route("/admin")
def admin_index(request):
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
    if not request.session["user"]["admin"]:
        raise HttpResponseForbidden
    return render(request, "admin.html")


#@app.route("/admin/reports", methods=["GET", "POST"])
def admin_reports(request):
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
    if not request.session["user"]["admin"]:
        raise HttpResponseForbidden
    if request.method == "POST":
        mysql.delete("reports", {"id": request.values["id"]})
        return HttpResponseRedirect("/admin/reports")
    data = mysql.select("reports", ["id", "from", "atc_id", "time"],
                        order_by=["time"])
    reports = []
    for i in data:
        reports.append({
            "id": i[0],
            "from": users.get_by_id(i[1]),
            "article": articles.get(i[2]),
            "time": format_time(i[3])
        })
    return render(request, "admin_reports.html", {"reports": reports})


#@app.route("/admin/hidded-atc")
def admin_hiddedatc(request):
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
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
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
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
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
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
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
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
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
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
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
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
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
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
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
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
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
    if request.session["user"]["admin"] != 2:
        raise HttpResponseForbidden
    return render(request, "sadmin.html")


def sadmin_deluser(request):
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
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
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
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
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
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
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
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
    # print(exception)
    return render(request, "404.html")


def error_500(request):
    return render(request, "500.html")


def error_410(error):
    return HttpResponseRedirect("/user/logout")
