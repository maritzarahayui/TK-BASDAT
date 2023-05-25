from django.urls import path
from pelatih import views

app_name = "pelatih"

urlpatterns = [
  path('register/', views.register_pelatih, name="register-pelatih"),
  path('', views.dashboard_pelatih, name="dashboard_pelatih"),
  path('daftar-atlet/', views.daftar_atlet, name="daftar_atlet"),
  path('list-atlet/', views.list_atlet, name="list_atlet"),
]
