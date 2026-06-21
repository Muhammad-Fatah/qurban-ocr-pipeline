import os
import cv2
import pytesseract
import re
import duckdb
from ultralytics import YOLO

# Konfigurasi awal
pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'
model = YOLO("dataset-yolo/runs/detect/train/weights/best.pt")

# Tentukan folder tempat foto-foto mentah berada
folder_path = "dataset-yolo/test/images/"

# Ambil semua daftar nama file berakhiran .jpg di folder tersebut
image_files = [f for f in os.listdir(folder_path) if f.endswith('.jpg')]

# Buka koneksi DuckDB SATU KALI saja di awal
conn = duckdb.connect('qurban_silver.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS silver_transaksi (
        id_transaksi VARCHAR,
        nama_file VARCHAR,
        waktu_ekstrak TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

print(f"🚀 Memulai proses batch untuk {len(image_files)} foto...\n")

# Lakukan perulangan untuk setiap foto
for img_file in image_files:
    image_path = os.path.join(folder_path, img_file)
    print(f"Menganalisis: {img_file} ...", end=" ")
    
    # Deteksi YOLO (verbose=False agar terminal tidak kepenuhan teks loading)
    results = model.predict(source=image_path, verbose=False)
    img = cv2.imread(image_path)
    
    banner_found = False
    for result in results:
        boxes = result.boxes
        for box in boxes:
            banner_found = True
            
            # Potong (Crop)
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            cropped_img = img[y1:y2, x1:x2]
            
            # Filter gambar (Binarization)
            img_resized = cv2.resize(cropped_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
            gray_img = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
            _, thresh_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Ekstrak OCR
            custom_config = r'-l ind --psm 6'
            extracted_text = pytesseract.image_to_string(thresh_img, config=custom_config)
            
            # Filter Regex untuk Silver Layer
            id_pola = re.search(r'\d{5}', extracted_text)
            if id_pola:
                id_transaksi = id_pola.group(0)
                # Simpan ID beserta nama fotonya agar mudah dilacak
                conn.execute("INSERT INTO silver_transaksi (id_transaksi, nama_file) VALUES (?, ?)", (id_transaksi, img_file))
                print(f"✅ Sukses (ID: {id_transaksi})")
            else:
                print("❌ Gagal (Teks tidak jelas)")
            
            break # Cukup ambil 1 banner per foto
            
    if not banner_found:
        print("⚠️ Dilewati (Banner tidak ditemukan oleh YOLO)")

print("\n=== SEMUA FOTO SELESAI DIPROSES ===")
# Hitung total data yang berhasil diselamatkan ke Silver Layer
total_data = conn.execute("SELECT COUNT(*) FROM silver_transaksi").fetchone()[0]
print(f"Total data di Database Silver saat ini: {total_data} baris.")

conn.close()
