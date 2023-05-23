from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db import *
from utils.query import query
from django.views.decorators.csrf import csrf_exempt

def verify(request):
    try:
        request.session["username"]
        return True
    except:
        return False

def get_session_data(request):
    if not verify(request):
        return {}
    try:
        return {"username": request.session["username"], "role": request.session["role"]}
    except:
        return {}

def home(request):
    return render(request, "home.html")

def login_form(request):
    if verify(request):
        if request.session["role"] == "atlet":
            return redirect("/atlet")
        elif request.session["role"] == "pelatih":
            return redirect("/pelatih")
        elif request.session["role"] == "umpire":
            return redirect("/umpire")
    return render(request, "login.html")

def get_role(email):
    res = query(f"SELECT * FROM ADMIN WHERE EMAIL='{email}'")
    if len(res) > 0:
        return 'atlet'
    
    res = query(f"SELECT * FROM customer WHERE EMAIL='{email}'")
    if len(res) > 0:
        return 'pelatih'
    
    res = query(f"SELECT * FROM courier WHERE EMAIL='{email}'")
    if len(res) > 0:
        return 'umpire'
    
@csrf_exempt
def login(request):
    next = request.GET.get("next")
    cont = {}

    if request.method != "POST":
        return login_view(request)

    username=''
    password=''
    
    if verify(request):
        username = str(request.session["username"])
        password = str(request.session["password"])
    else:
        username = str(request.POST["username"])
        password = str(request.POST["password"])

    if not username or not password :
        cont["berhasil"] = True
        return render(request, "login.html", cont)

    print(username, password)
    role = get_role(username)
    print(role)
    if role == "" or role == None:
        if username and password :
            cont["gagal"] = True
            return render(request, "login.html", cont)

        return login_view(request)
    else:
        request.session["username"] = username
        request.session["password"] = password
        request.session["role"] = role
        request.session.set_expiry(0)
        request.session.modified = True

        if next != None and next != "None":
            print('salah masuk')
            return redirect(next)
        else:   
            print('masuk')
            if role == "atlet":
                return redirect("/atlet/")
            elif role == "pelatih":
                res = query(f"SELECT * FROM restaurant WHERE EMAIL='{username}'")[0]
                request.session['rname'] = res['rname']
                request.session['rbranch'] = res['rbranch']
                return redirect("/pelatih/")
            elif role == "umpire":
                return redirect("/umpire/")

def login_view(request):
    if not verify(request):
        return render(request, "login.html")
    else:
        return render(request, "login.html")
    
def logout(request):
    next=request.GET.get("next")
    if not verify(request):
        return redirect("/login/")
    request.session.flush()
    request.session.clear_expired()
    if next!= None and next!="None":
        return redirect(next)
    return redirect("/")

# def login(request):
#     if "nama" in request.session:
#         nama = request.session['nama']
#         email = request.session['email']
#         role = request.session['role']
#         auth = {
#             "nama": nama,
#             "email":email,
#             "role": role
#         }
#         return redirect('/atlet')
#     return render(request, 'login.html')


# def loginHelper(request):
#     # DB Connection
#     cur = connection.cursor()

#     # SQL Query
#     cur.execute("""SELECT M.id, M.nama,M.email FROM MEMBER M, ATLET A
#                     WHERE M.id=A.id;""")
#     atlet = cur.fetchall()
#     cur.execute("""SELECT M.id, M.nama,M.email FROM MEMBER M, PELATIH P
#                     WHERE M.id=P.id;""")
#     pelatih = cur.fetchall()
#     cur.execute("""SELECT M.id, M.nama,M.email FROM MEMBER M, UMPIRE U
#                     WHERE M.id=U.id;""")
#     umpire = cur.fetchall()

     
#     nama = request.GET.get('nama', None)
#     email = request.GET.get('email', None)

#     isValid = False
#     role = False

#     for a in atlet:
#         if(a[0] == nama and a[1] == email):
#             isValid = True
#             role = 'atlet'
#             break
#     for a in pelatih:
#         if(a[0] == nama and a[1] == email):
#             isValid = True
#             role = 'pelatih'
#             break
#     for a in umpire:
#         if(a[0] == nama and a[1] == email):
#             isValid = True
#             role = 'umpire'
#             break
#     data = dict()
#     if isValid:
#         data = {
#             "status": "success",
#         }
#         request.session['role'] = role
#     else:
#         data = {
#             "status" : "failed",
#         }
#     cur.close()
    
#     return JsonResponse(data)



def register(request):
    return render(request, "register.html")