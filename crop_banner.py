import cv2
import pytesseract
import re # Tambahkan library Regex
from ultralytics import YOLO

pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

model = YOLO("dataset-yolo/runs/detect/train/weights/best.pt")
image_path = "dataset-yolo/test/images/99383_jpg.rf.20c003c3bffc046177b460175e197755.jpg" 

results = model.predict(source=image_path)
img = cv2.imread(image_path)

for result in results:
    boxes = result.boxes
    for box in boxes:
        x1, y1, x2, y2 = box.xyxy[0]
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        cropped_img = img[y1:y2, x1:x2]
        
        # Pra-pemrosesan OCR
        img_resized = cv2.resize(cropped_img, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
        gray_img = cv2.cvtColor(img_resized, cv2.COLOR_BGR2GRAY)
        _, thresh_img = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        custom_config = r'-l ind --psm 6'
        extracted_text = pytesseract.image_to_string(thresh_img, config=custom_config)
        
        print("\n=== LAPISAN BRONZE (TEKS MENTAH) ===")
        print(extracted_text.strip())
        print("====================================\n")
        
        # --- LAPISAN SILVER (PEMBERSIHAN DATA DENGAN REGEX) ---
        print("Memproses data ke Silver Layer...")
        
        # Mencari ID Transaksi (Pola: 5 digit angka berturut-turut)
        id_pola = re.search(r'\d{5}', extracted_text)
        
        if id_pola:
            id_transaksi = id_pola.group(0)
            print(f"✅ Sukses Ekstrak ID Transaksi : {id_transaksi}")
            # Nantinya, variabel id_transaksi ini yang akan kita simpan ke DuckDB!
        else:
            print("❌ Gagal menemukan ID Transaksi.")
            
        break
