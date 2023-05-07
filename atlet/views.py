from django.shortcuts import render

def register_atlet(request):
    return render(request, "register_atlet.html")

def dashboard_atlet(request):
    return render(request, "dashboard_atlet.html")

def tes_kualifikasi(request):
    return render(request, "tes_kualifikasi.html")

def form_kualifikasi(request):
    return render(request, "form_kualifikasi.html")