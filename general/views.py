from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import *

def home(request):
    return render(request, "home.html")

def login(request):
    if "nama" in request.session:
        nama = request.session['nama']
        email = request.session['email']
        role = request.session['role']
        auth = {
            "nama": nama,
            "email":email,
            "role": role
        }
        return redirect('/atlet')
    return render(request, 'login.html')


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
        if(a[0] == nama and a[1] == email):
            isValid = True
            role = 'atlet'
            break
    for a in pelatih:
        if(a[0] == nama and a[1] == email):
            isValid = True
            role = 'pelatih'
            break
    for a in umpire:
        if(a[0] == nama and a[1] == email):
            isValid = True
            role = 'umpire'
            break
    data = dict()
    if isValid:
        data = {
            "status": "success",
        }
        request.session['role'] = role
    else:
        data = {
            "status" : "failed",
        }
    cur.close()
    
    return JsonResponse(data)
        

def register(request):
    return render(request, "register.html")