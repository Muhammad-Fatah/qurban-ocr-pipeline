import duckdb

conn = duckdb.connect('qurban_silver.db')

print("=== 1. MENYIAPKAN DATA MASTER ===")
conn.execute('''
    CREATE OR REPLACE TABLE master_donatur (
        id_transaksi VARCHAR,
        nama_donatur VARCHAR,
        jenis_hewan VARCHAR,
        lokasi VARCHAR
    )
''')
conn.execute("INSERT INTO master_donatur VALUES ('99393', 'Ratih Ayu Wulandari', 'Sapi', 'Uganda')")
conn.execute("INSERT INTO master_donatur VALUES ('12345', 'Budi Santoso', 'Kambing', 'Yogyakarta')")
print("Data Master siap.\n")

print("=== 2. MEMPROSES GOLD LAYER (DATA ENRICHMENT) ===")
conn.execute('''
    CREATE OR REPLACE TABLE gold_laporan_qurban AS
    SELECT 
        s.id_transaksi,
        m.nama_donatur,
        m.jenis_hewan,
        m.lokasi,
        s.waktu_ekstrak AS waktu_validasi_foto
    FROM silver_transaksi s
    JOIN master_donatur m ON s.id_transaksi = m.id_transaksi
''')
print("✅ Tabel Gold Layer berhasil dibuat!\n")

print("=== 3. HASIL AKHIR GOLD LAYER ===")
hasil_gold = conn.execute("SELECT * FROM gold_laporan_qurban").fetchall()

print(f"{'ID':<8} | {'NAMA DONATUR':<20} | {'HEWAN':<8} | {'LOKASI':<12} | {'WAKTU VALIDASI'}")
print("-" * 80)
for baris in hasil_gold:
    print(f"{baris[0]:<8} | {baris[1]:<20} | {baris[2]:<8} | {baris[3]:<12} | {baris[4]}")
print("=================================\n")

conn.close()
