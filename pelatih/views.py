from django.shortcuts import render


def register_pelatih(request):
    return render(request, "register_pelatih.html")

def dashboard_pelatih(request):
    return render(request, "dashboard_pelatih.html")

def daftar_atlet(request):
    return render(request, "daftar_atlet.html")

def list_atlet(request):
    return render(request, "list_atlet.html")

