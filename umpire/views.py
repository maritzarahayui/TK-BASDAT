from django.shortcuts import render
from django.db import connection
from pprint import pprint

# import psycopg2


# def connectDb():
#     return psycopg2.connect(
#         user='postgres',
#         password='VqhDHXgGPL8avdUHqCWP',
#         host='containers-us-west-72.railway.app',
#         databases='railway',
#         port='7729',
#     )


def register_umpire(request):
    return render(request, "register_umpire.html")


def dashboard_umpire(request):
    return render(request, "dashboard_umpire.html")


def pertandingan_page(request):
    return render(request, "pertandingan.html")


def semifinal_page(request):
    return render(request, "semifinal_page.html")


def juara3_page(request):
    return render(request, "juara3_page.html")


def final_page(request):
    return render(request, "final_page.html")


def hasil_pertandingan(request):
    return render(request, "hasil_pertandingan.html")


def list_event(request):
    return render(request, "list_event.html")


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
