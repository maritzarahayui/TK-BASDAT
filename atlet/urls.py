from django.urls import path
from atlet import views

app_name = "atlet"

urlpatterns = [
   path('register/', views.register_atlet, name="register-atlet"),
]