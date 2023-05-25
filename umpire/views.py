from django.shortcuts import render, redirect
from django.db import connection
from pprint import pprint
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from uuid import uuid1
from utils.query import *
from urllib.parse import unquote
from django.http import JsonResponse
import json
from django.db import transaction


def register_umpire(request):
    if request.method == "post".upper():
        id = uuid1()
        name = request.POST.get("nama")
        email = request.POST.get("email")
        negara = request.POST.get("negara")

        check_mail = exec(f"""SELECT * FROM MEMBER WHERE email='{email}'""")
        if check_mail:
            msg = "Email sudah terdaftar"
            return render(request, "register_umpire.html", {"msg": msg})
        else:
            exec(
                f"""INSERT INTO MEMBER VALUES ('{id}', '{name}', '{email}')""")
            exec(f"""INSERT INTO UMPIRE VALUES ('{id}', '{negara}')""")
            return render(request, 'register_umpire.html', {"msg": "Berhasil mendaftar"})

    return render(request, "register_umpire.html")


def dashboard_umpire(request):
    nama = request.session["nama"]
    email = request.session["email"]
    is_umpire = query(
        f"SELECT M.ID FROM MEMBER M, UMPIRE U WHERE M.ID=U.ID AND M.Email='{email}'")
    if len(is_umpire) > 0:
        request.session["id"] = str(is_umpire[0]['id'])
    with connection.cursor() as cursor:
        cursor.execute(f"""
        SELECT negara FROM MEMBER M, UMPIRE U WHERE M.ID=U.ID AND M.nama='{nama}' AND M.email='{email}';
        """)
        result = cursor.fetchone()
        negara = result[0]

    context = {
        "nama": nama,
        "email": email,
        "negara": negara
    }
    return render(request, "dashboard_umpire.html", context)


def pertandingan_page(request, event, partai, tahun):
    babak = request.GET.get("babak")

    sblm_babak = {
        'R2': 'R4',
        'R4': 'R8',
        'R8': 'R16',
        'R16': 'R32',
        'R32': '',
    }

    if babak:
        babak_sblm = sblm_babak[babak]
        list_peserta = query(f"""SELECT pk.* FROM partai_peserta_kompetisi ppk  INNER JOIN peserta_kompetisi pk ON pk.nomor_peserta = ppk.nomor_peserta INNER JOIN peserta_mengikuti_match pmm ON pmm.nomor_peserta = ppk.nomor_peserta WHERE ppk.nama_event = '{event}' AND ppk.jenis_partai = '{partai}' AND ppk.tahun_event = '{tahun}' AND pmm.jenis_babak = '{babak_sblm}' AND status_menang IS TRUE
        """)
    else:
        list_peserta = query(f"""SELECT pk.* FROM peserta_kompetisi AS pk INNER JOIN partai_peserta_kompetisi AS ppk ON pk.nomor_peserta = ppk.nomor_peserta WHERE ppk.jenis_partai = '{partai}' AND ppk.nama_event = '{event}' AND ppk.tahun_event = '{tahun}'
        """)

    lst_pertandingan = []
    total_pertandingan = len(list_peserta) // 2
    for i in range(total_pertandingan):
        tim1 = list_peserta[i * 2]
        tim2 = list_peserta[i * 2 + 1]
        pertandingan = {
            "tim1": tim1,
            "tim2": tim2,
        }

        if tim1['id_atlet_ganda'] != None:
            atlet_ganda = query(f"""
                SELECT ag.* FROM atlet_ganda as ag WHERE ag.id_atlet_ganda = '{tim1['id_atlet_ganda']}' LIMIT 1
            """)[0]

            member_ganda_1 = query(f"""
                SELECT * FROM member as m WHERE m.id IN
                ('{atlet_ganda['id_atlet_kualifikasi']}', '{atlet_ganda['id_atlet_kualifikasi_2']}')
                LIMIT 2
            """)
            tim1['nama'] = " & ".join(
                map(lambda member: member['nama'], member_ganda_1))
        else:
            member_tunggal_1 = query(f"""
                SELECT * FROM member as member WHERE member.id = '{tim1['id_atlet_kualifikasi']}'
                LIMIT 1
            """)[0]
            tim1['nama'] = member_tunggal_1['nama']

        if tim2['id_atlet_ganda'] != None:
            atlet_ganda_2 = query(f"""
                SELECT ag.* FROM atlet_ganda as ag WHERE ag.id_atlet_ganda = '{tim2['id_atlet_ganda']}' LIMIT 1
            """)[0]

            member_ganda_2 = query(f"""
                SELECT * FROM member as m WHERE m.id IN
                ('{atlet_ganda_2['id_atlet_kualifikasi']}', '{atlet_ganda_2['id_atlet_kualifikasi_2']}')
                LIMIT 2
            """)
            tim2['nama'] = " & ".join(
                map(lambda member: member['nama'], member_ganda_2))
        else:
            member_tunggal_2 = query(f"""
                SELECT * FROM member as member WHERE member.id = '{tim2['id_atlet_kualifikasi']}'
                LIMIT 1
            """)[0]
            tim2['nama'] = member_tunggal_2['nama']

        lst_pertandingan.append(pertandingan)

    total_peserta = query(f"""
    SELECT COUNT(*) AS total_peserta
    FROM partai_peserta_kompetisi AS ppk
    WHERE ppk.jenis_partai = '{partai}' AND ppk.nama_event = '{event}'
    GROUP BY ppk.nama_event, ppk.jenis_partai
    LIMIT 1;""")[0]['total_peserta']

    rounds = {
        32: ("R32", "R32"),
        16: ("R16", "R16"),
        8: ("PEREMPAT FINAL", "R8"),
        4: ("SEMIFINAL", "R4"),
        2: ("FINAL", "R2"),
    }
    jenis_pertandingan, babak = rounds.get(total_peserta, ("", ""))
    konteks = {
        'lst_pertandingan': lst_pertandingan,
        'event': event,
        'tahun': tahun,
        'jenis_pertandingan': jenis_pertandingan,
        'partai': partai,
        'babak': babak,
        'total_peserta': total_peserta
    }
    return render(request, "pertandingan.html", konteks)


