from django.urls import path, include
from . import views #.은 현재폴더의 디렉토리라는뜻. 즉 현재폴더의 views.py를 import하는것임

urlpatterns = [
path('', views.index),
#path('oniondata/<str:onionscanfile>/', views.onionscanfiles),
path('datas/<str:data>/', views.datas),
#path('', views.results),
path('result',views.results)
]