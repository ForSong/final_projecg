from django.shortcuts import render,redirect
from django.shortcuts import HttpResponse
from Recommend import models
from .forms import UserForm, RegisterForm
from .models import Insertposter, Resulttable
import hashlib

#对传输的密码进行加密
def hash_code(s, salt='mysite'):  # 加点盐
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()


def index(request):
    return render(request, 'login/index.html')

'''对于非POST方法发送数据时，比如GET方法请求页面，返回空的表单，让用户可以填入数据；
对于POST方法，接收表单数据，并验证；
使用表单类自带的is_valid()方法一步完成数据验证工作；
验证成功后可以从表单对象的cleaned_data数据字典中获取表单的具体值；
如果验证不通过，则返回一个包含先前数据的表单给前端页面，方便用户修改。也就是说，它会帮你保留先前填写的数据内容，而不是返回一个空表！
'''
def login(request):
    if request.session.get('is_login',None):
        return redirect('/index')
    if request.method == "POST":
        login_form = UserForm(request.POST)
        message = "check contents！"
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            try:
                user = models.User.objects.get(name=username)
                if user.password == hash_code(password):  # 哈希值和数据库内的值进行比对
                    request.session['is_login'] = True
                    request.session['user_id'] = user.id
                    request.session['user_name'] = user.name
                    return redirect('/index/')
                else:
                    message = "password error！"
            except:
                message = "user doesn't exsit！"
        return render(request, 'login/login.html', locals())

    login_form = UserForm()
    return render(request, 'login/login.html', locals())