@csrf_exempt
def simpan_pertandingan(request):
    if request.method == 'POST':
        request_body = json.loads(request.body)

        tanggal_mulai = request_body['tanggal_mulai']
        waktu_mulai = request_body['waktu_mulai']
        babak = request_body['babak']
        partai = request_body['partai']
        event = request_body['event']
        tahun = request_body['tahun']
        durasi = request_body['durasi']
        data_pertandingan = request_body['data_pertandingan']

        umpire_id = request.session['id']

        with transaction.atomic():
            row_count = query(f"""
                INSERT INTO match (jenis_babak, tanggal, waktu_mulai, nama_event, tahun_event, id_umpire, total_durasi) 
                VALUES 
                ('{babak}', '{tanggal_mulai}', '{waktu_mulai}', 
                '{event}', {tahun}, '{umpire_id}', {durasi}) 
            """)

            if (isinstance(row_count, int) and row_count <= 0) or not isinstance(row_count, int):
                raise Exception("failed insert to match")

            for i in data_pertandingan:
                tim1_no = i['tim1']['nomor_peserta']
                tim2_no = i['tim2']['nomor_peserta']
                tim1_win = i['tim1']['is_win']
                tim2_win = i['tim2']['is_win']

                row_count = query(f"""
                    INSERT INTO peserta_mengikuti_match (jenis_babak, tanggal, waktu_mulai, nomor_peserta, status_menang)
                    VALUES ('{babak}', '{tanggal_mulai}', '{waktu_mulai}', {tim1_no}, {tim1_win})
                """)

                if (isinstance(row_count, int) and row_count <= 0) or not isinstance(row_count, int):
                    raise Exception("error insert tim 1 data")

                row_count = query(f"""
                    INSERT INTO peserta_mengikuti_match (jenis_babak, tanggal, waktu_mulai, nomor_peserta, status_menang)
                    VALUES ('{babak}', '{tanggal_mulai}', '{waktu_mulai}', {tim2_no}, {tim2_win})
                """)

                if (isinstance(row_count, int) and row_count <= 0) or not isinstance(row_count, int):
                    print("error")
                    print(row_count)
                    raise Exception("error insert tim 2 data")
        stlh_babak = {
            'R2': 'R1',
            'R4': 'R2',
            'R8': 'R4',
            'R16': 'R8',
            'R32': 'R16',
        }
        nextBabak = stlh_babak[babak]
        return JsonResponse({
            "next_babak": nextBabak,
        })


