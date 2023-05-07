from django.shortcuts import render

def login(request):
    return render(request, "general/login.html")

def register(request):
    return render(request, "general/register.html")