def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/index/")
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        message = "请检查填写的内容！"
        if register_form.is_valid():  # 获取数据
            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            sex = register_form.cleaned_data['sex']
            if password1 != password2:  # 判断两次密码是否相同
                message = "password different for twice input！"
                return render(request, 'login/register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    message = 'user exists，retry！'
                    return render(request, 'login/register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    message = 'email has been registered , try another！'
                    return render(request, 'login/register.html', locals())

                # 当一切都OK的情况下，创建新用户

                new_user = models.User.objects.create()
                new_user.name = username
                new_user.password = hash_code(password1)
                new_user.email = email
                new_user.sex = sex
                new_user.save()
                return redirect('/login/')  # 自动跳转到登录页面
    register_form = RegisterForm()
    return render(request, 'login/register.html', locals())

def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/index/")

def main_movie(request):
    pass
    return render(request, 'ind.html')


## 将基于用户的推荐转到前端
def recommend1(request):
    USERID = int(request.GET["userIdd"]) + 1000
    Insertposter.objects.filter(userId=USERID).delete()
    #selectMysql()
    read_to_csv('Recommend/static/users_resulttable.csv',USERID)  #追加数据，提高速率
    ratingfile = os.path.join('Recommend/static', 'users_resulttable.csv')
    usercf = UserBasedCF()
    #userid = '1001'
    userid = str(USERID)#得到了当前用户的id
    print(userid)
    usercf.generate_dataset(ratingfile)
    usercf.calc_user_sim()
    usercf.recommend(userid)    #得到imdbId号

    #先删除所有数据


    try:
        conn = get_conn()
        cur = conn.cursor()
        #Insertposter.objects.filter(userId=USERID).delete()
        for i in matrix:
            cur.execute('select * from moviegenre3 where imdbId = %s',i)
            rr = cur.fetchall()
            for imdbId,title,poster in rr:
                #print(value)         #value才是真正的海报链接
                if(Insertposter.objects.filter(title=title)):
                    continue
                else:
                    Insertposter.objects.create(userId=USERID, title=title, poster=poster)

        # print(poster_result)
    finally:
        conn.close()
    #results = Insertposter.objects.all()       #从这里传递给html= Insertposter.objects.all()  # 从这里传递给html
    results = Insertposter.objects.filter(userId=USERID)
    return render(request,'users/movieRecommend.html', locals())
    # return render(request, 'users/..//index.html', locals())

# def recommend2(request):
#     # USERID = int(request.GET["userIddd"]) + 1000
#     USERID = 1001
#     Insertposter.objects.filter(userId=USERID).delete()
#     #selectMysql()
#     read_to_csv2('users/static/users_resulttable2.csv',USERID)  #追加数据，提高速率
#     ratingfile2 = os.path.join('users/static', 'users_resulttable2.csv')
#     itemcf = ItemBasedCF()
#     #userid = '1001'
#     userid = str(USERID)#得到了当前用户的id
#     print(userid)
#     itemcf.generate_dataset(ratingfile2)
#     itemcf.calc_movie_sim()
#     itemcf.recommend(userid)    #得到imdbId号
#
#     #先删除所有数据
#
#
#     try:
#         conn = get_conn()
#         cur = conn.cursor()
#         #Insertposter.objects.filter(userId=USERID).delete()
#         for i in matrix2:
#             cur.execute('select * from moviegenre3 where imdbId = %s',i)
#             rr = cur.fetchall()
#             for imdbId,title,poster in rr:
#                 #print(value)         #value才是真正的海报链接
#                 if(Insertposter.objects.filter(title=title)):
#                     continue
#                 else:
#                     Insertposter.objects.create(userId=USERID, title=title, poster=poster)
#
#         # print(poster_result)
#     finally:
#         conn.close()
#         results = Insertposter.objects.filter(userId=USERID)       #从这里传递给html= Insertposter.objects.all()  # 从这里传递给html
#
#     return render(request, 'users/movieRecommend2.html',locals())
#     # return HttpResponseRedirect('movieRecommend.html', locals())



import sqlite3
import csv
import codecs
def get_conn():
    conn = sqlite3.connect(host='127.0.0.1', port=3307, user='root', passwd='123456789.', db='db', charset='utf8')
    return conn

def query_all(cur, sql, args):
    cur.execute(sql, args)
    return cur.fetchall()
def read_to_csv(filename,user):
    with codecs.open(filename=filename, mode='w', encoding='utf-8') as f:
        write = csv.writer(f, dialect='excel')
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('select * from users_resulttable')
        #sql = ('select * from users_resulttable WHERE userId = 1001')
        rr = cur.fetchall()
        #results = query_all(cur=cur, sql=sql, args=None)
        for result in rr:
            #print(result)
            write.writerow(result[:-1])


def read_to_csv2(filename,user):
    with codecs.open(filename=filename, mode='a', encoding='utf-8') as f:
        write = csv.writer(f, dialect='excel')
        conn = get_conn()
        cur = conn.cursor()
        cur.execute('select * from users_resulttable')
        sql = ('select * from users_resulttable WHERE userId = 1001')
        rr = cur.fetchall()
        results = query_all(cur=cur, sql=sql, args=None)
        for result in results:
            #print(result)
            write.writerow(result[:-1])

import sys
import random
import math
import os
from operator import itemgetter

random.seed(0)
user_sim_mat = {}
matrix = []  #全局变量
matrix2 = []

class UserBasedCF(object):
    ''' TopN recommendation - User Based Collaborative Filtering '''

    def __init__(self):
        self.trainset = {}  # 训练集
        self.testset = {}  # 测试集
        self.initialset = {}  # 存储要推荐的用户的信息
        self.n_sim_user = 30
        self.n_rec_movie = 10

        self.movie_popular = {}
        self.movie_count = 0  # 总电影数量

        print('Similar user number = %d' % self.n_sim_user, file=sys.stderr)
        print('recommended movie number = %d' %
              self.n_rec_movie, file=sys.stderr)

    @staticmethod
    def loadfile(filename):
        ''' load a file, return a generator. '''
        fp = open(filename, 'r', encoding='UTF-8')
        for i, line in enumerate(fp):
            yield line.strip('\r\n')
            # if i % 100000 == 0:
            #     print ('loading %s(%s)' % (filename, i), file=sys.stderr)
        fp.close()
        print('load %s success' % filename, file=sys.stderr)

    def initial_dataset(self, filename1):
        initialset_len = 0
        for lines in self.loadfile(filename1):
            users, movies, ratings = lines.split(',')
            self.initialset.setdefault(users, {})
            self.initialset[users][movies] = (ratings)
            initialset_len += 1

    def generate_dataset(self, filename2, pivot=1.0):
        ''' load rating data and split it to training set and test set '''
        trainset_len = 0
        testset_len = 0

        for line in self.loadfile(filename2):
            # user, movie, rating, _ = line.split('::')
            user, movie, rating = line.split(',')
            # split the data by pivot
            if random.random() < pivot:  # pivot=0.7应该表示训练集：测试集=7：3
                self.trainset.setdefault(user, {})
                self.trainset[user][movie] = (rating)  # trainset[user][movie]可以获取用户对电影的评分  都是整数
                trainset_len += 1
            else:
                self.testset.setdefault(user, {})
                self.testset[user][movie] = (rating)
                testset_len += 1

        print('split training set and test set succ', file=sys.stderr)
        print('train set = %s' % trainset_len, file=sys.stderr)
        print('test set = %s' % testset_len, file=sys.stderr)

    def calc_user_sim(self):
        movie2users = dict()

        for user, movies in self.trainset.items():
            for movie in movies:
                # inverse table for item-users
                if movie not in movie2users:
                    movie2users[movie] = set()
                movie2users[movie].add(user)  # 看这个电影的用户id
                # print(movie)   #输出的是movieId
                # print(movie2users[movie])   #输出的是{'userId'...}
                # print(movie2users)    #movieId:{'userId','userId'...}

                # count item popularity at the same time
                if movie not in self.movie_popular:
                    self.movie_popular[movie] = 0
                self.movie_popular[movie] += 1
        # print ('build movie-users inverse table succ', file=sys.stderr)

        # save the total movie number, which will be used in evaluation
        self.movie_count = len(movie2users)
        print('total movie number = %d' % self.movie_count, file=sys.stderr)

        # count co-rated items between users  计算用户之间共同评分的物品
        usersim_mat = user_sim_mat
        # print ('building user co-rated movies matrix...', file=sys.stderr)

        for movie, users in movie2users.items():  # 通过.items()遍历movie2users这个字典里的所有键、值
            for u in users:
                for v in users:
                    if u == v:
                        continue
                    usersim_mat.setdefault(u, {})
                    usersim_mat[u].setdefault(v, 0)
                    usersim_mat[u][v] += 1 / math.log(1 + len(users))  # usersim_mat二维矩阵应该存的是用户u和用户v之间共同评分的电影数目
        # print ('build user co-rated movies matrix succ', file=sys.stderr)

        # calculate similarity matrix
        # print ('calculating user similarity matrix...', file=sys.stderr)
        simfactor_count = 0
        PRINT_STEP = 20000

        for u, related_users in usersim_mat.items():
            for v, count in related_users.items():
                usersim_mat[u][v] = count / math.sqrt(
                    len(self.trainset[u]) * len(self.trainset[v]))
                simfactor_count += 1


    def recommend(self, user):
        ''' Find K similar users and recommend N movies. '''
        matrix.clear()   #每次都要清空
        K = self.n_sim_user  # 这里等于20
        N = self.n_rec_movie  # 这里等于10
        rank = dict()  # 用户对电影的兴趣度
        # print(self.initialset[user])
        watched_movies = self.trainset[user]  # user用户已经看过的电影  只包括训练集里的
        # 这里之后不能是训练集
        # watched_movies = self.initialset[user]
        for similar_user, similarity_factor in sorted(user_sim_mat[user].items(),
                                                      key=itemgetter(1), reverse=True)[
                                               0:K]:  # itemgetter(1)表示对第2个域(相似度)排序   reverse=TRUE表示降序
            for imdbid in self.trainset[similar_user]:  # similar_user是items里面的键，就是所有用户   similarity_factor是值，就是对应的相似度
                if imdbid in watched_movies:
                    continue  # 如果该电影用户已经看过，则跳过
                # predict the user's "interest" for each movie
                rank.setdefault(imdbid, 0)  # 没有值就为0
                rank[imdbid] += similarity_factor   #rank[movie]就是各个电影的相似度

        rank_ = sorted(rank.items(), key=itemgetter(1), reverse=True)[0:N]  #类型是list不是字典了
        for key,value in rank_:
            matrix.append(key)    #matrix为存储推荐的imdbId号的数组
            #print(key)     #得到了推荐的电影的imdbid号
        print(matrix)
        #return sorted(rank.items(), key=itemgetter(1), reverse=True)[0:N]
        return matrix

class ItemBasedCF(object):
    ''' TopN recommendation - Item Based Collaborative Filtering '''

    def __init__(self):
        self.trainset = {}
        self.testset = {}

        self.n_sim_movie = 20
        self.n_rec_movie = 10

        self.movie_sim_mat = {}
        self.movie_popular = {}
        self.movie_count = 0

        # print('Similar movie number = %d' % self.n_sim_movie, file=sys.stderr)
        # print('Recommended movie number = %d' %
        #       self.n_rec_movie, file=sys.stderr)

    @staticmethod
    def loadfile(filename):
        ''' load a file, return a generator. '''
        # data1=np.loadtxt(filename,delimiter=',',dtype=float)
        fp = open(filename, 'r', encoding='UTF-8')
        for i, line in enumerate(fp):
            yield line.strip('\r\n')
            # if i % 100000 == 0:
            #     print ('loading %s(%s)' % (filename, i), file=sys.stderr)
        fp.close()
        print('load %s succ' % filename, file=sys.stderr)




