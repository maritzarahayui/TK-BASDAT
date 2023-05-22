from django.shortcuts import render
import psycopg2

def connectDb():
    return psycopg2.connect(
        user='postgres',
        password='VqhDHXgGPL8avdUHqCWP',
        host='containers-us-west-72.railway.app',
        databases='railway',
        port='7729',
    )

def register_atlet(request):
    return render(request, "register_atlet.html")


def dashboard_atlet(request):
    return render(request, "dashboard_atlet.html")


def tes_kualifikasi(request):

    # # DB Connection
    # con = connectDb()
    # cur = con.cursor()
        
    # # SQL Query
    # cur.execute(""" SELECT tanggal FROM ujian_kualifikasi; """)   
    # tanggal_pelaksanaan = cur.fetchall()     
    # cur.execute(""" SELECT tempat FROM ujian_kualifikasi; """)   
    # tempat_pelaksanaan = cur.fetchall()   

    # content = {
    #     'tanggal_pelaksanaan' : tanggal_pelaksanaan,
    #     'tempat_pelaksanaan' : tempat_pelaksanaan,
    # }


    return render(request, "tes_kualifikasi.html")


def form_kualifikasi(request):

    return render(request, "form_kualifikasi.html")


def daftar_event(request):
    return render(request, "daftar_event.html")


def daftar_event_detail(request):
    return render(request, "daftar_event_detail.html")


def pilih_kategori(request):
    return render(request, "pilih_kategori.html")


def enrolled_event(request):
    return render(request, "enrolled_event.html")


def daftar_sponsor(request):
    return render(request, "daftar_sponsor.html")
