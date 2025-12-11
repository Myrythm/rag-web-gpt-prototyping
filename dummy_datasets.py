from fpdf import FPDF
import os

# Data untuk 12 Laporan (Sesuai output sebelumnya)
dataset = [
    # --- ANGGA ---
    {
        "filename": "reimburse-Angga-Agustus-2025.pdf",
        "name": "Angga",
        "month": "Agustus",
        "data": [
            ["2025-08-04", "Tiket KRL perjalanan dinas", "Transportasi", 12000],
            ["2025-08-08", "Makan siang dengan tim proyek", "Makan Siang", 65000],
            ["2025-08-15", "Beli map dan kertas A4", "Peralatan Kantor", 24500],
            ["2025-08-16", "Grab ke lokasi meeting klien", "Transportasi", 42000],
            ["2025-08-20", "Biaya fotocopy dokumen", "Lain-lain", 10000],
            ["2025-08-26", "Makan siang sendirian", "Makan Siang", 38500],
            ["2025-08-28", "Parkir di gedung kantor klien", "Transportasi", 15000],
        ]
    },
    {
        "filename": "reimburse-Angga-September-2025.pdf",
        "name": "Angga",
        "month": "September",
        "data": [
            ["2025-09-03", "Biaya download software sementara", "Lain-lain", 50000],
            ["2025-09-09", "Makan siang tim (4 orang)", "Makan Siang", 145000],
            ["2025-09-12", "Tiket Transjakarta ke cabang", "Transportasi", 7000],
            ["2025-09-19", "Beli notes dan pulpen", "Peralatan Kantor", 18000],
            ["2025-09-24", "Grab express kirim dokumen", "Transportasi", 30000],
            ["2025-09-30", "Makan malam lembur", "Makan Siang", 45000],
        ]
    },
    {
        "filename": "reimburse-Angga-Oktober-2025.pdf",
        "name": "Angga",
        "month": "Oktober",
        "data": [
            ["2025-10-01", "Makan siang meeting di luar", "Makan Siang", 62500],
            ["2025-10-07", "Beli mouse dan keyboard cadangan", "Peralatan Kantor", 105000],
            ["2025-10-15", "Transportasi taksi bandara", "Transportasi", 120000],
            ["2025-10-15", "Penginapan (1 malam) di Bandung", "Akomodasi", 550000],
            ["2025-10-16", "Makan siang dinas di Bandung", "Makan Siang", 55000],
            ["2025-10-16", "Transportasi lokal di Bandung", "Transportasi", 50000],
            ["2025-10-24", "Bensin untuk kunjungan lapangan", "Transportasi", 70000],
            ["2025-10-29", "Biaya domain untuk prototype", "Lain-lain", 97500],
        ]
    },
    {
        "filename": "reimburse-Angga-November-2025.pdf",
        "name": "Angga",
        "month": "November",
        "data": [
            ["2025-11-05", "Grab Bike ke kantor pusat", "Transportasi", 17500],
            ["2025-11-10", "Makan siang dengan vendor", "Makan Siang", 85000],
            ["2025-11-14", "Beli webcam untuk meeting online", "Peralatan Kantor", 120000],
            ["2025-11-20", "Tiket bus ke kantor klien", "Transportasi", 35000],
            ["2025-11-25", "Biaya tambah daya hp darurat", "Lain-lain", 10000],
        ]
    },
    # --- ANDIKA ---
    {
        "filename": "reimburse-Andika-Agustus-2025.pdf",
        "name": "Andika",
        "month": "Agustus",
        "data": [
            ["2025-08-01", "Tiket kereta menuju Surabaya", "Transportasi", 250000],
            ["2025-08-01", "Penginapan (2 malam) Surabaya", "Akomodasi", 700000],
            ["2025-08-02", "Makan siang internal tim", "Makan Siang", 90000],
            ["2025-08-03", "Taksi dari hotel ke stasiun", "Transportasi", 35000],
            ["2025-08-10", "Beli stabilo dan spidol", "Peralatan Kantor", 15000],
            ["2025-08-18", "Biaya jasa kurir dokumen", "Lain-lain", 40000],
            ["2025-08-25", "Makan siang lembur di kantor", "Makan Siang", 45000],
            ["2025-08-29", "Grab ke rumah (pulang malam)", "Transportasi", 55000],
        ]
    },
    {
        "filename": "reimburse-Andika-September-2025.pdf",
        "name": "Andika",
        "month": "September",
        "data": [
            ["2025-09-02", "Beli charger laptop pengganti", "Peralatan Kantor", 150000],
            ["2025-09-10", "Makan siang meeting partner", "Makan Siang", 120000],
            ["2025-09-17", "Tiket bus Pulo Gebang - Blok M", "Transportasi", 15000],
            ["2025-09-22", "Biaya scan dan cetak dokumen A3", "Lain-lain", 20000],
            ["2025-09-26", "Toll perjalanan dinas ke Bogor", "Transportasi", 32500],
            ["2025-09-27", "Makan malam dinas", "Makan Siang", 62500],
        ]
    },
    {
        "filename": "reimburse-Andika-Oktober-2025.pdf",
        "name": "Andika",
        "month": "Oktober",
        "data": [
            ["2025-10-04", "Grab Bike antar dokumen", "Transportasi", 20000],
            ["2025-10-09", "Makan siang tim (6 orang)", "Makan Siang", 185000],
            ["2025-10-14", "Beli headset low-end sementara", "Peralatan Kantor", 75000],
            ["2025-10-21", "Transportasi bus ke lokasi event", "Transportasi", 25000],
            ["2025-10-28", "Makan malam sendirian (lembur)", "Makan Siang", 40000],
        ]
    },
    {
        "filename": "reimburse-Andika-November-2025.pdf",
        "name": "Andika",
        "month": "November",
        "data": [
            ["2025-11-01", "Tiket pesawat Jakarta - Medan", "Transportasi", 750000],
            ["2025-11-01", "Hotel (2 malam) di Medan", "Akomodasi", 900000],
            ["2025-11-02", "Biaya laundry selama dinas", "Lain-lain", 50000],
            ["2025-11-03", "Taksi dari hotel ke bandara", "Transportasi", 65000],
            ["2025-11-13", "Makan siang di kantor", "Makan Siang", 40000],
        ]
    },
    # --- ANCIKA ---
    {
        "filename": "reimburse-Ancika-Agustus-2025.pdf",
        "name": "Ancika",
        "month": "Agustus",
        "data": [
            ["2025-08-06", "Grab ke kantor cabang briefing", "Transportasi", 30000],
            ["2025-08-12", "Makan siang dengan agency", "Makan Siang", 75000],
            ["2025-08-19", "Beli binder dan sticky notes", "Peralatan Kantor", 22500],
            ["2025-08-21", "Tiket KRL menuju kantor klien", "Transportasi", 9000],
            ["2025-08-23", "Biaya top up pulsa emergency", "Lain-lain", 25000],
            ["2025-08-27", "Makan malam tim marketing", "Makan Siang", 98500],
        ]
    },
    {
        "filename": "reimburse-Ancika-September-2025.pdf",
        "name": "Ancika",
        "month": "September",
        "data": [
            ["2025-09-05", "Taksi online ke venue event", "Transportasi", 45000],
            ["2025-09-11", "Makan siang pribadi hari kerja", "Makan Siang", 35000],
            ["2025-09-18", "Beli tinta printer untuk kantor", "Peralatan Kantor", 85000],
            ["2025-09-20", "Biaya registrasi webinar", "Lain-lain", 150000],
            ["2025-09-25", "Parkir di gedung perkantoran", "Transportasi", 15000],
        ]
    },
    {
        "filename": "reimburse-Ancika-Oktober-2025.pdf",
        "name": "Ancika",
        "month": "Oktober",
        "data": [
            ["2025-10-02", "Makan siang meeting klien baru", "Makan Siang", 110000],
            ["2025-10-08", "Tiket travel ke Semarang", "Transportasi", 180000],
            ["2025-10-08", "Penginapan (1 malam) Semarang", "Akomodasi", 450000],
            ["2025-10-09", "Transportasi lokal taxi Semarang", "Transportasi", 75000],
            ["2025-10-15", "Beli folder arsip", "Peralatan Kantor", 15000],
            ["2025-10-22", "Biaya fotocopy dan jilid", "Lain-lain", 15000],
            ["2025-10-29", "Makan siang (3 org) brainstorming", "Makan Siang", 95000],
        ]
    },
    {
        "filename": "reimburse-Ancika-November-2025.pdf",
        "name": "Ancika",
        "month": "November",
        "data": [
            ["2025-11-04", "Grab ke stasiun", "Transportasi", 25000],
            ["2025-11-07", "Makan siang urgent saat training", "Makan Siang", 40000],
            ["2025-11-12", "Beli flashdisk backup data", "Peralatan Kantor", 55000],
            ["2025-11-19", "Biaya download asset desain", "Lain-lain", 50000],
            ["2025-11-26", "Tiket TJ pulang-pergi event", "Transportasi", 14000],
        ]
    },
]

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 14)
        # Title placeholder, will be set per document
    
    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, 'Halaman ' + str(self.page_no()), 0, 0, 'C')

