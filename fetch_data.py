from flask import Flask, render_template, jsonify  # type: ignore
import mysql.connector

app = Flask(__name__)


def connect_to_db():
    """Membuat koneksi ke database MySQL."""
    try:
        conn = mysql.connector.connect(
            host="localhost",  # Ganti dengan host Anda
            user="root",  # Ganti dengan username Anda
            password="password",  # Ganti dengan password Anda
            database="db_iot_bb",  # Ganti dengan nama database Anda
        )
        return conn
    except mysql.connector.Error as e:
        print(f"Error saat menghubungkan ke database: {e}")
        return None


def fetch_data(conn, query):
    """Mengambil data dari database berdasarkan query yang diberikan."""
    try:
        cursor = conn.cursor()
        cursor.execute(query)
        rows = cursor.fetchall()  # Menarik semua hasil query
        return rows
    except mysql.connector.Error as e:
        print(f"Error saat mengambil data: {e}")
        return []


@app.route("/")
def index():
    query = "SELECT * FROM tb_cuaca;"  # Ganti dengan query yang sesuai dengan kebutuhan Anda

    # Terhubung ke database
    conn = connect_to_db()

    if conn:
        # Menarik data
        data = fetch_data(conn, query)

        if data:
            # Menghitung suhu tertinggi, terendah, dan rata-rata
            suhu_data = [row[2] for row in data]  # Kolom suhu (misalnya kolom ke-3)
            kelembapan_data = [
                row[3] for row in data
            ]  # Kolom kelembapan (misalnya kolom ke-4)
            waktu_data = [row[1] for row in data]  # Kolom waktu (misalnya kolom ke-2)

            suhu_tertinggi = max(suhu_data)
            suhu_terendah = min(suhu_data)
            rata_rata_suhu = sum(suhu_data) / len(suhu_data) if suhu_data else 0

            # Mengirim data ke template HTML
            return render_template(
                "index.html",
                data=data,
                suhu_data=suhu_data,
                kelembapan_data=kelembapan_data,
                waktu_data=waktu_data,
                suhu_tertinggi=suhu_tertinggi,
                suhu_terendah=suhu_terendah,
                rata_rata_suhu=rata_rata_suhu,
            )
        else:
            return "Tidak ada data yang ditemukan."

        # Menutup koneksi ke database
        conn.close()
    else:
        return "Gagal terhubung ke database."


# Endpoint untuk menampilkan data dalam format JSON
@app.route("/api/cuaca")
def cuaca_json():
    query = "SELECT * FROM tb_cuaca;"  # Ganti dengan query yang sesuai dengan kebutuhan Anda

    # Terhubung ke database
    conn = connect_to_db()

    if conn:
        # Menarik data
        data = fetch_data(conn, query)

        if data:
            # Menyiapkan data dalam format dictionary agar mudah dikonversi ke JSON
            result = [
                {"waktu": row[1], "suhu": row[2], "kelembapan": row[3]} for row in data
            ]

            # Menutup koneksi ke database
            conn.close()

            # Mengirim data sebagai JSON
            return jsonify(result)
        else:
            return jsonify({"message": "Tidak ada data yang ditemukan."}), 404

    else:
        return jsonify({"message": "Gagal terhubung ke database."}), 500


if __name__ == "__main__":
    app.run(debug=True)
