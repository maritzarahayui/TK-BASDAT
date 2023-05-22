from django.urls import path
from general import views

app_name = "general"

urlpatterns = [
   path('', views.home, name="home"),
   path('login/', views.login, name="login"),
   path('login/auth/', views.loginHelper, name="auth"),
   path('register/', views.register, name="register"),
]