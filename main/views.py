import base64
import re

# Create your views here.

import hashlib
import os
import time

import lightmysql
from flask import *

from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseForbidden, HttpResponseRedirect, HttpResponseNotFound

app = Flask(__name__)
app.secret_key = "QABBQ"
thisDir = os.path.dirname(os.path.abspath(__file__))
mysql = lightmysql.Connect("alimysql.yixiangzhilv.com",
                           "yxzl",
                           "@wangzihan*yixiangzhilv20070601",
                           "qabbq",
                           pool_size=10)
signs = []


class Users:
    users = {}
    blacklist = []
    data = [
        "id", "name", "password", "email", "real_name", "real_name_md5", "sex",
        "grade", "introduction", "tags", "admin"
    ]

    def __init__(self):
        temp = mysql.select("users", self.data)
        for i in temp:
            user = {self.data[j]: i[j] for j in range(len(self.data))}
            self.users[i[0]] = user
        return

    def add(self, name, password):
        for i, j in self.users.items():
            if j["name"] == name:
                return "用户名已存在"
        user = {"name": name, "password": password}
        user["tags"] = "无认证信息"
        user["sex"] = user["grade"] = "保密"
        user["introduction"] = user["real_name"] = user["email"] = ""
        mysql.insert("users", user)
        user["id"] = mysql.select("users", ["id"], {"name": name})[0][0]
        self.users[user["id"]] = user
        return user

    def update(self, num, values):
        if values["real_name"]:
            values["real_name_md5"] = get_md5(values["real_name"])
        mysql.update("users", values, {"id": num})
        temp = mysql.select("users", self.data, {"id": num})[0]
        user = {self.data[j]: temp[j] for j in range(len(self.data))}
        self.users[num] = user
        return user

    def get_by_id(self, num):
        return self.users.get(num) or None

    def get_by_name(self, name):
        for i in self.users.values():
            if i["name"] == name:
                return i
        return None

    def flush(self, num):
        temp = mysql.select("users", self.data, {"id": num})[0]
        user = {self.data[j]: temp[j] for j in range(len(self.data))}
        self.users[num] = user
        return user


class Notices:
    notices = {}

    def add(self, user, content, url, _time=""):
        user = int(user)
        if not url.startswith("http"):
            url = "https://qa.yxzl.top" + url
        _time = _time or format_time(int(time.time()))
        if not self.notices.get(user):
            self.notices[user] = [[content, _time, url]]
        elif self.notices[user][-1][0] != content:
            self.notices[user].append([content, _time, url])
            if len(self.notices[user]) > 10:
                self.notices[user].pop(0)

    def get(self, user):
        user = int(user)
        return self.notices.get(user) or []


class Articles:
    articles = {}
    cnt = 0
    cnts = {}

    def __init__(self):
        self.cnt = int(mysql.run_code("SELECT COUNT(id) FROM articles;")[0][0])

    def get(self, num):
        num = int(num)
        if self.articles.get(num):
            return self.articles[num]
        else:
            return self.reget(num)

    def reget(self, num):
        data = mysql.select("articles", condition={"id": num})[0]
        self.articles[num] = {
            "id": num,
            "from": data[1],
            "title": data[2],
            "content": data[3],
            "time": data[4]
        }
        return self.articles[num]

    def get_user_atcs(self, user):
        user = int(user)
        if self.cnts.get(user):
            return self.cnts[user]
        else:
            self.cnts[user] = mysql.run_code(
                f"SELECT COUNT(id) FROM articles WHERE `from`={user};")[0][0]
            return self.cnts[user]


users = Users()
notices = Notices()
articles = Articles()
infos = {"上次数据更新时间戳": 0}
start_info = {"time": int(time.time()), "request_cnt": 0}


def get_md5(s):
    m = hashlib.md5()
    m.update(s.encode('utf-8'))
    return m.hexdigest()


def get_base64(s):
    return str(base64.b64encode(s.encode("utf-8")), "utf-8")


def format_time(s):
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(s))


def info_init():
    global start_info
    start_info["request_cnt"] += 1
    # request.session["ip"] = request.headers.get(
    #     "Ali-Cdn-Real-Ip") or request.remote_addr
    # if request.session.get("user"):
    #     if request.session["user"]["id"] in users.blacklist:
    #         abort(410)
    #     elif request.session["user"].get("admin"):
    #         request.session["user"] = users.get_by_id(request.session["user"]["id"])


def post_check(data, scene, sign):
    # data = [request.session["user"]["name"]] + data
    if sign in signs:
        return "签名已存在"
    ans = ""
    for i in data:
        ans += get_md5(get_base64(get_md5(str(i))))
    ans += scene
    if get_md5(ans) != sign:
        return "签名错误"
    signs.append(sign)
    return None


