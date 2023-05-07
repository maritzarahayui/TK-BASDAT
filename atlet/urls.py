from django.urls import path
from atlet import views

app_name = "atlet"

urlpatterns = [
   path('register/', views.register_atlet, name="register-atlet"),
   path('dashboard/', views.dashboard_atlet, name="dashboard_atlet"),
   path('tes_kualifikasi/', views.tes_kualifikasi, name="tes_kualifikasi")
]