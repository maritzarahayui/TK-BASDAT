from django.shortcuts import render
import psycopg2
from django.db import *


def register_atlet(request):
    return render(request, "register_atlet.html")


def dashboard_atlet(request):
    return render(request, "dashboard_atlet.html")


def tes_kualifikasi(request):
    return render(request, "tes_kualifikasi.html")


def form_kualifikasi(request):

    # DB Connection
    cur = connection.cursor()

    # SQL Query
   
    # cur.execute(""" SELECT * FROM ujian_kualifikasi; """)   
    # dataUjian = cur.fetchall() 

    # sql_batch, sql_tahun, sql_tempat, sql_tanggal = ([] for i in range(4))
    # for data in dataUjian:
    #         sql_batch.append(data[0])
    #         sql_tahun.append(data[1])
    #         sql_tempat.append(data[2])
    #         sql_tanggal.append(str(data[3]))
    #         print(sql_tanggal)

    cur.execute(""" SELECT tanggal FROM ujian_kualifikasi; """)   
    tanggal = cur.fetchall() 
    cur.execute(""" SELECT tempat FROM ujian_kualifikasi; """)   
    tempat = cur.fetchall() 

    sql_tanggal = []
    for data in tanggal:
            sql_tanggal.append(str(data[0]))
    sql_tempat = []
    for data in tempat:
            sql_tempat.append(data[0])

  
    context =  {
        "tempat" : sql_tempat,
        "tanggal" :  sql_tanggal,
    }

    return render(request, "form_kualifikasi.html",  context)


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

def datetime_to_string(data):
    listTanggal = str(data[0]).split("-")
    result = ""
    result += listTanggal[1]
    result += " "
    if listTanggal[2] == "01" :
        result += "Januari"
    elif listTanggal[2] == "02" :
        result += "Februari"
    elif listTanggal[2] == "03" :
        result += "Maret"
    elif listTanggal[2] == "04" :
        result += "April"
    elif listTanggal[2] == "05" :
        result += "Mei"
    elif listTanggal[2] == "06" :
        result += "Juni"
    elif listTanggal[2] == "07" :
        result += "Juli"
    elif listTanggal[2] == "08" :
        result += "Agustus"
    elif listTanggal[2] == "09" :
        result += "September"
    elif listTanggal[2] == "10" :
        result += "Oktober"
    elif listTanggal[2] == "11" :
        result += "November"
    elif listTanggal[2] == "12" :
        result += "Desember"
    result += " "
    result += listTanggal[0]  
    return result
