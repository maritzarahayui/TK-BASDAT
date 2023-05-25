from django.shortcuts import render, redirect
from collections import namedtuple
from django.db import *
import psycopg2
from uuid import uuid1
from utils.query import *

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
    if request.method == "post".upper():
        id = uuid1()
        nama = request.POST.get("nama")
        email = request.POST.get("email")
        negara = request.POST.get("negara")
        tgl_lahir = request.POST.get("tanggal-lahir")
        if request.POST.get('question1') == "on":
            play = False
        else:
            play = True
        tinggi = request.POST.get("tinggi-badan")
        if request.POST.get('question2') == "on":
            kelamin = True
        else:
            kelamin = False
        
        error, check_mail = try_exec(f"SELECT * FROM member WHERE email = '{email}'")
        if check_mail:
            msg = "Email sudah terdaftar"
            return render(request, "register_atlet.html", {"msg": msg})
        else:
            error, res = try_exec(f"INSERT INTO member VALUES ('{id}', '{nama}', '{email}')")
            if error: 
                print(res)
                return render(request, "register_atlet.html", {"msg": "Gagal mendaftar"})

            error, res = try_exec(f"INSERT INTO atlet VALUES ('{id}', '{tgl_lahir}', '{negara}', {play}, '{tinggi}', null,{kelamin})")
            print(f"INSERT INTO atlet VALUES ('{id}', '{tgl_lahir}', '{negara}', {play}, '{tinggi}', null,{kelamin})")
            if error:
                print(res)
                return render(request, "register_atlet.html", {"msg": "Gagal mendaftar"})

            error, res = try_exec(f"INSERT INTO atlet_non_kualifikasi VALUES ('{id}')")
            if error: 
                print(res)
                return render(request, "register_atlet.html", {"msg": "Gagal mendaftar"})

            return render(request, "register_atlet.html", {"msg": "Berhasil mendaftar"})


    return render(request, "register_atlet.html")


def dashboard_atlet(request):
    nama = request.session["nama"]
    email = request.session["email"]
    id = get_query(
        f'''SELECT id FROM MEMBER WHERE nama='{nama}' AND email = '{email}'
        '''
    )[0][0]

    query = get_query(
        f'''SELECT m.nama, negara_asal, email, tgl_lahir, play_right, height, jenis_kelamin, world_rank FROM ATLET A, MEMBER M WHERE A.id = '{id}' AND M.id = A.id GROUP BY m.nama, negara_asal, email, tgl_lahir, play_right, height, jenis_kelamin, world_rank;
        '''
    )
    
    query.append(get_query(
        f'''SELECT SUM(total_point) FROM POINT_HISTORY WHERE id_atlet = '{id}'
        '''
    ))
    
    query.append(get_query(
        f'''SELECT nama FROM MEMBER M, ATLET_PELATIH AP
        WHERE AP.id_atlet = '{id}' AND AP.id_pelatih = M.id
        '''
    ))
    
    if (query[0][4]):
        play = "Right Hand"
    else:
        play = "Left Hand"
    
    if (query[0][6]):
        jenis_kelamin = "Laki-laki"
    else:
        jenis_kelamin = "Perempuan"
        
    if (query[0][7] == None):
        world_rank = "-"
        status = "Not Qualified"
    else:
        world_rank = query[0][7]
        status = "Qualified"
        
    if (query[2] ==  []):
        pelatih = "-"
    else:
        pelatih = query[2][0][0]
        
    if (query[1][0][0] == None):
        poin = 0
    else:
        poin = query[1][0][0]
    
    context = {
        "nama": nama,
        "email": email,
        "negara": query[0][1],
        "tgl_lahir": query[0][3],
        "jenis_kelamin": jenis_kelamin,
        "play" : play,
        "status" : status,
        "height": query[0][5],
        "world_rank": world_rank,
        "pelatih" : pelatih,
        "poin" : poin
    }
    return render(request, "dashboard_atlet.html", context)


def tes_kualifikasi(request):

    # DB Connection
    cur = connection.cursor()
   
    # Sessions
    nama = request.session['nama']
    email = request.session['email']
    role = request.session['role']
    
    batch = request.session['batch']
    tempat_pelaksanaan = request.session['tempat_pelaksanaan']
    tanggal_pelaksanaan = request.session['tanggal_pelaksanaan']

    cur.execute(""" SELECT id FROM MEMBER WHERE nama = %s AND email = %s; """, [nama, email])
    id_atlet = cur.fetchone()[0] 

    print(id_atlet)
    print(batch)
    print(tempat_pelaksanaan)
    print(tanggal_pelaksanaan)

    if request.method == 'POST':
      
        option_1 = request.POST.get('1', '')
        option_2 = request.POST.get('2', '')
        option_3 = request.POST.get('3', '')
        option_4 = request.POST.get('4', '')
        option_5 = request.POST.get('5', '')

        score = 0
        if option_1 == 'benar':
            score += 1
        if option_2 == 'benar':
            score += 1
        if option_3 == 'benar':
            score += 1
        if option_4 == 'benar':
            score += 1
        if option_5 == 'benar':
            score += 1


        cur.execute(""" SELECT id FROM MEMBER WHERE nama = %s AND email = %s; """, [nama, email])
        id_atlet = cur.fetchone()[0] 

        if score >= 4:
            print("yeyyy lulus:)")
            #
        else:
            print("nooo ga lulus:(")
        print(score)
        return redirect('/' + role)
    return render(request, "tes_kualifikasi.html")


