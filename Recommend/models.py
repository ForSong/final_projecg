from django.db import models

# Create your models here.
class User(models.Model):
    '''用户表'''

    gender = (
        ('male', '男'),
        ('female', '女'),
    )

    name = models.CharField(max_length=128, unique=True)
    password = models.CharField(max_length=256)
    email = models.EmailField(unique=True)
    sex = models.CharField(max_length=32, choices=gender, default='男')
    c_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['c_time']
        verbose_name = '用户'
        verbose_name_plural = '用户'


class Resulttable(models.Model):
    # movieId = models.IntegerField(null=True)  # Field name made lowercase.
    userId = models.IntegerField(null=True)  # Field name made lowercase.
    imdbId = models.IntegerField()  # Field name made lowercase.
    rating = models.DecimalField(max_digits=3, decimal_places=1, blank=True, null=True)
    # title = models.CharField(max_length=50, blank=True, null=True)

    # class Meta:
    #     managed = False
    #     db_table = 'resulttable'

    def __str__(self):
        return self.userId+':'+self.rating


class Insertposter(models.Model):
    userId = models.IntegerField(null=True)
    title = models.CharField(max_length=200,blank=True,null = False)
    poster = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return self.userId + ':' + self.poster