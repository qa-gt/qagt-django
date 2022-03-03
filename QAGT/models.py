from django.db import models

# Create your models here.
class User(models.Model):
    id = models.IntegerField(primary_key=True, auto_created=True)
    name = models.CharField(max_length=30)
    password = models.CharField(max_length=30)
    real_name = models.CharField(max_length=10)
    real_name_md5 = models.CharField(max_length=32)
    email = models.CharField(max_length=100)
    grade = models.CharField(max_length=10)
    sex = models.CharField(max_length=5)
    introduction = models.TextField(max_length=100)
    tags = models.TextField(max_length=30)
    admin = models.SmallIntegerField()

    def __str__(self):
        return f"{self.id} - {self.name}"

    class Meta:
        db_table = "users"
