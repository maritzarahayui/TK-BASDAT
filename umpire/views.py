from django.shortcuts import render


def register_umpire(request):
    return render(request, "register_umpire.html")


def dashboard_umpire(request):
    return render(request, "dashboard_umpire.html")


def pertandingan_page(request):
    return render(request, "pertandingan.html")


def semifinal_page(request):
    return render(request, "semifinal_page.html")


def juara3_page(request):
    return render(request, "juara3_page.html")


def final_page(request):
    return render(request, "final_page.html")


def hasil_pertandingan(request):
    return render(request, "hasil_pertandingan.html")


def list_event(request):
    return render(request, "list_event.html")
