from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import *
from utils.query import query
from django.views.decorators.csrf import csrf_exempt
from utils.query import *


def home(request):
    return render(request, "home.html")

def login(request):
    if "nama" in request.session:
        nama = request.session['nama']
        email = request.session['email']
        role = request.session['role']
        print(nama)
        print(email)
        print(role)
        return redirect('/' + role)

    return render(request, 'login.html',)


def loginHelper(request):
    # DB Connection
    cur = connection.cursor()

    # SQL Query
    cur.execute("""SELECT M.id, M.nama,M.email FROM MEMBER M, ATLET A
                    WHERE M.id=A.id;""")
    atlet = cur.fetchall()
    cur.execute("""SELECT M.id, M.nama,M.email FROM MEMBER M, PELATIH P
                    WHERE M.id=P.id;""")
    pelatih = cur.fetchall()
    cur.execute("""SELECT M.id, M.nama,M.email FROM MEMBER M, UMPIRE U
                    WHERE M.id=U.id;""")
    umpire = cur.fetchall()

     
    nama = request.GET.get('nama', None)
    email = request.GET.get('email', None)

    isValid = False
    role = False

    for a in atlet:
        if(a[1] == nama and a[2] == email):
            isValid = True
            role = 'atlet'
            break
    for a in pelatih:
        if(a[1] == nama and a[2] == email):
            isValid = True
            role = 'pelatih'
            break
    for a in umpire:
        if(a[1] == nama and a[2] == email):
            isValid = True
            role = 'umpire'
            break
    data = dict()
    if isValid:
        data = {
            "status": "success",
            "role" : role,
        }
        request.session['nama'] = nama
        request.session['email'] = email
        request.session['role'] = role
    else:
        data = {
            "status" : "failed",
        }
    
    return JsonResponse(data)

def logout(request):
    request.session.clear()
    return redirect("/")

def register(request):
    return render(request, "register.html")