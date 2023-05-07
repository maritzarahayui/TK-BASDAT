from django.urls import path
from general import views

app_name = "general"

urlpatterns = [
   path('login/', views.login, name="login"),
   path('register/', views.register, name="register"),
]