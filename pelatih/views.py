from django.shortcuts import render
from uuid import uuid1
from utils.query import *

def register_pelatih(request):
    if request.method == "post".upper():
        id = uuid1()
        nama = request.POST.get("nama")
        email = request.POST.get("email")
        tgl_mulai = request.POST.get("tgl_mulai")
        spesialisasi = {
            "tunggal_putra":request.POST.get('tunggal_putra'),
            "tunggal_putri":request.POST.get('tunggal_putri'),
            "ganda_putra":request.POST.get('ganda_putra'),
            "ganda_putri":request.POST.get('ganda_putri'),
            "ganda_campuran":request.POST.get('ganda_campuran')
        }
        id_spesialisasi = {
            "tunggal_putra":str(exec("SELECT S.id FROM spesialisasi S WHERE S.spesialisasi = 'Tunggal Putra';")[0][0]),
            "tunggal_putri":str(exec("SELECT S.id FROM spesialisasi S WHERE S.spesialisasi = 'Tunggal Putri';")[0][0]),
            "ganda_putra":str(exec("SELECT S.id FROM spesialisasi S WHERE S.spesialisasi = 'Ganda Putra';")[0][0]),
            "ganda_putri":str(exec("SELECT S.id FROM spesialisasi S WHERE S.spesialisasi = 'Ganda Putri';")[0][0]),
            "ganda_campuran":str(exec("SELECT S.id FROM spesialisasi S WHERE S.spesialisasi = 'Ganda Campuran';")[0][0])
        }

        check_mail = exec(f"""SELECT * FROM MEMBER WHERE email='{email}'""")
        if check_mail:
            msg = "Email sudah terdaftar"
            return render(request, "register_pelatih.html", {"msg":msg})
        else:
            exec(f"""INSERT INTO MEMBER VALUES ('{id}', '{nama}', '{email}')""")
            exec(f"""INSERT INTO PELATIH VALUES ('{id}', '{tgl_mulai}')""")

            for key_spesialisasi in spesialisasi:
                if (spesialisasi[key_spesialisasi] is not None):
                    exec(f"INSERT INTO PELATIH_SPESIALISASI VALUES ('{id}','{id_spesialisasi[key_spesialisasi]}');")

            return render(request, 'register_pelatih.html', {"msg":"Berhasil mendaftar"})
    return render(request, "register_pelatih.html")

def dashboard_pelatih(request):
    return render(request, "dashboard_pelatih.html")

def daftar_atlet(request):
    return render(request, "daftar_atlet.html")

def list_atlet(request):
    return render(request, "list_atlet.html")

