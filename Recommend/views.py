from django.shortcuts import render
from django.shortcuts import render, redirect,HttpResponseRedirect
from .forms import RegisterForm
from Recommend.models import Resulttable,Insertposter
from django.db import models

def register(request):
    # 只有当请求为 POST 时，才表示用户提交了注册信息
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        # 验证数据的合法性
        if form.is_valid():
            # 如果提交数据合法，调用表单的 save 方法将用户数据保存到数据库
            form.save()

            # 注册成功，跳转回首页
            return redirect('/')
    else:
        # 请求不是 POST，表明用户正在访问注册页面，展示一个空的注册表单给用户
        form = RegisterForm()

    # 渲染模板
    # 如果用户正在访问注册页面，则渲染的是一个空的注册表单
    # 如果用户通过表单提交注册信息，但是数据验证不合法，则渲染的是一个带有错误信息的表单
    return render(request, 'Recommend/register.html', context={'form': form})


def index(request):
    return render(request, 'Recommend/..//index.html')
# 为啥？

def check(request):
    return render((request, 'Recommend/..//index.html'))


def showmessage(request):
    usermovieid = []
    usermovietitle = []
    data=Resulttable.objects.filter(userId=1001)
    for row in data:
        usermovieid.append(row.imdbId)

    try:
        conn = get_conn()
        cur = conn.cursor()
        #Insertposter.objects.filter(userId=USERID).delete()
        for i in usermovieid:
            cur.execute('select * from moviegenre3 where imdbId = %s',i)
            rr = cur.fetchall()
            for imdbId,title,poster in rr:
                usermovietitle.append(title)
                print(title)

        # print(poster_result)
    finally:
        conn.close()
    # return render(request, 'Recommend/message.html', locals())


