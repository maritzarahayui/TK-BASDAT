from django.urls import path
from atlet import views

app_name = "atlet"

urlpatterns = [
    path('register/', views.register_atlet, name="register-atlet"),
    path('', views.dashboard_atlet, name="dashboard_atlet"),
    path('tes-kualifikasi/', views.tes_kualifikasi, name="tes_kualifikasi"),
    path('list_ujian_kualifikasi/', views.list_ujian_kualifikasi_atlet, name="list_ujian_kualifikasi"),
    path('daftar-event/', views.daftar_event, name="daftar_event"),
    path('daftar-event-detail/<str:stadium_id>/', views.daftar_event_detail,
         name="daftar_event_detail"),
    path('pilih-kategori/<str:event_id>/', views.pilih_kategori, name="pilih_kategori"),
    path('enrolled_partai_kompetisi/', views.enrolled_partai_kompetisi, name="enrolled_partai_kompetisi"),
    path('enrolled_event/', views.enrolled_event, name="enrolled_event"),
    path('daftar_sponsor/', views.daftar_sponsor, name="daftar_sponsor"),
    path('list_sponsor/', views.list_sponsor, name="list_sponsor"),
    path('riwayat_ujian_kualifikasi/', views.riwayat_ujian_kualifikasi_atlet, name="riwayat_ujian_kualifikasi"),
]
