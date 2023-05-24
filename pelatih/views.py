from django.shortcuts import render, redirect
from pprint import pprint
from utils.query import query
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt


def register_pelatih(request):
    return render(request, "register_pelatih.html")


def dashboard_pelatih(request):
    return render(request, "dashboard_pelatih.html")


def list_atlet(request):
    nama_pelatih = request.session["nama"]
    with connection.cursor() as cursor:
        cursor.execut = ("""
                        SELECT MA.Nama, MA.Email, A.World_rank
                        FROM MEMBER MA
                        JOIN ATLET A ON MA.ID = A.ID
                        JOIN ATLET_PELATIH AP ON A.ID = AP.ID_Atlet
                        JOIN PELATIH P ON AP.ID_Pelatih = P.ID
                        WHERE MA.Nama = '{}'""".format(nama_pelatih))
    latih_atlet_raw = cursor.fetchall()

    latih_atlet = []

    for res in latih_atlet_raw:
        latih_atlet.append(
            {
                "nama": res[0],
                "email": res[1],
                "world_rank": res[2],
            }
        )

    context = {
        "latih_atlet": latih_atlet
    }
    return render(request, "list_atlet.html", context)


def daftar_atlet(request):
    if request.method == 'POST':
        # list_atlet = query(
        #     "SELECT M.Nama FROM MEMBER M, ATLET A WHERE M.ID=A.ID;")
        # context = {
        #     "list_atlet": list_atlet,
        #     "fail": False
        # }
        # return render(request, "daftar_atlet.html", context)

        nama_atlet = request.POST.get("nama_atlet")
        if not nama_atlet:
            list_atlet = query(
                "SELECT M.Nama FROM MEMBER M, ATLET A WHERE M.ID=A.ID;")
            context = {
                "list_atlet": list_atlet,
            }
            return render(request, "daftar_atlet.html", context)

    nama_pelatih = request.session["nama"]
    id_pelatih = str(query(
        f"SELECT P.ID FROM MEMBER M, PELATIH P WHERE M.ID=P.ID AND M.Nama='{nama_pelatih}';")[0]["id"])
    id_atlet = str(query(
        f"SELECT A.ID FROM MEMBER M, ATLET A WHERE M.ID=A.ID AND M.Nama='{nama_atlet}';")[0]["id"])
    query(f"INSERT INTO ATLET_PELATIH VALUES ('{id_pelatih}', '{id_atlet}');")
    return redirect('/pelatih/list-atlet')