def user_login(request):
    info_init()
    if request.method == "POST":
        name = request.POST.get("name")
        password = request.POST.get(
            "password")  #我不知道这个要不要改成GET.get--Iron_Grey_
        if name and password:
            user = users.get_by_name(name)
            if user:
                if user["id"] in users.blacklist or user["password"] == "封号":
                    return "用户已被封禁"
                elif user["password"] == password:
                    request.session["user"] = user
                    # request.session["user"] = user
                    return HttpResponse("Success")
                else:
                    return HttpResponse("密码错误")
            else:
                request.session["user"] = users.add(name, password)
                # request.session["user"] = users.add(name, password)
                return HttpResponse("Success")
        else:
            return HttpResponse("用户名或密码不能为空")
    return render(request, "login.html")  #这个后面需要加花括号吗--Iron_Grey_


def user_logout(request):
    del request.session["user"]
    return HttpResponseRedirect("/")  #我也不知道这个怎么改--Iron_Grey_


def dashboard(request):
    global infos
    if infos["上次数据更新时间戳"] < time.time() - 600:
        infos["注册用户数"] = mysql.run_code("SELECT COUNT(id) FROM users;")[0][0]
        infos["文章数"] = mysql.run_code("SELECT COUNT(id) FROM articles;")[0][0]
        articles.cnt = infos["文章数"]
        infos["评论数"] = mysql.run_code("SELECT COUNT(id) FROM comments;")[0][0]
        infos["管理员用户数"] = mysql.run_code(
            "SELECT COUNT(id) FROM users WHERE `admin`=1 OR `admin`=2;")[0][0]
        infos["被禁止首页列出的贴子数(隐藏级别为1)"] = mysql.run_code(
            "SELECT COUNT(id) FROM articles WHERE `hide`=1;")[0][0]
        infos["被禁止列出的贴子数(隐藏级别为2)"] = mysql.run_code(
            "SELECT COUNT(id) FROM articles WHERE `hide`=2;")[0][0]
        infos["置顶贴子数"] = mysql.run_code(
            "SELECT COUNT(id) FROM articles WHERE `top`=1;")[0][0]
        infos["置顶评论数"] = mysql.run_code(
            "SELECT COUNT(id) FROM comments WHERE `top`=1;")[0][0]
        infos["未处理举报数"] = mysql.run_code(
            "SELECT COUNT(id) FROM reports;")[0][0]
        infos["上次数据更新时间戳"] = time.time()
        infos["上次数据更新时间"] = format_time(infos["上次数据更新时间戳"])
        infos["本次服务器启动时间"] = format_time(start_info["time"])
    t = int(time.time() - start_info["time"])
    infos[
        "本次启动稳定运行时长（实时）"] = f"{t // 86400}天{t % 86400 // 3600}小时{t % 3600 // 60}分钟{t % 60}秒"
    infos["本次启动后总请求数（实时）"] = start_info["request_cnt"]
    return render(request, "dashboard.html", {"data": infos})


# @app.route("/search", methods=["GET", "POST"])
# def search():
#     user = int(request.values.get("user") or 0)
#     return "搜索功能暂未开放"


def search(request):
    user = int(request.GET.get("user") or 0)
    return HttpResponse("搜索功能暂未开放")


def index(request):
    info_init()
    page = int(request.GET.get("page") or 1)
    if request.GET.get("hide") == "false":
        _article = mysql.run_code(
            f"SELECT * FROM articles ORDER BY `id` DESC LIMIT {(page - 1) * 15}, 15;"
        )
    else:
        _article = mysql.run_code(
            f"SELECT * FROM articles WHERE `hide`=0 OR `hide` IS NULL ORDER BY `id` DESC LIMIT {(page - 1) * 15}, 15;"
        )
    _top = mysql.select("articles", condition={"top": 1})
    article = []
    top = []
    for i in (_article + _top):
        t = {
            "id": i[0],
            "from": i[1],
            "title": i[2],
            "content": i[3],
            "time": format_time(int(i[4])),
            "writer": users.get_by_id(i[1]),
            "top": i[5]
        }
        if i[5]:
            t["title"] = "【置顶】" + t["title"]
            if t not in top:
                top.append(t)
        else:
            article.append(t)
    article = top + article
    return render(request, "index.html", {
        "articles": article,
        "page": page,
        "pages": articles.cnt // 15 + 1
    })


