from django.shortcuts import render


def register_atlet(request):
    return render(request, "register_atlet.html")


def dashboard_atlet(request):
    return render(request, "dashboard_atlet.html")


def tes_kualifikasi(request):
    return render(request, "tes_kualifikasi.html")


def form_kualifikasi(request):
    return render(request, "form_kualifikasi.html")


def daftar_event(request):
    return render(request, "daftar_event.html")


def daftar_event_detail(request):
    return render(request, "daftar_event_detail.html")


def pilih_kategori(request):
    return render(request, "pilih_kategori.html")


def enrolled_event(request):
    return render(request, "enrolled_event.html")


def daftar_sponsor(request):
    return render(request, "daftar_sponsor.html")
