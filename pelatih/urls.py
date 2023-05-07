from django.urls import path
from pelatih import views

app_name = "pelatih"

urlpatterns = [
  path('register/', views.register_pelatih, name="register-pelatih"),
  path('dashboard/', views.dashboard_pelatih, name="dashboard_pelatih")
]