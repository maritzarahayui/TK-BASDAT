from django.shortcuts import render
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
        # print("An exception occurred:", str(e))
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
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT E.nama_stadium, E.negara, S.kapasitas
            FROM STADIUM S, EVENT E
            WHERE S.nama = E.nama_stadium
        """)
        stadium_raw = cursor.fetchall()

        stadium = []

        for res in stadium_raw:
            stadium.append(
                {
                    "nama_stadium": res[0],
                    "negara": res[1],
                    "kapasitas": res[2],
                }
            )

        context = {
            "stadium": stadium
        }

        return render(request, "daftar_event.html", context)
    

# di dummy data tgl_mulai nya 2021/2022 semua jd wassalamualaikum alias kosong

def daftar_event_detail(request, stadium_id):
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT E.nama_event, E.total_hadiah, E.tgl_mulai, E.kategori_superseries, E.nama_stadium
            FROM EVENT E
            JOIN STADIUM S ON S.nama = E.nama_stadium
            WHERE E.tgl_mulai > CURRENT_DATE AND S.nama = %s
        """, [stadium_id])
        event_raw = cursor.fetchall()

        event = []

        for res in event_raw:
            event.append(
                {
                    "nama_event": res[0],
                    "total_hadiah": res[1],
                    "tgl_mulai": res[2],
                    "kategori_superseries": res[3],
                }
            )

        context = {
            "event": event
        }

        return render(request, "daftar_event_detail.html", context)


def pilih_kategori(request):
    return render(request, "pilih_kategori.html")

def enrolled_partai_kompetisi(request):
    # id = str(request.session["id"]).strip()
    id = 'e2fac2f5-b3d7-4987-a386-45de0aeb812e'
    
    query = get_query(
        f'''SELECT par.nama_event, par.tahun_event, nama_stadium, par.jenis_partai, total_hadiah, kategori_superseries, tgl_mulai, tgl_selesai
        FROM EVENT E, PARTAI_KOMPETISI par, PESERTA_KOMPETISI pes, PARTAI_PESERTA_KOMPETISI kom
        WHERE pes.nomor_peserta = kom.nomor_peserta AND kom.jenis_partai = par.jenis_partai AND kom.nama_event = par.nama_event AND kom.tahun_event = par.tahun_event AND par.nama_event = e.nama_event AND e.tahun_event = par.tahun_event AND id_atlet_kualifikasi = '{id}';
        '''
    )
    
    if query == []:
        id_ganda = get_query(
            f'''SELECT id_atlet_ganda
            FROM ATLET_GANDA
            WHERE id_atlet_kualifikasi = '{id}' OR id_atlet_kualifikasi_2 = '{id}'
            '''
        )
        
        query = get_query(
            f'''SELECT par.nama_event, par.tahun_event, nama_stadium, par.jenis_partai, total_hadiah, kategori_superseries, tgl_mulai, tgl_selesai
            FROM EVENT E, PARTAI_KOMPETISI par, PESERTA_KOMPETISI pes, PARTAI_PESERTA_KOMPETISI kom
            WHERE pes.nomor_peserta = kom.nomor_peserta AND kom.jenis_partai = par.jenis_partai AND kom.nama_event = par.nama_event AND kom.tahun_event = par.tahun_event AND par.nama_event = e.nama_event AND e.tahun_event = par.tahun_event AND id_atlet_ganda = '{id_ganda[0].id_atlet_ganda}';
            '''
        )
    
    return render(request, "enrolled_partai_kompetisi.html", {"query": query})

def enrolled_event(request):
    # id = str(request.session["id"]).strip()
    id = 'e2fac2f5-b3d7-4987-a386-45de0aeb812e'
    # id = 'c2b8357e-7865-4939-8be0-97b283320eaf'
    
    query = get_query(
        f'''SELECT rol.nama_event, rol.tahun, nama_stadium, total_hadiah, kategori_superseries, tgl_mulai, tgl_selesai, pes.nomor_peserta
        FROM EVENT E, PESERTA_KOMPETISI pes, PESERTA_MENDAFTAR_EVENT rol
        WHERE pes.nomor_peserta = rol.nomor_peserta AND e.nama_event = rol.nama_event AND e.tahun_event = rol.tahun AND id_atlet_kualifikasi = '{id}';
        '''
    )
    
    if query == []:
        id_ganda = get_query(
            f'''SELECT id_atlet_ganda
            FROM ATLET_GANDA
            WHERE id_atlet_kualifikasi = '{id}' OR id_atlet_kualifikasi_2 = '{id}'
            '''
        )
        
        query = get_query(
            f'''SELECT rol.nama_event, rol.tahun, nama_stadium, total_hadiah, kategori_superseries, tgl_mulai, tgl_selesai, pes.nomor_peserta
        FROM EVENT E, PESERTA_KOMPETISI pes, PESERTA_MENDAFTAR_EVENT rol
        WHERE pes.nomor_peserta = rol.nomor_peserta AND e.nama_event = rol.nama_event AND e.tahun_event = rol.tahun AND id_atlet_ganda = '{id_ganda[0].id_atlet_ganda}';
            '''
        )
    
    if request.method != "POST":    
        return render(request, "enrolled_event.html", {"query" : query})
    
    nama_tahun_nomor = request.POST.urlencode().split("&")[1].split("=")[0].split("+")
    nama_event = ' '.join(nama_tahun_nomor[:-2])
    tahun_event = nama_tahun_nomor[-2]
    nomor_peserta = nama_tahun_nomor[-1]

    delete = get_query(
        f'''DELETE FROM PESERTA_MENDAFTAR_EVENT
        WHERE nomor_peserta = '{nomor_peserta}' AND nama_event = '{nama_event}' AND tahun = '{tahun_event}'
        ''')
    
    if (type(delete) != InternalError):
        get_query(
            f'''DELETE FROM PARTAI_PESERTA_KOMPETISI
        WHERE nomor_peserta = '{nomor_peserta}' AND nama_event = '{nama_event}' AND tahun_event = '{tahun_event}'
            '''
        )
        
    print(delete)
    
    query = get_query(
        f'''SELECT rol.nama_event, rol.tahun, nama_stadium, total_hadiah, kategori_superseries, tgl_mulai, tgl_selesai, pes.nomor_peserta
        FROM EVENT E, PESERTA_KOMPETISI pes, PESERTA_MENDAFTAR_EVENT rol
        WHERE pes.nomor_peserta = rol.nomor_peserta AND e.nama_event = rol.nama_event AND e.tahun_event = rol.tahun AND id_atlet_kualifikasi = '{id}';
        '''
    )
    
    if query == []:
        id_ganda = get_query(
            f'''SELECT id_atlet_ganda
            FROM ATLET_GANDA
            WHERE id_atlet_kualifikasi = '{id}' OR id_atlet_kualifikasi_2 = '{id}'
            '''
        )
        
        query = get_query(
            f'''SELECT rol.nama_event, rol.tahun, nama_stadium, total_hadiah, kategori_superseries, tgl_mulai, tgl_selesai, pes.nomor_peserta
        FROM EVENT E, PESERTA_KOMPETISI pes, PESERTA_MENDAFTAR_EVENT rol
        WHERE pes.nomor_peserta = rol.nomor_peserta AND e.nama_event = rol.nama_event AND e.tahun_event = rol.tahun AND id_atlet_ganda = '{id_ganda[0].id_atlet_ganda}';
            '''
        )    
    
    return render(request, "enrolled_event.html", {"query" : query})

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
