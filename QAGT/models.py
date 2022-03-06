from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
# class User(AbstractUser):
#     grade = models.CharField(max_length=10,
#                              null=True,
#                              blank=True,
#                              default="保密")
#     sex = models.CharField(max_length=5, null=True, blank=True, default="保密",
#                            choices=(
#                                ("男", "男"),
#                                ("女", "女"),
#                                ("保密", "保密"),
#                            ))
#     introduction = models.TextField(max_length=100,
#                                     null=True,
#                                     blank=True,
#                                     default="")
#     tags = models.TextField(max_length=30,
#                             null=True,
#                             blank=True,
#                             default="无认证信息")

#     def __str__(self):
#         return f"{self.id} - {self.username}"

#     class Meta:
#         db_table = "users"


class Users(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    name = models.CharField(max_length=30, unique=True)
    password = models.CharField(max_length=30)
    real_name = models.CharField(max_length=6,
                                 null=True,
                                 blank=True,
                                 default="")
    real_name_md5 = models.CharField(max_length=32,
                                     null=True,
                                     blank=True,
                                     default="")
    email = models.EmailField(max_length=60, null=True, blank=True, default="")
    grade = models.CharField(max_length=6, null=True, blank=True, default="保密")
    sex = models.CharField(max_length=5,
                           null=True,
                           blank=True,
                           default="保密",
                           choices=(
                               ("男", "男"),
                               ("女", "女"),
                               ("保密", "保密"),
                           ))
    introduction = models.TextField(max_length=100,
                                    null=True,
                                    blank=True,
                                    default="")
    tags = models.TextField(max_length=20,
                            null=True,
                            blank=True,
                            default="无认证信息")
    state = models.SmallIntegerField(default=0,
                                     null=True,
                                     blank=True,
                                     choices=(
                                         (3, "超级管理员"),
                                         (2, "全站管理员"),
                                         (1, "话题管理员"),
                                         (0, "普通用户"),
                                         (-1, "禁止发贴"),
                                         (-2, "禁止发言"),
                                         (-3, "封禁帐号"),
                                     ))
    pushplus_token = models.CharField(max_length=32,
                                      null=True,
                                      blank=True,
                                      default="")

    def __str__(self):
        return f"{self.id} - {self.name}"

    class Meta:
        db_table = "users"


class Articles(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    author = models.ForeignKey(Users,
                               on_delete=models.CASCADE,
                               related_name='articles')
    title = models.CharField(max_length=100)
    content = models.TextField()
    create_time = models.BigIntegerField()
    update_time = models.BigIntegerField()
    state = models.SmallIntegerField(null=True,
                                     blank=True,
                                     default=0,
                                     choices=(
                                         (3, "全站置顶"),
                                         (2, "话题页置顶"),
                                         (1, "个人页置顶"),
                                         (0, "正常"),
                                         (-1, "禁止首页列出"),
                                         (-2, "禁止首页和话题列出"),
                                         (-3, "禁止首页、话题和个人页列出"),
                                         (-4, "禁止查看"),
                                         (-5, "删除"),
                                     ))
    tags = models.TextField(max_length=30, null=True, blank=True)

    def __str__(self):
        return f"{self.id} - {self.title}"

    class Meta:
        db_table = "articles"


class Comments(models.Model):
    id = models.AutoField(primary_key=True, unique=True)
    author = models.ForeignKey(Users,
                               on_delete=models.CASCADE,
                               related_name='comments')
    under = models.ForeignKey(Articles,
                              on_delete=models.CASCADE,
                              related_name='comments')
    content = models.CharField(max_length=300)
    time = models.BigIntegerField()
    state = models.SmallIntegerField(null=True,
                                     blank=True,
                                     default=0,
                                     choices=(
                                         (1, "置顶"),
                                         (0, "正常"),
                                         (-1, "隐藏"),
                                         (-2, "删除"),
                                     ))

    def __str__(self):
        return f"{self.id} - {self.author.name} 于 {self.under.title}"

    class Meta:
        db_table = "comments"
