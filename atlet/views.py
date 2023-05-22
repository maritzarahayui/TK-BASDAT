from django.shortcuts import redirect, render
from collections import namedtuple
from django.db import *
import psycopg2

def connectDb():
    return psycopg2.connect(
        user='postgres',
        password='VqhDHXgGPL8avdUHqCWP',
        host='containers-us-west-72.railway.app',
        databases='railway',
        port='7729',
    )
    
def namedtuplefetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]

def get_query(str):
    '''Execute SQL query and return its result as a list'''
    cursor = connection.cursor()
    result = []
    try:
        cursor.execute(str)
        result = namedtuplefetchall(cursor)
    except Exception as e:
        result = e
    finally:
        cursor.close()
        return result

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
    # id = str(request.session["id"]).strip()
    id = 'aa8a676a-07a3-4eb6-bcec-54a74ee35c93'

    query = get_query(
        f'''SELECT nama_brand
        FROM sponsor
        WHERE id NOT IN 
        (SELECT id_sponsor FROM atlet_sponsor WHERE id_atlet = '{id}')
        '''
    )
    
    if request.method != "POST":
        return render(request, "daftar_sponsor.html", {"query":query})
    
    nama_brand = request.POST["sponsor"]
    tgl_mulai = request.POST["tgl_selesai"]
    tgl_selesai = request.POST["tgl_selesai"]
    
    id_sponsor = get_query(
        f'''SELECT id
        FROM SPONSOR
        WHERE nama_brand = '{nama_brand}'
        '''
    )
    
    print(id_sponsor[0].id)
    
    get_query(
        f'''INSERT INTO atlet_sponsor
        VALUES ('{id}', '{id_sponsor[0].id}', '{tgl_mulai}', '{tgl_selesai}');
        '''
    )
    
    query = get_query(
        f'''SELECT nama_brand
        FROM sponsor
        WHERE id NOT IN 
        (SELECT id_sponsor FROM atlet_sponsor WHERE id_atlet = '{id}')
        '''
    )

    return render(request, "daftar_sponsor.html", {"query":query})

def list_sponsor(request):
    # id = str(request.session["id"]).strip()
    id = 'aa8a676a-07a3-4eb6-bcec-54a74ee35c93'

    query = get_query(
        f'''SELECT nama_brand, tgl_mulai, tgl_selesai
        FROM atlet_sponsor, sponsor
        WHERE id_sponsor = id AND ID_atlet = '{id}'
        '''
    )
    
    return render(request, "list_sponsor.html", {"query" : query})

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
