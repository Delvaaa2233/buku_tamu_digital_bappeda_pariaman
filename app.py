import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import pandas as pd
import base64
import io

# ================== CONFIG ==================
st.set_page_config(
    page_title="Buku Tamu Digital BAPPEDA",
    layout="wide",
    page_icon="📘"
)

# ================== STYLE MODERN ==================
st.markdown("""
<style>
body {
    background-color: #f4f6f9;
}
.header {
    background: linear-gradient(90deg, #0d47a1, #1976d2);
    padding: 20px;
    border-radius: 12px;
    color: white;
    text-align: center;
}
.card {
    background: white;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 4px 10px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}
.stButton>button {
    background-color: #0d47a1;
    color: white;
    border-radius: 10px;
    padding: 8px 16px;
}
</style>
""", unsafe_allow_html=True)

# ================== GOOGLE SHEETS ==================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(creds)

SPREADSHEET_ID = "1lBGe8ZTLBICZz5dbDgPqwNiv4FO-CEFmcSnczYNUxz8"
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

HEADER = [
    "tanggal","nama_lengkap","nip","jabatan","opd",
    "nomor_hp","bidang","maksud","foto","tanda_tangan","kesan"
]

if sheet.row_values(1) != HEADER:
    sheet.insert_row(HEADER, 1)

# ================== HEADER ==================
st.markdown("""
<div class="header">
    <h1>📘 BUKU TAMU DIGITAL</h1>
    <h3>BAPPEDA KOTA PARIAMAN</h3>
</div>
""", unsafe_allow_html=True)

# ================== MENU ==================
menu = st.sidebar.radio("📌 Menu", ["Input Tamu", "Dashboard", "Daftar Tamu"])

# --- Halaman Utama ---
if menu == "Halaman Utama":
    st.title("📘 Selamat Datang di Buku Tamu Digital BAPPEDA Kota Pariaman")

    with st.form("form_tamu", clear_on_submit=True):
        tanggal = st.date_input("Tanggal", value=date.today())
        tanggal_spt = st.date_input("Tanggal SPT", value=date.today())
        nama = st.text_input("Nama Lengkap")
        nip = st.text_input("NIP")
        jabatan = st.text_input("Jabatan")
        opd = st.text_input("OPD")
        nomor_hp = st.text_input("Nomor HP")

        bidang = st.selectbox("Bidang Tujuan", [
            "Sekretariat",
            "Bidang Litbang",
            "Bidang Ekonomi",
            "Bidang Sarana dan Prasarana Wilayah",
            "Bidang Pemerintahan dan Sosial Budaya"
        ])

        maksud = st.text_area("Maksud Kunjungan")
        kesan = st.text_area("Kesan dan Pesan")

        # ================= FOTO =================
        st.subheader("📷 Ambil Foto")
        foto = st.camera_input("Ambil foto tamu")

        import base64, io
        foto_base64 = ""
        if foto is not None:
            foto_base64 = base64.b64encode(foto.getvalue()).decode()

        # ================= TANDA TANGAN =================
        st.subheader("✍️ Tanda Tangan Digital")
        canvas_result = st_canvas(
            fill_color="rgba(255, 255, 255, 0)",
            stroke_width=2,
            stroke_color="#000000",
            background_color="#FFFFFF",
            update_streamlit=True,
            height=200,
            width=400,
            drawing_mode="freedraw",
            key="tanda_tangan",
        )

        ttd_base64 = ""
        if canvas_result.image_data is not None:
            img = Image.fromarray(canvas_result.image_data.astype("uint8"))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            ttd_base64 = base64.b64encode(buf.getvalue()).decode()

        # ================= SIMPAN =================
        submitted = st.form_submit_button("💾 Simpan Data")

        if submitted:
            sheet.append_row([
                str(tanggal),
                str(tanggal_spt),
                nama,
                nip,
                jabatan,
                opd,
                nomor_hp,
                bidang,
                maksud,
                foto_base64,
                ttd_base64,
                kesan
            ])

            st.success(f"Data tamu {nama} berhasil disimpan!")

# ================== DASHBOARD ==================
elif menu == "Dashboard":
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📊 Statistik Kunjungan")

    data = sheet.get_all_values()

    if len(data) > 1:
        df = pd.DataFrame(data[1:], columns=data[0])
        df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")

        today = datetime.today()

        col1, col2, col3 = st.columns(3)
        col1.metric("Hari Ini", len(df[df["tanggal"].dt.date == today.date()]))
        col2.metric("Bulan Ini", len(df[df["tanggal"].dt.month == today.month]))
        col3.metric("Tahun Ini", len(df[df["tanggal"].dt.year == today.year]))

        st.subheader("Distribusi Bidang")
        st.bar_chart(df["bidang"].value_counts())

    else:
        st.info("Belum ada data")

    st.markdown('</div>', unsafe_allow_html=True)

# ================== DAFTAR ==================
elif menu == "Daftar Tamu":
    st.markdown('<div class="card">', unsafe_allow_html=True)

    st.subheader("📑 Data Tamu")

    data = sheet.get_all_values()

    if len(data) > 1:
        df = pd.DataFrame(data[1:], columns=data[0])
        st.dataframe(df, use_container_width=True)

        st.subheader("📷 Dokumentasi")

        for _, row in df.iterrows():
            st.markdown(f"**{row['nama_lengkap']}** ({row['tanggal']})")

            col1, col2 = st.columns(2)

            with col1:
                if row["foto"]:
                    st.image(base64.b64decode(row["foto"]), width=200)

            with col2:
                if row["tanda_tangan"]:
                    st.image(base64.b64decode(row["tanda_tangan"]), width=200)

            st.divider()

    else:
        st.info("Belum ada data")

    st.markdown('</div>', unsafe_allow_html=True)
