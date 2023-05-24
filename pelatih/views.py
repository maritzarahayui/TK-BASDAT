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

# @login_required
@csrf_exempt
def daftar_atlet(request):
    cursor = connection.cursor()
    if request.method == 'POST':
        nama_pelatih = request.session["nama"]
        id_atlet = request.POST.get("id_atlet")

        cursor.execute(
            f"""
            SELECT ID FROM MEMBER WHERE NAMA = '{nama_pelatih}';
            """
        )

        id_peletih = cursor.fetchone()[0]

        if id_atlet:
            cursor.execute(
                f"""
                INSERT INTO ATLET_PELATIH VALUES ('{id_peletih}', '{id_atlet}');
                """
            )

            return redirect("/pelatih/list-atlet")

    cursor.execute(
        f"""
        SELECT M.Nama, M.id FROM MEMBER M, ATLET A WHERE M.ID=A.ID ORDER BY M.nama;
        """
    )

    result = cursor.fetchall()

    daftar_atlet = []

    for res in result:
        daftar_atlet.append(
            {
                "nama_atlet": res[0],
                "id_atlet": res[1]
            }
        )

    context = {
        "daftar_atlet": daftar_atlet
    }

    return render(request, 'daftar_atlet.html', context)

# @login_required
def list_atlet(request):
    nama_pelatih = request.session["nama"]

    cursor = connection.cursor()

    cursor.execute(
        f"""
        select id from member m where m.nama = '{nama_pelatih}'
        """
    )

    id_pelatih = cursor.fetchone()[0]

    cursor.execute(f"""
                        SELECT MA.Nama, MA.Email, A.World_rank
                        FROM MEMBER MA
                        JOIN ATLET A ON MA.ID = A.ID
                        JOIN ATLET_PELATIH AP ON A.ID = AP.ID_Atlet
                        JOIN PELATIH P ON AP.ID_Pelatih = P.ID
                        WHERE p.id= '{id_pelatih}'""")

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