def list_ujian_kualifikasi_atlet(request):

    # DB Connection
    cur = connection.cursor()

    # SQL Query
    cur.execute(""" SELECT * FROM ujian_kualifikasi; """)   
    dataUjian = cur.fetchall() 

    batch, tahun, tempat, tanggal = ([] for i in range(4))
    for data in dataUjian:
            batch.append(data[0])
            tahun.append(data[1])
            tempat.append(data[2])
            tanggal.append(str(data[3]))

    context =  {}
    context['ujian'] = zip(batch,
                        tahun,
                        tempat,
                        tanggal)

    if request.method == 'POST':

        try:
            # Mengambil data dari POST
            batch = request.POST.get('batch')
            tempat_pelaksanaan = request.POST.get('tempat')
            tanggal_pelaksanaan = request.POST.get('tanggal')

            # Mengambil data dari Session
            nama = request.session['nama']
            email = request.session['email']
            cur.execute(""" SELECT id FROM MEMBER WHERE nama = %s AND email = %s; """, [nama, email])
            id_atlet = cur.fetchone()[0] 
            print(id_atlet)

            # Set data ke Session
            request.session['batch'] = batch
            request.session['tempat_pelaksanaan'] = tempat_pelaksanaan
            request.session['tanggal_pelaksanaan'] = tanggal_pelaksanaan

            # Cek 
            print(tahun)
            print(batch)
            print(tempat_pelaksanaan)
            print(tanggal_pelaksanaan)

            # Mengecek apakah dia atlet qualified atau not qualified
            cur.execute("""
                SELECT
                    CASE
                        WHEN EXISTS (
                            SELECT 1
                            FROM atlet_kualifikasi
                            WHERE id_atlet = %s
                        )
                        THEN 'Qualified'
                        ELSE 'Not Qualified'
                    END AS qualification_status
                FROM atlet
                WHERE id = %s;
            """, [id_atlet, id_atlet])
            status = cur.fetchone()[0]

            if status == 'Not Qualified':
                # SQL Query
                cur.execute("""
                    INSERT INTO atlet_nonkualifikasi_ujian_kualifikasi
                    VALUES (%s, %s, %s, %s, CAST(%s AS DATE), FALSE)
                """, [id_atlet, tahun, batch, tempat_pelaksanaan, tanggal_pelaksanaan])
                
                connection.commit()

            return redirect("/atlet/tes-kualifikasi")
        
        except Error as e:
       
            print("uda pernah ngambil")
            error_message = "Anda sudah pernah mengambil ujian kualifikasi yang dipilih."
            context["error_message"] =  error_message            
            return render(request, "form_kualifikasi.html", context)

    return render(request, "list_ujian_kualifikasi_atlet.html",  context)


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
    nama = request.session["nama"]
    email = request.session["email"]
    id = get_query(
        f'''SELECT id FROM MEMBER WHERE nama='{nama}' AND email = '{email}'
        '''
    )[0][0]
    
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
    nama = request.session["nama"]
    email = request.session["email"]
    id = get_query(
        f'''SELECT id FROM MEMBER WHERE nama='{nama}' AND email = '{email}'
        '''
    )[0][0]
    
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
    nama = request.session["nama"]
    email = request.session["email"]
    id = get_query(
        f'''SELECT id FROM MEMBER WHERE nama='{nama}' AND email = '{email}'
        '''
    )[0][0]

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
    nama = request.session["nama"]
    email = request.session["email"]
    id = get_query(
        f'''SELECT id FROM MEMBER WHERE nama='{nama}' AND email = '{email}'
        '''
    )[0][0]

    query = get_query(
        f'''SELECT nama_brand, tgl_mulai, tgl_selesai
        FROM atlet_sponsor, sponsor
        WHERE id_sponsor = id AND ID_atlet = '{id}'
        '''
    )
    
    return render(request, "list_sponsor.html", {"query" : query})

def riwayat_ujian_kualifikasi_atlet(request):

    # DB Connection
    cur = connection.cursor()

    # Mengambil data dari Session
    nama = request.session['nama']
    email = request.session['email']
    cur.execute(""" SELECT id FROM MEMBER WHERE nama = %s AND email = %s; """, [nama, email])
    id_atlet = cur.fetchone()[0] 
    print(id_atlet)

    # SQL Query
    cur.execute(
        """ 
            SELECT DISTINCT U.tahun, U.batch, U.tempat, U.tanggal, N.hasil_lulus
            FROM member M, atlet A, ujian_kualifikasi U, ATLET_NONKUALIFIKASI_UJIAN_KUALIFIKASI N
            WHERE M.id = %s AND N.id_atlet = M.id AND N.tempat = U.tempat
            AND N.batch = U.batch AND N.tempat = U.tempat AND N.tanggal = U.tanggal; 
        """,
        [id_atlet]
    )   
    dataUjian = cur.fetchall() 

    tahun, batch, tempat, tanggal, hasil = ([] for i in range(5))
    for data in dataUjian:
            tahun.append(data[0])
            batch.append(data[1])
            tempat.append(data[2])
            tanggal.append(str(data[3]))
            hasil.append(data[4])

    context =  {}
    context['ujian'] = zip(tahun,
                        batch,
                        tempat,
                        tanggal,
                        hasil)
    
    return render(request, "riwayat_ujian_kualifikasi_atlet.html",  context)