def semifinal_page(request):
    return render(request, "semifinal_page.html")


def juara3_page(request):
    return render(request, "juara3_page.html")


def final_page(request):
    return render(request, "final_page.html")


def hasil_pertandingan(request):
    nama_event = unquote(request.GET.get("nama_event"))
    tahun_event = request.GET.get("tahun_event")
    jenis_partai = request.GET.get("jenis_partai")
    # pprint(nama_event)
    # pprint(tahun_event)
    # pprint(jenis_partai)
    with connection.cursor() as cursor:
        cursor.execute(f"""
        SELECT PK.Jenis_partai, E.Nama_event, E.Nama_stadium, E.total_hadiah,
        E.Kategori_Superseries, E.Tgl_mulai, E.Tgl_selesai, S.Kapasitas
        FROM EVENT E
        JOIN PARTAI_KOMPETISI PK ON E.Nama_event = PK.Nama_event AND E.Tahun_Event = PK.Tahun_event
        JOIN STADIUM S ON E.Nama_stadium = S.Nama
        WHERE PK.Jenis_partai = '{jenis_partai}'
        AND PK.Nama_event = '{nama_event}'
        AND PK.Tahun_event = '{tahun_event}';
        """)

        info_pertandingan_raw = cursor.fetchall()
        info_pertandingan = []
        for res in info_pertandingan_raw:
            info_pertandingan.append(
                {
                    "jenis_partai": res[0],
                    "nama_event": res[1],
                    "nama_stadium": res[2],
                    "total_hadiah": res[3],
                    "kategori_superseries": res[4],
                    "tanggal_mulai": res[5],
                    "tanggal_selesai": res[6],
                    "kapasitas": res[7],
                }
            )

        # pprint(info_pertandingan)

        cursor.execute(f"""
        SELECT NAMA FROM MEMBER WHERE ID IN  
        (SELECT AG.ID_ATLET_KUALIFIKASI
        FROM PESERTA_MENGIKUTI_MATCH PMG
        NATURAL JOIN PARTAI_PESERTA_KOMPETISI PPK
        NATURAL JOIN PESERTA_KOMPETISI PK
        JOIN ATLET_GANDA AG
        ON AG.ID_ATLET_GANDA = PK.ID_ATLET_GANDA
        WHERE PMG.JENIS_BABAK = 'FINAL'
        AND PMG.STATUS_MENANG = TRUE
        AND PPK.NAMA_EVENT = '{nama_event}'
        AND PPK.TAHUN_EVENT = '{tahun_event}'
        AND PPK.JENIS_PARTAI = '{jenis_partai}')
        OR ID IN
        (SELECT AG.ID_ATLET_KUALIFIKASI_2
        FROM PESERTA_MENGIKUTI_MATCH PMG
        NATURAL JOIN PARTAI_PESERTA_KOMPETISI PPK
        NATURAL JOIN PESERTA_KOMPETISI PK
        JOIN ATLET_GANDA AG
        ON AG.ID_ATLET_GANDA = PK.ID_ATLET_GANDA
        WHERE PMG.JENIS_BABAK = 'FINAL'
        AND PMG.STATUS_MENANG = TRUE
        AND PPK.NAMA_EVENT = '{nama_event}'
        AND PPK.TAHUN_EVENT = '{tahun_event}'
        AND PPK.JENIS_PARTAI = '{jenis_partai}');
        """)

        juara_satu_ganda_raw = cursor.fetchall()
        juara_satu_ganda = []
        for res in juara_satu_ganda_raw:
            juara_satu_ganda.append(
                {
                    "atlet": res[0]
                }
            )
    # pprint(juara_satu_ganda)

        cursor.execute(f"""
        SELECT NAMA FROM MEMBER WHERE ID IN  
        (SELECT AK.ID_ATLET
        FROM PESERTA_MENGIKUTI_MATCH PMG
        NATURAL JOIN PARTAI_PESERTA_KOMPETISI PPK
        NATURAL JOIN PESERTA_KOMPETISI PK
        JOIN ATLET_KUALIFIKASI AK ON AK.ID_ATLET = PK.ID_ATLET_KUALIFIKASI
        WHERE PMG.JENIS_BABAK = 'FINAL'
        AND PMG.STATUS_MENANG = TRUE
        AND PPK.NAMA_EVENT = '{nama_event}'
        AND PPK.TAHUN_EVENT = '{tahun_event}'
        AND PPK.JENIS_PARTAI = '{jenis_partai}')
        """)

        juara_satu_tunggal_raw = cursor.fetchall()
        juara_satu_tunggal = []
        for res in juara_satu_tunggal_raw:
            juara_satu_tunggal.append(
                {
                    "atlet": res[0]
                }
            )

        cursor.execute(f"""
        SELECT NAMA FROM MEMBER WHERE ID IN  
        (SELECT AG.ID_ATLET_KUALIFIKASI
        FROM PESERTA_MENGIKUTI_MATCH PMG
        NATURAL JOIN PARTAI_PESERTA_KOMPETISI PPK
        NATURAL JOIN PESERTA_KOMPETISI PK
        JOIN ATLET_GANDA AG
        ON AG.ID_ATLET_GANDA = PK.ID_ATLET_GANDA
        WHERE PMG.JENIS_BABAK = 'FINAL'
        AND PMG.STATUS_MENANG = FALSE
        AND PPK.NAMA_EVENT = '{nama_event}'
        AND PPK.TAHUN_EVENT = '{tahun_event}'
        AND PPK.JENIS_PARTAI = '{jenis_partai}')
        OR ID IN
        (SELECT AG.ID_ATLET_KUALIFIKASI_2
        FROM PESERTA_MENGIKUTI_MATCH PMG
        NATURAL JOIN PARTAI_PESERTA_KOMPETISI PPK
        NATURAL JOIN PESERTA_KOMPETISI PK
        JOIN ATLET_GANDA AG
        ON AG.ID_ATLET_GANDA = PK.ID_ATLET_GANDA
        WHERE PMG.JENIS_BABAK = 'FINAL'
        AND PMG.STATUS_MENANG = FALSE
        AND PPK.NAMA_EVENT = '{nama_event}'
        AND PPK.TAHUN_EVENT = '{tahun_event}'
        AND PPK.JENIS_PARTAI = '{jenis_partai}');
        """)

        juara_dua_ganda_raw = cursor.fetchall()
        juara_dua_ganda = []
        for res in juara_dua_ganda_raw:
            juara_dua_ganda.append(
                {
                    "atlet": res[0]
                }
            )

        cursor.execute(f"""
        SELECT NAMA FROM MEMBER WHERE ID IN  
        (SELECT AK.ID_ATLET
        FROM PESERTA_MENGIKUTI_MATCH PMG
        NATURAL JOIN PARTAI_PESERTA_KOMPETISI PPK
        NATURAL JOIN PESERTA_KOMPETISI PK
        JOIN ATLET_KUALIFIKASI AK ON AK.ID_ATLET = PK.ID_ATLET_KUALIFIKASI
        WHERE PMG.JENIS_BABAK = 'FINAL'
        AND PMG.STATUS_MENANG = FALSE
        AND PPK.NAMA_EVENT = '{nama_event}'
        AND PPK.TAHUN_EVENT = '{tahun_event}'
        AND PPK.JENIS_PARTAI = '{jenis_partai}')
        """)

        juara_dua_tunggal_raw = cursor.fetchall()
        juara_dua_tunggal = []
        for res in juara_dua_tunggal_raw:
            juara_dua_tunggal.append(
                {
                    "atlet": res[0]
                }
            )

        cursor.execute(f"""
        SELECT NAMA FROM MEMBER WHERE ID IN  
        (SELECT AG.ID_ATLET_KUALIFIKASI
        FROM PESERTA_MENGIKUTI_MATCH PMG
        NATURAL JOIN PARTAI_PESERTA_KOMPETISI PPK
        NATURAL JOIN PESERTA_KOMPETISI PK
        JOIN ATLET_GANDA AG
        ON AG.ID_ATLET_GANDA = PK.ID_ATLET_GANDA
        WHERE PMG.JENIS_BABAK = 'SF'
        AND PMG.STATUS_MENANG = FALSE
        AND PPK.NAMA_EVENT = '{nama_event}'
        AND PPK.TAHUN_EVENT = '{tahun_event}'
        AND PPK.JENIS_PARTAI = '{jenis_partai}')
        OR ID IN
        (SELECT AG.ID_ATLET_KUALIFIKASI_2
        FROM PESERTA_MENGIKUTI_MATCH PMG
        NATURAL JOIN PARTAI_PESERTA_KOMPETISI PPK
        NATURAL JOIN PESERTA_KOMPETISI PK
        JOIN ATLET_GANDA AG
        ON AG.ID_ATLET_GANDA = PK.ID_ATLET_GANDA
        WHERE PMG.JENIS_BABAK = 'SF'
        AND PMG.STATUS_MENANG = FALSE
        AND PPK.NAMA_EVENT = '{nama_event}'
        AND PPK.TAHUN_EVENT = '{tahun_event}'
        AND PPK.JENIS_PARTAI = '{jenis_partai}');
        """)

        juara_tiga_ganda_raw = cursor.fetchall()
        juara_tiga_ganda = []
        for res in juara_tiga_ganda_raw:
            juara_tiga_ganda.append(
                {
                    "atlet": res[0]
                }
            )

        cursor.execute(f"""
        SELECT NAMA FROM MEMBER WHERE ID IN  
        (SELECT AK.ID_ATLET
        FROM PESERTA_MENGIKUTI_MATCH PMG
        NATURAL JOIN PARTAI_PESERTA_KOMPETISI PPK
        NATURAL JOIN PESERTA_KOMPETISI PK
        JOIN ATLET_KUALIFIKASI AK ON AK.ID_ATLET = PK.ID_ATLET_KUALIFIKASI
        WHERE PMG.JENIS_BABAK = 'SF'
        AND PMG.STATUS_MENANG = FALSE
        AND PPK.NAMA_EVENT = '{nama_event}'
        AND PPK.TAHUN_EVENT = '{tahun_event}'
        AND PPK.JENIS_PARTAI = '{jenis_partai}')
        """)

        juara_tiga_tunggal_raw = cursor.fetchall()
        juara_tiga_tunggal = []
        for res in juara_tiga_tunggal_raw:
            juara_tiga_tunggal.append(
                {
                    "atlet": res[0]
                }
            )

        cursor.execute(f"""
        SELECT NAMA FROM MEMBER WHERE ID IN  
        (SELECT AG.ID_ATLET_KUALIFIKASI
        FROM PESERTA_MENGIKUTI_MATCH PMG
        NATURAL JOIN PARTAI_PESERTA_KOMPETISI PPK
        NATURAL JOIN PESERTA_KOMPETISI PK
        JOIN ATLET_GANDA AG
        ON AG.ID_ATLET_GANDA = PK.ID_ATLET_GANDA
        WHERE PMG.JENIS_BABAK = 'SF'
        AND PMG.STATUS_MENANG = FALSE
        AND PPK.NAMA_EVENT = '{nama_event}'
        AND PPK.TAHUN_EVENT = '{tahun_event}'
        AND PPK.JENIS_PARTAI = '{jenis_partai}')
        OR ID IN
        (SELECT AG.ID_ATLET_KUALIFIKASI_2
        FROM PESERTA_MENGIKUTI_MATCH PMG
        NATURAL JOIN PARTAI_PESERTA_KOMPETISI PPK
        NATURAL JOIN PESERTA_KOMPETISI PK
        JOIN ATLET_GANDA AG
        ON AG.ID_ATLET_GANDA = PK.ID_ATLET_GANDA
        WHERE PMG.JENIS_BABAK = 'SF'
        AND PMG.STATUS_MENANG = FALSE
        AND PPK.NAMA_EVENT = '{nama_event}'
        AND PPK.TAHUN_EVENT = '{tahun_event}'
        AND PPK.JENIS_PARTAI = '{jenis_partai}');
        """)

        semifinal_ganda_raw = cursor.fetchall()
        semifinal_ganda = []
        for res in semifinal_ganda_raw:
            semifinal_ganda.append(
                {
                    "atlet": res[0]
                }
            )

        cursor.execute(f"""
        SELECT NAMA FROM MEMBER WHERE ID IN  
        (SELECT AK.ID_ATLET
        FROM PESERTA_MENGIKUTI_MATCH PMG
        NATURAL JOIN PARTAI_PESERTA_KOMPETISI PPK
        NATURAL JOIN PESERTA_KOMPETISI PK
        JOIN ATLET_KUALIFIKASI AK ON AK.ID_ATLET = PK.ID_ATLET_KUALIFIKASI
        WHERE PMG.JENIS_BABAK = 'SF'
        AND PMG.STATUS_MENANG = FALSE
        AND PPK.NAMA_EVENT = '{nama_event}'
        AND PPK.TAHUN_EVENT = '{tahun_event}'
        AND PPK.JENIS_PARTAI = '{jenis_partai}')
        """)

        semifinal_tunggal_raw = cursor.fetchall()
        semifinal_tunggal = []
        for res in semifinal_tunggal_raw:
            semifinal_tunggal.append(
                {
                    "atlet": res[0]
                }
            )

        cursor.execute(f"""
        SELECT NAMA FROM MEMBER WHERE ID IN  
        (SELECT AG.ID_ATLET_KUALIFIKASI
        FROM PESERTA_MENGIKUTI_MATCH PMG
        NATURAL JOIN PARTAI_PESERTA_KOMPETISI PPK
        NATURAL JOIN PESERTA_KOMPETISI PK
        JOIN ATLET_GANDA AG
        ON AG.ID_ATLET_GANDA = PK.ID_ATLET_GANDA
        WHERE PMG.JENIS_BABAK = 'QF'
        AND PMG.STATUS_MENANG = FALSE
        AND PPK.NAMA_EVENT = '{nama_event}'
        AND PPK.TAHUN_EVENT = '{tahun_event}'
        AND PPK.JENIS_PARTAI = '{jenis_partai}')
        OR ID IN
        (SELECT AG.ID_ATLET_KUALIFIKASI_2
        FROM PESERTA_MENGIKUTI_MATCH PMG
        NATURAL JOIN PARTAI_PESERTA_KOMPETISI PPK
        NATURAL JOIN PESERTA_KOMPETISI PK
        JOIN ATLET_GANDA AG
        ON AG.ID_ATLET_GANDA = PK.ID_ATLET_GANDA
        WHERE PMG.JENIS_BABAK = 'QF'
        AND PMG.STATUS_MENANG = FALSE
        AND PPK.NAMA_EVENT = '{nama_event}'
        AND PPK.TAHUN_EVENT = '{tahun_event}'
        AND PPK.JENIS_PARTAI = '{jenis_partai}');
        """)

        perempat_final_ganda_raw = cursor.fetchall()
        perempat_final_ganda = []
        for res in perempat_final_ganda_raw:
            perempat_final_ganda.append(
                {
                    "atlet": res[0]
                }
            )

        cursor.execute(f"""
        SELECT NAMA FROM MEMBER WHERE ID IN  
        (SELECT AK.ID_ATLET
        FROM PESERTA_MENGIKUTI_MATCH PMG
        NATURAL JOIN PARTAI_PESERTA_KOMPETISI PPK
        NATURAL JOIN PESERTA_KOMPETISI PK
        JOIN ATLET_KUALIFIKASI AK ON AK.ID_ATLET = PK.ID_ATLET_KUALIFIKASI
        WHERE PMG.JENIS_BABAK = 'QF'
        AND PMG.STATUS_MENANG = FALSE
        AND PPK.NAMA_EVENT = '{nama_event}'
        AND PPK.TAHUN_EVENT = '{tahun_event}'
        AND PPK.JENIS_PARTAI = '{jenis_partai}')
        """)

        perempat_final_tunggal_raw = cursor.fetchall()
        perempat_final_tunggal = []
        for res in perempat_final_tunggal_raw:
            perempat_final_tunggal.append(
                {
                    "atlet": res[0]
                }
            )

    context = {
        'info_pertandingan': info_pertandingan,
        'juara_satu_ganda': juara_satu_ganda,
        'juara_satu_tunggal': juara_satu_tunggal,
        'juara_dua_ganda': juara_dua_ganda,
        'juara_dua_tunggal': juara_dua_tunggal,
        'juara_tiga_ganda': juara_tiga_ganda,
        'juara_tiga_tunggal': juara_tiga_tunggal,
        'semifinal_ganda': semifinal_ganda,
        'semifinal_tunggal': semifinal_tunggal,
        'perempat_final_ganda': perempat_final_ganda,
        'perempat_final_tunggal': perempat_final_tunggal,
    }
    return render(request, "hasil_pertandingan.html", context)


