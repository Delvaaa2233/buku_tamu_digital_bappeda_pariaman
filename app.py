import streamlit as st
import pandas as pd
import datetime
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from streamlit_drawable_canvas import st_canvas
import plotly.express as px
from fpdf import FPDF
import io

# --- KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="Buku Tamu Digital - BAPPEDA Kota Pariaman",
    page_icon="🏢",
    layout="wide"
)

# --- KONFIGURASI GOOGLE SHEETS ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1c3DA7X56NbbeZyOFnfBFG8ZdxX-JZd9Ml372xvAA80o/edit#gid=0"

# --- KONEKSI DATABASE ---
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

# Lokal: credential.json ada di folder project
creds = ServiceAccountCredentials.from_json_keyfile_name("credential.json", scope)

# Kalau di Streamlit Cloud, pakai Secrets Manager:
# import json
# creds_dict = json.loads(st.secrets["gcp_service_account"])
# creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)

client = gspread.authorize(creds)

def load_data(sheet_name):
    try:
        sheet = client.open_by_url(SHEET_URL).worksheet(sheet_name)
        data = sheet.get_all_records()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Gagal memuat data {sheet_name}: {e}")
        return pd.DataFrame()

def update_data(sheet_name, df):
    try:
        sheet = client.open_by_url(SHEET_URL).worksheet(sheet_name)
        sheet.clear()
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
    except Exception as e:
        st.error(f"Gagal update data {sheet_name}: {e}")

def create_pdf(data, is_report=False, title="TANDA TERIMA KUNJUNGAN"):
    pdf = FPDF()
    pdf.add_page()
    
    # Header Instansi
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="BAPPEDA KOTA PARIAMAN", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=title, ln=True, align='C')
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    
    pdf.set_font("Arial", size=11)
    
    if not is_report:
        fields = {
            "ID Registrasi": data.get('id', '-'),
            "Waktu": data.get('timestamp', '-'),
            "Nama": data.get('nama', '-'),
            "Instansi/OPD": data.get('opd', '-'),
            "Tujuan": data.get('bidang_tujuan', '-'),
            "Maksud": data.get('maksud_kunjungan', '-')
        }
        for label, val in fields.items():
            pdf.cell(50, 10, txt=f"{label}:", border=0)
            pdf.cell(140, 10, txt=f"{val}", border=0, ln=True)
    else:
        pdf.set_font("Arial", 'B', 9)
        col_widths = [25, 45, 40, 80]
        headers = ["Tanggal", "Nama", "Instansi", "Maksud"]
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 10, h, border=1, align='C')
        pdf.ln()
        
        pdf.set_font("Arial", size=8)
        for _, row in data.iterrows():
            pdf.cell(col_widths[0], 10, str(row['tanggal']), border=1)
            pdf.cell(col_widths[1], 10, str(row['nama'])[:25], border=1)
            pdf.cell(col_widths[2], 10, str(row['opd'])[:20], border=1)
            pdf.cell(col_widths[3], 10, str(row['maksud_kunjungan'])[:45], border=1)
            pdf.ln()

    pdf.ln(15)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(200, 10, txt=f"Dicetak pada: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=True, align='C')
    return pdf.output(dest='S').encode('latin-1')

# Load data awal
df_tamu = load_data("data_tamu")

# Sidebar Menu
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a8/Logo_Kota_Pariaman.png", width=70)
    st.title("Sistem BAPPEDA")
    menu = st.radio("Navigasi:", ["🏠 Form Buku Tamu", "📊 Statistik", "📋 Riwayat", "📂 Laporan"])

# --- MENU UTAMA ---
if menu == "🏠 Form Buku Tamu":
    st.markdown("""
        <div style='background: linear-gradient(135deg, #004a99 0%, #0072ff 100%); padding: 25px; border-radius: 15px; color: white; text-align: center; margin-bottom: 20px;'>
            <h1 style='margin:0;'>BUKU TAMU DIGITAL</h1>
            <p style='margin:0;'>BAPPEDA KOTA PARIAMAN</p>
        </div>
    """, unsafe_allow_html=True)

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
        foto = st.camera_input("Ambil Foto Verifikasi")
        
        st.write("✍️ **Tanda Tangan**")
        canvas_result = st_canvas(
            stroke_width=2, stroke_color="#000", background_color="#fff",
            height=150, width=400, drawing_mode="freedraw", key="canvas_sign"
        )

        submitted = st.form_submit_button("SIMPAN KUNJUNGAN")
        
        if submitted:
            if not nama or not no_hp or not opd or not jabatan or not maksud:
                st.error("Mohon lengkapi kolom yang wajib diisi (*)")
            else:
                entry_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                entry_data = {
                    "id": entry_id,
                    "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tanggal": str(datetime.date.today()),
                    "tanggal_spt": str(tgl_spt) if tgl_spt else "",
                    "nama": nama,
                    "nip": nip,
                    "jabatan": jabatan,
                    "opd": opd,
                    "nomor_hp": no_hp,
                    "bidang_tujuan": bidang,
                    "maksud_kunjungan": maksud,
                    "kesan_pesan": kesan,
                    "foto_url": "Terlampir",
                    "tanda_tangan_url": "Terlampir",
                    "latitude": "Offline",
                    "longitude": "Offline"
                }
                
                try:
                    df_new = pd.DataFrame([entry_data])
                    if not df_tamu.empty:
                        updated_df = pd.concat([df_tamu, df_new], ignore_index=True)
                    else:
                        updated_df = df_new
                        
                    update_data("data_tamu", updated_df)
                    
                    st.success("✅ Data berhasil disimpan!")
                    st.balloons()
                    
                    pdf_bytes = create_pdf(entry_data)
                    st.download_button("📥 Unduh Tanda Terima (PDF)", pdf_bytes, f"Tanda_Terima_{entry_id}.pdf", "application/pdf")
                except Exception as e:
                    st.error(f"Gagal menyimpan ke Google Sheets: {e}")

elif menu == "📊 Statistik":
    st.title("Statistik Pengunjung")
    if not df_tamu.empty:
        fig = px.pie(df_tamu, names='bidang_tujuan', hole=0.4, title="Distribusi Tujuan Kunjungan")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Data statistik belum tersedia.")

elif menu == "📋 Riwayat":
    st.title("Daftar Kunjungan")
    if not df_tamu.empty:
        st.dataframe(df_t