def user_page(request, user_id):
    info_init()
    if users.get_by_id(user_id) is None:
        abort(404)
    page = int(request.GET.get("page") or 1)
    if request.GET.get("hide") == "false":
        _article = mysql.run_code(
            f"SELECT * FROM articles WHERE `from`={user_id} ORDER BY `id` DESC LIMIT {(page - 1) * 15}, 15;"
        )
    else:
        _article = mysql.run_code(
            f"SELECT * FROM articles WHERE `from`={user_id} AND (`hide`<=1 OR `hide` IS NULL) ORDER BY `id` DESC LIMIT {(page - 1) * 15}, 15;"
        )
    _top = mysql.select("articles", condition={"top": 1, "from": user_id})
    article = []
    top = []
    for i in (_article + _top):
        t = {
            "id": i[0],
            "from": i[1],
            "title": i[2],
            "content": i[3],
            "time": format_time(int(i[4])),
            "writer": users.get_by_id(i[1]),
            "top": i[5]
        }
        if i[5]:
            t["title"] = "【置顶】" + t["title"]
            if t not in top:
                top.append(t)
        else:
            article.append(t)
    article = top + article
    return render(
        request, "user_page.html",
        dict(owner=users.get_by_id(user_id),
             articles=article,
             page=page,
             pages=articles.get_user_atcs(user_id) // 15 + 1))


def article_writing(request):
    info_init()
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
    if request.method == "POST":
        if post_check([
                request.session["user"]["name"], request.POST["title"],
                request.POST["content"]
        ], "article", request.POST["sign"]):
            return HttpResponseForbidden("签名校验错误")
        if request.GET["update"] == "true":
            mysql.update(
                "articles", {
                    "title": request.POST["title"],
                    "content": request.POST["content"],
                    "time": int(time.time()),
                }, {"id": request.GET["id"]})
            articles.reget(request.GET["id"])
            return HttpResponse(request.GET["id"])
        mysql.insert(
            "articles", {
                "from": request.session["user"]["id"],
                "title": request.POST["title"],
                "content": request.POST["content"],
                "time": int(time.time())
            })
        articles.cnt += 1
        articles.get_user_atcs(request.session["user"]["id"])
        articles.cnts[request.session["user"]["id"]] += 1
        return HttpResponse(
            str(
                mysql.select("articles",
                             condition={
                                 "from": request.session["user"]["id"],
                                 "title": request.POST["title"],
                                 "content": request.POST["content"]
                             })[-1][0]))
    else:
        if request.GET.get("id") and request.GET["id"].isdigit():
            data = mysql.select("articles", ["from", "title", "content", "id"],
                                {"id": int(request.GET["id"])})[0]
            if request.session["user"]["id"] == data[0]:
                data = {
                    "from": data[0],
                    "title": data[1],
                    "content": data[2],
                    "id": data[3]
                }
                return render(request, "article-writing.html", {"data": data})
        return render(request, "article-writing.html", {"data": {}})


def article_delete(request, atc_id):
    info_init()
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
    atc = articles.get(atc_id)
    if atc.get("from") != request.session["user"]["id"]:
        raise HttpResponseForbidden("您不是该文章作者！")
    try:
        mysql.delete("articles", {"id": atc_id})
        articles.cnt -= 1
        articles.articles.pop(atc_id)
        # flash("删除成功！")
    except Exception as e:
        ...
        # flash(f"删除失败！\n<br />\n{e}")
    return HttpResponseRedirect(f"/user/{request.session['user']['id']}")


#@app.route('/image-upload', methods=['POST'])
def upload(request):
    info_init()
    f = request.files.get('file')
    name = f"{time.time()}_{f.filename}"
    f.save(f"{thisDir}/static/article_images/{name}")
    return HttpResponse(name)


#@app.route("/notice")
def make_notice(request):
    info_init()
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
    to = request.GET["to"]
    at = request.GET["at"]
    if at == "article":
        notices.add(
            to,
            f"{request.session['user']['name']}在文章：{articles.get(request.GET['atc'])['title']}下提到了你",
            f"/article/{request.GET['atc']}")
    return HttpResponse("Success")


def article_page(request, atc_id):
    info_init()
    if request.method == "POST":
        if post_check([
                request.session["user"]["name"],
                str(atc_id), request.POST["comment"]
        ], "comment", request.POST["sign"]):
            return HttpResponseForbidden("签名校验错误")
        if not request.session.get("user"):
            return HttpResponseRedirect("/user/login?from=" +
                                        request.build_absolute_uri())
        mysql.insert(
            "comments", {
                "from": request.session.get("user")["id"],
                "under": atc_id,
                "content": request.POST["comment"],
                "time": int(time.time())
            })
        notices.add(
            articles.get(atc_id)["from"],
            f"{request.session['user']['name']}评论了你的文章：{articles.get(atc_id)['title']}",
            f"/article/{atc_id}")
        # return HttpResponseRedirect("/article/%d" % atc_id)
        return HttpResponse("Success")
    _article = mysql.select("articles", ["from", "title", "content", "time"],
                            {"id": atc_id})
    if not _article:
        return HttpResponseNotFound("文章不存在！")
    else:
        _article = _article[0]
    article = {
        "id": atc_id,
        "from": _article[0],
        "title": _article[1],
        "content": _article[2],
        "time": time.strftime("%Y年%m月%d日 %H:%M:%S",
                              time.localtime(_article[3]))
    }
    _comments = mysql.select("comments",
                             target=["from", "content", "time", "top"],
                             condition={"under": atc_id})
    comment = []
    top = []
    for i in _comments:
        comment.append({
            "from": users.get_by_id(i[0]),
            "content": i[1],
            "time": format_time(i[2]),
            "top": i[3]
        })
        if i[3]:
            top.append(comment[-1])
    return render(
        request, "article.html",
        dict(article=article,
             comments=comment,
             tops=top,
             writer=users.get_by_id(article["from"]),
             owner=users.get_by_id(article["from"])))


def edit_information(request):
    info_init()
    # if not request.session.get("user"):
    #     return HttpResponseRedirect("/user/login?from=" + request.build_absolute_uri())
    if request.method == "POST":
        values = request.POST.dict()
        if values["sex"] not in ["男", "女"]:
            values["sex"] = "保密"
        request.session["user"] = users.update(request.session["user"]["id"],
                                               values)
        # flash("信息修改成功！")
        return HttpResponseRedirect("/user/edit")
    else:
        return render(request, "edit_information.html")


@app.route("/flush/user/<int:user_id>")  #这个不会改--Iron_Grey_
def flush_user(user_id):
    info_init()
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
    if not request.session["user"]["admin"]:
        raise HttpResponseForbidden
    users.flush(user_id)
    return "OK"


@app.route("/report/article/<int:atc_id>")  #这个不会改--Iron_Grey_
def report_article(atc_id):
    info_init()
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
    info_init()
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
    if not request.session["user"]["admin"]:
        raise HttpResponseForbidden
    return render(request, "admin.html")


#@app.route("/admin/reports", methods=["GET", "POST"])
def admin_reports(request):
    info_init()
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
    info_init()
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
    info_init()
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
    info_init()
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
    info_init()
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
    info_init()
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
    info_init()
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
    info_init()
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
    info_init()
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
        # flash(f"删除失败！\n<br />\n{e}")
    return HttpResponseRedirect("/admin")


#@app.route("/sadmin")
def sadmin_index(request):
    info_init()
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
    if request.session["user"]["admin"] != 2:
        raise HttpResponseForbidden
    return render(request, "sadmin.html")


#@app.route("/sadmin/del-user", methods=["POST"])
def sadmin_deluser(request):
    info_init()
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
        # flash("封禁成功！")
    except Exception as e:
        ...
        # flash(f"封禁失败！\n<br />\n{e}")
    return HttpResponseRedirect("/sadmin")


#@app.route("/sadmin/add-admin", methods=["POST"])
def sadmin_addadmin(request):
    info_init()
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
        # flash("操作成功！")
    except Exception as e:
        ...
        # flash(f"操作失败！\n<br />\n{e}")
    return HttpResponseRedirect("/sadmin")


# @app.route("/sadmin/add-tag", methods=["POST"])
def sadmin_addtag(request):
    info_init()
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
        # flash("操作成功！")
    except Exception as e:
        ...
        # flash(f"操作失败！\n<br />\n{e}")
    return HttpResponseRedirect("/sadmin")


#@app.route("/sadmin/rm-admin", methods=["POST"])
def sadmin_rmdamin(request):
    info_init()
    if not request.session.get("user"):
        return HttpResponseRedirect("/user/login?from=" +
                                    request.build_absolute_uri())
    if request.session["user"]["admin"] != 2:
        raise HttpResponseForbidden
    try:
        user_id = int(request.POST["user_id"])
        mysql.update("users", {"admin": 0}, {"id": user_id})
        users.flush(user_id)
        # flash("操作成功！")
    except Exception as e:
        ...
        # flash(f"操作失败！\n<br />\n{e}")
    return HttpResponseRedirect("/sadmin")


#@app.route("/test")
def test(request):
    return HttpResponse("123")


@app.route("/404")  #这个不会改--Iron_Grey_
@app.errorhandler(404)
def error_404(error):
    return render_template("404.html"), 404


@app.route("/410")  #这个不会改--Iron_Grey_
@app.errorhandler(410)
def error_410(error):
    return HttpResponseRedirect("/user/logout")


@app.context_processor  #这个不会改--Iron_Grey_
def default():
    return {
        "user":
        request.session.get("user"),
        "title":
        "QA瓜田",
        "logined":
        bool(request.session.get("user")),
        "notice":
        request.session.get("user")
        and notices.get(request.session["user"]["id"])[::-1] or [],
    }
