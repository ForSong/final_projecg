from django.conf.urls import url
from . import views

app_name = 'Recommend'
urlpatterns = [
    url(r'^register/', views.register, name='register'),
    url(r'^showmessage/', views.showmessage, name='showmessage'),

]