def list_event(request):
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT DISTINCT E.Nama_event, E.Tahun_Event, E.Nama_stadium, PK.Jenis_partai,
                E.Kategori_Superseries, E.Tgl_mulai, E.Tgl_selesai, S.Kapasitas, COUNT(PPK.nomor_peserta) as total_peserta
            FROM EVENT E
            JOIN PARTAI_KOMPETISI PK
                ON E.Nama_event = PK.Nama_event
                AND E.Tahun_Event = PK.Tahun_event
            JOIN PARTAI_PESERTA_KOMPETISI PPK
                ON PK.Nama_event = PPK.Nama_event
                AND PK.Tahun_event = PPK.Tahun_event
                AND PK.Jenis_partai = PPK.Jenis_partai
            JOIN STADIUM S
                ON E.Nama_stadium = S.Nama
            GROUP BY E.Nama_event, E.Tahun_Event, E.Nama_stadium, PK.Jenis_partai,
                E.Kategori_Superseries, E.Tgl_mulai, E.Tgl_selesai, S.Kapasitas;
        """)
        partai_kompetisi_event_raw = cursor.fetchall()

        partai_kompetisi_event = []

        for res in partai_kompetisi_event_raw:
            partai_kompetisi_event.append(
                {
                    "nama_event": res[0],
                    "tahun": res[1],
                    "stadium": res[2],
                    "jenis_partai": res[3],
                    "kategori_superseries": res[4],
                    "tanggal_mulai": res[5].strftime("%d %B %Y"),
                    "tanggal_selesai": res[6].strftime("%d %B %Y"),
                    "kapasitas": res[7],
                    "total_peserta": res[8]
                }
            )

        context = {
            "partai_kompetisi_event": partai_kompetisi_event
        }

        return render(request, "list_event.html", context)


def get_daftar_atlet(request):
    with connection.cursor() as cursor:
        cursor.execute(f"""
            SELECT DISTINCT M.nama, A.tgl_lahir, A.negara_asal, A.play_right, A.height, AK.world_rank, AK.world_tour_rank, A.jenis_kelamin, P.total_point
            FROM MEMBER M
            JOIN ATLET A ON M.ID=A.ID
            JOIN ATLET_KUALIFIKASI AK ON A.ID=AK.ID_atlet
            LEFT OUTER JOIN POINT_HISTORY P ON A.ID=P.ID_atlet AND total_point IN (
                    SELECT total_point FROM POINT_HISTORY
                    WHERE AK.ID_atlet=P.ID_atlet
            );
        """)
        atlet_kuali_raw = cursor.fetchall()

        atlet_kuali = []

        for res in atlet_kuali_raw:
            atlet_kuali.append(
                {
                    "nama": res[0],
                    "tgl_lahir": res[1].strftime("%d %B %Y"),
                    "negara_asal": res[2],
                    "play_right": res[3],
                    "height": res[4],
                    "world_rank": res[5],
                    "world_tour_rank": res[6],
                    "jenis_kelamin": res[7],
                    "total_point": res[8],
                }
            )

        # pprint(atlet_kuali_raw)

        cursor.execute(f"""
            SELECT DISTINCT M.nama, A.tgl_lahir, A.negara_asal, A.play_right, A.height, A.jenis_kelamin
            FROM MEMBER M, ATLET A, ATLET_NON_KUALIFIKASI AN
            WHERE M.ID=A.ID AND A.ID=AN.ID_atlet;
        """)
        atlet_nonkuali_raw = cursor.fetchall()

        # pprint(atlet_nonkuali_raw)

        atlet_nonkuali = []
        for res in atlet_nonkuali_raw:
            atlet_nonkuali.append(
                {
                    "nama": res[0],
                    "tgl_lahir": res[1].strftime("%d %B %Y"),
                    "negara_asal": res[2],
                    "play_right": res[3],
                    "height": res[4],
                    "jenis_kelamin": res[5],
                }
            )

        cursor.execute(f"""
            SELECT AG.ID_Atlet_Ganda, MA.Nama AS nama_atlet_1, MB.Nama AS nama_atlet_2, SUM(PHA.total_point + PHB.total_point) AS total_point
            FROM ATLET_GANDA AG
            JOIN MEMBER MA ON AG.ID_Atlet_kualifikasi = MA.ID
            JOIN MEMBER MB ON AG.ID_Atlet_kualifikasi_2 = MB.ID
            LEFT JOIN POINT_HISTORY PHA ON PHA.ID_Atlet = AG.ID_Atlet_kualifikasi
            LEFT JOIN POINT_HISTORY PHB ON PHB.ID_Atlet = AG.ID_Atlet_kualifikasi_2
            GROUP BY AG.ID_Atlet_Ganda, MA.Nama, MB.Nama;
                    """)
        atlet_ganda_raw = cursor.fetchall()

        # pprint(atlet_ganda_raw)

        atlet_ganda = []
        for res in atlet_ganda_raw:
            atlet_ganda.append(
                {
                    "id_atlet_ganda": res[0],
                    "nama_atlet_1": res[1],
                    "nama_atlet_2": res[2],
                    "total_point": res[3],
                }
            )

    context = {
        "atlet_kuali": atlet_kuali,
        "atlet_nonkuali": atlet_nonkuali,
        "atlet_ganda": atlet_ganda
    }

    return render(request, "get_daftar_atlet.html", context)


def buat_ujian_kualifikasi(request):

    # DB Connection
    cur = connection.cursor()

    context = {}

    if request.method == 'POST':
        tahun = request.POST.get('tahun')
        batch = request.POST.get('batch')
        tempat_pelaksanaan = request.POST.get('tempat')
        tanggal_pelaksanaan = request.POST.get('tanggal')

        # Cek
        print(tahun)
        print(batch)
        print(tempat_pelaksanaan)
        print(tanggal_pelaksanaan)

        if tahun == "" or batch == "" or tempat_pelaksanaan == "" or tanggal_pelaksanaan == None:
            context["error_message"] = "Data yang diisikan belum lengkap, silahkan lengkapi data terlebih dahulu."
            return render(request, "buat_ujian_kualifikasi.html", context)

        # SQL Query
        cur.execute(
            """
            INSERT INTO UJIAN_KUALIFIKASI VALUES (%s, %s, %s, CAST(%s AS DATE));
            """,
            [int(tahun), int(batch), tempat_pelaksanaan, tanggal_pelaksanaan]
        )

        print("berhasil nambahin")

    return render(request, "buat_ujian_kualifikasi.html")


def list_ujian_kualifikasi_umpire(request):

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

    context = {}
    context['ujian'] = zip(batch,
                           tahun,
                           tempat,
                           tanggal)

    return render(request, "list_ujian_kualifikasi_umpire.html",  context)


def riwayat_ujian_kualifikasi_umpire(request):

    # DB Connection
    cur = connection.cursor()

    # SQL Query
    cur.execute(
        """ 
            SELECT M.nama, U.tahun, U.batch, U.tempat, U.tanggal, N.hasil_lulus
            FROM member M, atlet A, ujian_kualifikasi U, ATLET_NONKUALIFIKASI_UJIAN_KUALIFIKASI N
            WHERE M.id IN (SELECT A.id FROM ATLET) AND N.id_atlet = M.id AND N.tempat = U.tempat
            AND N.batch = U.batch AND N.tempat = U.tempat AND N.tanggal = U.tanggal; 
        """
    )
    dataUjian = cur.fetchall()

    nama, tahun, batch, tempat, tanggal, hasil = ([] for i in range(6))
    for data in dataUjian:
        nama.append(data[0])
        tahun.append(data[1])
        batch.append(data[2])
        tempat.append(data[3])
        tanggal.append(str(data[4]))
        hasil.append(data[5])

    context = {}
    context['ujian'] = zip(nama,
                           tahun,
                           batch,
                           tempat,
                           tanggal,
                           hasil)

    return render(request, "riwayat_ujian_kualifikasi_umpire.html",  context)
