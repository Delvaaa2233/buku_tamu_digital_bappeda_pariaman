import streamlit as st
import pandas as pd
import datetime
from streamlit_gsheets import GSheetsConnection
from streamlit_drawable_canvas import st_canvas
from streamlit_js_eval import get_geolocation
import plotly.express as px
import math
from fpdf import FPDF
import io

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Buku Tamu Digital - BAPPEDA Kota Pariaman",
    page_icon="🏢",
    layout="wide"
)

# --- KONEKSI DATABASE ---
conn = st.connection("gsheets", type=GSheetsConnection)

def load_data(sheet_name):
    try:
        return conn.read(worksheet=sheet_name, ttl=0)
    except Exception as e:
        st.error(f"Gagal memuat data {sheet_name}: {e}")
        return pd.DataFrame()

def create_pdf(data, is_report=False, title="TANDA TERIMA KUNJUNGAN"):
    pdf = FPDF()
    pdf.add_page()
    
    # Header
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="BAPPEDA KOTA PARIAMAN", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    
    pdf.set_font("Arial", size=10)
    
    if not is_report:
        # PDF untuk Tanda Terima Perorangan
        fields = {
            "ID Registrasi": data.get('id', '-'),
            "Waktu Input": data.get('timestamp', '-'),
            "Nama Lengkap": data.get('nama', '-'),
            "NIP": data.get('nip', '-'),
            "Jabatan": data.get('jabatan', '-'),
            "Instansi/OPD": data.get('opd', '-'),
            "Tujuan Bidang": data.get('bidang_tujuan', '-'),
            "Maksud": data.get('maksud_kunjungan', '-')
        }
        for label, val in fields.items():
            pdf.cell(50, 10, txt=f"{label}:", border=0)
            pdf.cell(140, 10, txt=f"{val}", border=0, ln=True)
    else:
        # PDF untuk Laporan Tabel
        pdf.set_font("Arial", 'B', 10)
        # Header Tabel
        col_width = [30, 50, 40, 70]
        headers = ["Tanggal", "Nama", "OPD", "Maksud"]
        for i, h in enumerate(headers):
            pdf.cell(col_width[i], 10, h, border=1, align='C')
        pdf.ln()
        
        pdf.set_font("Arial", size=9)
        for _, row in data.iterrows():
            pdf.cell(col_width[0], 10, str(row['tanggal']), border=1)
            pdf.cell(col_width[1], 10, str(row['nama'])[:25], border=1)
            pdf.cell(col_width[2], 10, str(row['opd'])[:20], border=1)
            pdf.cell(col_width[3], 10, str(row['maksud_kunjungan'])[:40], border=1)
            pdf.ln()

    pdf.ln(15)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(200, 10, txt=f"Dicetak otomatis pada: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# Load data
df_tamu = load_data("data_tamu")

# Styling
st.markdown("""
    <style>
    .stApp { background-color: #f8fafc; }
    .header-box {
        background: linear-gradient(135deg, #004a99 0%, #0072ff 100%);
        padding: 30px; border-radius: 15px; color: white;
        text-align: center; margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a8/Logo_Kota_Pariaman.png", width=70)
    st.title("Sistem BAPPEDA")
    menu = st.radio("Menu:", ["🏠 Form Buku Tamu", "📊 Visualisasi Data", "📋 Riwayat Kunjungan", "📂 Laporan"])

# Menu Utama
if menu == "🏠 Form Buku Tamu":
    st.markdown('<div class="header-box"><h1>BUKU TAMU DIGITAL</h1><p>BAPPEDA KOTA PARIAMAN</p></div>', unsafe_allow_html=True)
    st.info("💡 Fitur lokasi dinonaktifkan sementara untuk keperluan input data.")

    with st.form("guest_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Lengkap*")
            nip = st.text_input("NIP")
            jabatan = st.text_input("Jabatan*")
            opd = st.text_input("Instansi / OPD*")
        with col2:
            tgl_spt = st.date_input("Tanggal SPT", value=None)
            no_hp = st.text_input("Nomor HP*")
            bidang = st.selectbox("Tujuan Bidang*", ["Sekretariat", "Litbang & Evlap", "Pemerintahan & Sosbud", "Ekonomi", "Sarpras"])
            maksud = st.text_area("Maksud Kunjungan*")
            
        kesan = st.text_area("Kesan & Pesan")
        foto = st.camera_input("Foto Verifikasi")
        
        st.write("✍️ **Tanda Tangan**")
        canvas_result = st_canvas(
            stroke_width=2, stroke_color="#000", background_color="#fff",
            height=150, width=400, drawing_mode="freedraw", key="canvas_sign"
        )

        submitted = st.form_submit_button("SIMPAN DATA")
        
        if submitted:
            if not nama or not no_hp or not opd or not jabatan or not maksud:
                st.error("Mohon lengkapi data bertanda (*)")
            else:
                entry_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                entry_data = {
                    "id": entry_id,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tanggal": str(datetime.date.today()),
                    "tanggal_spt": str(tgl_spt) if tgl_spt else "",
                    "nama": nama, "nip": nip, "jabatan": jabatan, "opd": opd,
                    "nomor_hp": no_hp, "bidang_tujuan": bidang, "maksud_kunjungan": maksud,
                    "kesan_pesan": kesan, "foto_url": "Terlampir", "tanda_tangan_url": "Terlampir",
                    "latitude": "Manual Input", "longitude": "Manual Input"
                }
                
                try:
                    df_new = pd.DataFrame([entry_data])
                    updated_df = pd.concat([df_tamu, df_new], ignore_index=True)
                    conn.update(worksheet="data_tamu", data=updated_df)
                    st.success("✅ Data Tersimpan!")
                    st.balloons()
                    
                    pdf_data = create_pdf(entry_data)
                    st.download_button("📥 Download Tanda Terima (PDF)", pdf_data, f"Tamu_{entry_id}.pdf", "application/pdf")
                except Exception as e:
                    st.error(f"Error GSheets: {e}")

elif menu == "📊 Visualisasi Data":
    st.title("Statistik Pengunjung")
    if not df_tamu.empty:
        st.plotly_chart(px.pie(df_tamu, names='bidang_tujuan', hole=0.3, title="Persentase Kunjungan per Bidang"))
    else: st.info("Data masih kosong")

elif menu == "📋 Riwayat Kunjungan":
    st.title("Riwayat Kunjungan Terbaru")
    if not df_tamu.empty:
        st.dataframe(df_tamu.sort_values(by='timestamp', ascending=False), use_container_width=True)
    else: st.info("Belum ada riwayat")

elif menu == "📂 Laporan":
    st.title("📂 Laporan Kunjungan")
    
    if df_tamu.empty:
        st.info("Data kosong, tidak ada laporan yang bisa dihasilkan.")
    else:
        # Konversi kolom tanggal ke datetime untuk filter
        df_tamu['tanggal_dt'] = pd.to_datetime(df_tamu['tanggal'])
        
        tab1, tab2, tab3 = st.tabs(["Harian", "Bulanan", "Tahunan"])
        
        with tab1:
            date_filter = st.date_input("Pilih Tanggal Laporan", value=datetime.date.today())
            filtered_df = df_tamu[df_tamu['tanggal_dt'].dt.date == date_filter]
            st.write(f"Data Tanggal: {date_filter}")
            st.dataframe(filtered_df, use_container_width=True)
            if not filtered_df.empty:
                pdf_rep = create_pdf(filtered_df, is_report=True, title=f"LAPORAN HARIAN - {date_filter}")
                st.download_button("📥 Export Laporan Harian (PDF)", pdf_rep, f"Laporan_Harian_{date_filter}.pdf", "application/pdf")

        with tab2:
            col_m, col_y = st.columns(2)
            with col_m: month_filter = st.selectbox("Bulan", range(1, 13), index=datetime.date.today().month - 1)
            with col_y: year_filter = st.selectbox("Tahun ", range(2024, 2030), index=1)
            
            filtered_df_m = df_tamu[(df_tamu['tanggal_dt'].dt.month == month_filter) & (df_tamu['tanggal_dt'].dt.year == year_filter)]
            st.dataframe(filtered_df_m, use_container_width=True)
            if not filtered_df_m.empty:
                pdf_rep_m = create_pdf(filtered_df_m, is_report=True, title=f"LAPORAN BULANAN - {month_filter}/{year_filter}")
                st.download_button("📥 Export Laporan Bulanan (PDF)", pdf_rep_m, f"Laporan_Bulanan_{month_filter}_{year_filter}.pdf", "application/pdf")

        with tab3:
            year_only = st.selectbox("Pilih Tahun Laporan", range(2024, 2030), index=1)
            filtered_df_y = df_tamu[df_tamu['tanggal_dt'].dt.year == year_only]
            st.dataframe(filtered_df_y, use_container_width=True)
            if not filtered_df_y.empty:
                pdf_rep_y = create_pdf(filtered_df_y, is_report=True, title=f"LAPORAN TAHUNAN - {year_only}")
                st.download_button("📥 Export Laporan Tahunan (PDF)", pdf_rep_y, f"Laporan_Tahunan_{year_only}.pdf", "application/pdf")