def create_rupiah_format(amount):
    return "Rp " + "{:,.0f}".format(amount).replace(",", ".")

def generate_pdf(item):
    pdf = PDF()
    pdf.add_page()
    
    # Title
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, f"Laporan Reimburse {item['name']} - {item['month']} 2025", ln=True, align='C')
    pdf.ln(10)
    
    # Table Header
    pdf.set_font('Arial', 'B', 10)
    pdf.set_fill_color(200, 220, 255)
    pdf.cell(30, 10, 'Tanggal', 1, 0, 'C', True)
    pdf.cell(80, 10, 'Deskripsi', 1, 0, 'C', True)
    pdf.cell(40, 10, 'Kategori', 1, 0, 'C', True)
    pdf.cell(40, 10, 'Jumlah (Rp)', 1, 1, 'C', True)
    
    # Table Content
    pdf.set_font('Arial', '', 10)
    total = 0
    for row in item['data']:
        date, desc, cat, amount = row
        total += amount
        
        pdf.cell(30, 10, date, 1, 0, 'C')
        pdf.cell(80, 10, desc, 1, 0, 'L')
        pdf.cell(40, 10, cat, 1, 0, 'C')
        pdf.cell(40, 10, create_rupiah_format(amount), 1, 1, 'R')
        
    # Grand Total
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(150, 10, 'Grand Total', 1, 0, 'R')
    pdf.cell(40, 10, create_rupiah_format(total), 1, 1, 'R')
    
    # Save file
    pdf.output(item['filename'])
    print(f"Generated: {item['filename']}")

# Main Execution
if __name__ == "__main__":
    print("Generating 12 PDF files...")
    for item in dataset:
        generate_pdf(item)
    print("Done! Semua file telah dibuat.")