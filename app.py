import streamlit as st
import pandas as pd
import datetime
from streamlit_gsheets import GSheetsConnection
from streamlit_drawable_canvas import st_canvas
from streamlit_js_eval import get_geolocation
import plotly.express as px
import time
import math
from fpdf import FPDF

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
        return conn.read(worksheet=sheet_name, ttl="0")
    except Exception:
        return pd.DataFrame()

def haversine(lat1, lon1, lat2, lon2):
    R = 6371000 
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

def create_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="BAPPEDA KOTA PARIAMAN", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="TANDA TERIMA KUNJUNGAN DIGITAL", ln=True, align='C')
    pdf.line(10, 30, 200, 30)
    pdf.ln(10)
    
    pdf.set_font("Arial", size=11)
    fields = {
        "ID Registrasi": data.get('id', '-'),
        "Waktu": data.get('timestamp', '-'),
        "Nama Lengkap": data.get('nama', '-'),
        "NIP": data.get('nip', '-'),
        "Jabatan": data.get('jabatan', '-'),
        "Instansi/OPD": data.get('opd', '-'),
        "Bidang Tujuan": data.get('bidang_tujuan', '-'),
        "Maksud Kunjungan": data.get('maksud_kunjungan', '-')
    }
    
    for label, val in fields.items():
        pdf.cell(50, 10, txt=f"{label}:", border=0)
        pdf.cell(140, 10, txt=f"{val}", border=0, ln=True)
    
    pdf.ln(15)
    pdf.set_font("Arial", 'I', 8)
    pdf.cell(200, 10, txt=f"Dokumen ini sah secara digital. Dicetak pada: {datetime.datetime.now()}", ln=True, align='C')
    
    return pdf.output(dest='S').encode('latin-1')

df_tamu = load_data("data_tamu")
df_config = load_data("config")

if not df_config.empty:
    config_dict = dict(zip(df_config['key'], df_config['value']))
    target_lat = float(config_dict.get('lat_bappeda', -0.626))
    target_lon = float(config_dict.get('lon_bappeda', 100.117))
    allowed_radius = float(config_dict.get('radius_meter', 300))
else:
    target_lat, target_lon, allowed_radius = -0.626, 100.117, 300

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

with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/a/a8/Logo_Kota_Pariaman.png", width=70)
    st.title("BAPPEDA")
    menu = st.radio("Pilih Menu:", ["🏠 Beranda", "📊 Statistik", "📋 Daftar Tamu"])

loc = get_geolocation()

if menu == "🏠 Beranda":
    st.markdown('<div class="header-box"><h1>BUKU TAMU DIGITAL</h1><p>BAPPEDA KOTA PARIAMAN</p></div>', unsafe_allow_html=True)
    
    is_in_range = False
    current_lat, current_lon = None, None
    
    if loc:
        current_lat = loc['coords']['latitude']
        current_lon = loc['coords']['longitude']
        distance = haversine(current_lat, current_lon, target_lat, target_lon)
        
        if distance <= allowed_radius:
            st.success(f"📍 Lokasi Terverifikasi ({int(distance)}m dari kantor)")
            is_in_range = True
        else:
            st.error(f"⚠️ Anda berada di luar area kantor ({int(distance)}m).")
    else:
        st.warning("📍 Mencari lokasi GPS... Pastikan izin lokasi aktif.")

    with st.form("guest_form", clear_on_submit=True):
        st.subheader("Form Kunjungan")
        col1, col2 = st.columns(2)
        with col1:
            nama = st.text_input("Nama Lengkap*")
            nip = st.text_input("NIP (Opsional)")
            jabatan = st.text_input("Jabatan*")
            opd = st.text_input("Asal Instansi/OPD*")
        with col2:
            tgl_spt = st.date_input("Tanggal SPT (Jika Ada)", value=None)
            no_hp = st.text_input("Nomor HP/WhatsApp*")
            bidang = st.selectbox("Tujuan Bidang*", ["Sekretariat", "Litbang & Evlap", "Pemerintahan & Sosbud", "Ekonomi", "Sarpras"])
            maksud = st.text_area("Maksud Kunjungan*")
        
        kesan = st.text_area("Kesan & Pesan")
        
        st.divider()
        st.write("📸 **Foto Verifikasi**")
        foto = st.camera_input("Ambil Foto")
        
        st.write("✍️ **Tanda Tangan**")
        canvas_result = st_canvas(
            stroke_width=2, stroke_color="#000", background_color="#fff",
            height=150, width=400, drawing_mode="freedraw", key="canvas_signature"
        )

        btn_label = "SIMPAN DATA" if is_in_range else "LOKASI TIDAK SESUAI"
        submitted = st.form_submit_button(btn_label, disabled=not is_in_range)
        
        if submitted:
            if not nama or not no_hp or not opd or not jabatan or not maksud:
                st.error("Mohon isi semua kolom yang bertanda (*)")
            else:
                entry_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                # Mapping sesuai kolom di gambar image_86b3c7.png
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
                    "foto_url": "Tersimpan di Sistem",
                    "tanda_tangan_url": "Tersimpan di Sistem",
                    "latitude": current_lat,
                    "longitude": current_lon
                }
                
                try:
                    updated_df = pd.concat([df_tamu, pd.DataFrame([entry_data])], ignore_index=True)
                    conn.update(worksheet="data_tamu", data=updated_df)
                    st.success("Terima kasih! Data kunjungan Anda telah tersimpan.")
                    st.balloons()
                    
                    pdf_bytes = create_pdf(entry_data)
                    st.download_button(
                        label="📥 Download Tanda Terima (PDF)",
                        data=pdf_bytes,
                        file_name=f"Tanda_Terima_{entry_id}.pdf",
                        mime="application/pdf"
                    )
                except Exception as e:
                    st.error(f"Terjadi kesalahan saat menyimpan: {e}")

elif menu == "📊 Statistik":
    st.title("Statistik Pengunjung")
    if not df_tamu.empty:
        st.metric("Total Pengunjung", len(df_tamu))
        fig = px.pie(df_tamu, names='bidang_tujuan', title='Persentase Kunjungan per Bidang')
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Data masih kosong.")

elif menu == "📋 Daftar Tamu":
    st.title("Daftar Buku Tamu")
    if not df_tamu.empty:
        st.dataframe(df_tamu, use_container_width=True)
    else:
        st.info("Belum ada data tamu.")
