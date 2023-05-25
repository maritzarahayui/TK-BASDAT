from django.urls import path
from umpire import views

app_name = "umpire"

urlpatterns = [
    path('pertandingan/<event>/<partai>/<tahun>', views.pertandingan_page, name="pertandingan_page"),
    path('register/', views.register_umpire, name="register-umpire"),
    path('semifinal/', views.semifinal_page, name="semifinal_page"),
    path('juara-3/', views.juara3_page, name="juara3_page"),
    path('final/', views.final_page, name="final_page"),
    path('hasil-pertandingan/', views.hasil_pertandingan,
         name="hasil_pertandingan"),
    path('', views.dashboard_umpire, name="dashboard_umpire"),
    path('list_event/', views.list_event, name="list_event"),
    path('get_daftar_atlet/', views.get_daftar_atlet, name="get_daftar_atlet"),
    path('buat_ujian_kualifikasi/', views.buat_ujian_kualifikasi, name="buat_ujian_kualifikasi"),
    path('list_ujian_kualifikasi/', views.list_ujian_kualifikasi_umpire, name="list_ujian_kualifikasi"),
    path('riwayat_ujian_kualifikasi/', views.riwayat_ujian_kualifikasi_umpire, name="riwayat_ujian_kualifikasi"),
    path('simpan_pertandingan', views.simpan_pertandingan, name='simpan_pertandingan'),
]
