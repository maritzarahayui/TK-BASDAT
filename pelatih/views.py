from django.shortcuts import render


def register_pelatih(request):
    return render(request, "register_pelatih.html")

def dashboard_pelatih(request):
    return render(request, "dashboard_pelatih.html")

