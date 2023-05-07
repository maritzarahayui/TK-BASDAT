from django.urls import path
from umpire import views

app_name = "umpire"

urlpatterns = [
  path('', views.pertandingan_page, name="pertandingan_page"),
  path('semifinal/', views.semifinal_page, name="semifinal_page"),
  path('juara-3/', views.juara3_page, name="juara3_page"),
  path('final/', views.final_page, name="final_page"),
  path('hasil-pertandingan/', views.hasil_pertandingan, name="hasil_pertandingan")
]