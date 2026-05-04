import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import os
import pandas as pd
import base64
import io

# ================= GOOGLE SHEETS =================
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

SPREADSHEET_ID = "1lBGe8ZTLBICZz5dbDgPqwNiv4FO-CEFmcSnczYNUxz8"
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

# ================= SETUP =================
FOTO_DIR = "foto_tamu"
if not os.path.exists(FOTO_DIR):
    os.makedirs(FOTO_DIR)

st.set_page_config(
    page_title="Buku Tamu Digital BAPPEDA",
    page_icon="📘",
    layout="wide"
)

# ================= STYLE =================
st.markdown("""
<style>
.main { background-color: #f4f6f9; }

.header {
    background: linear-gradient(90deg,#0d47a1,#1976d2);
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
    background-color:#0d47a1;
    color:white;
    border-radius:8px;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div class="header">
<h1>📘 BUKU TAMU DIGITAL</h1>
<h3>BAPPEDA KOTA PARIAMAN</h3>
</div>
""", unsafe_allow_html=True)

# ================= MENU =================
menu = st.sidebar.radio("📌 Menu", ["Halaman Utama", "Ringkasan Statistik", "Daftar Buku Tamu"])

# ================= HALAMAN UTAMA =================
if menu == "Halaman Utama":
    st.title("📘 Selamat Datang di Buku Tamu Digital")

    with st.form("form_tamu", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            tanggal = st.date_input("Tanggal", value=date.today())
            tanggal_spt = st.date_input("Tanggal SPT", value=date.today())
            nama = st.text_input("Nama Lengkap *")
            nip = st.text_input("NIP")
            jabatan = st.text_input("Jabatan")

        with col2:
            opd = st.text_input("OPD")
            nomor_hp = st.text_input("Nomor HP")
            bidang = st.selectbox("Bidang Tujuan", [
                "Sekretariat",
                "Bidang Litbang",
                "Bidang Ekonomi",
                "Bidang Sarana dan Prasarana Wilayah",
                "Bidang Pemerintahan dan Sosial Budaya"
            ])

        maksud = st.text_area("Maksud Kunjungan *")
        kesan = st.text_area("Kesan dan Pesan")

        # ================= FOTO =================
        st.subheader("📷 Ambil Foto")
        foto = st.camera_input("Ambil foto tamu")

        foto_base64 = ""
        if foto is not None:
            foto_bytes = foto.getvalue()
            foto_base64 = base64.b64encode(foto_bytes).decode()
            st.image(foto_bytes, caption="Preview Foto", width=200)

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

            ttd_bytes = buf.getvalue()
            ttd_base64 = base64.b64encode(ttd_bytes).decode()

            st.image(ttd_bytes, caption="Preview Tanda Tangan", width=200)

        # ================= SIMPAN =================
        submitted = st.form_submit_button("💾 Simpan Data")

        if submitted:
            if nama == "" or maksud == "":
                st.warning("⚠️ Nama dan Maksud Kunjungan wajib diisi!")
            else:
                with st.spinner("Menyimpan data..."):
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
                st.success(f"✅ Data tamu {nama} berhasil disimpan!")

# ================= RINGKASAN =================
elif menu == "Ringkasan Statistik":
    st.title("📊 Dashboard Statistik")

    data = sheet.get_all_values()

    if len(data) > 1:
        df = pd.DataFrame(data[1:], columns=data[0])
        df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")

        today = datetime.today()

        col1, col2, col3 = st.columns(3)
        col1.metric("Hari Ini", len(df[df["tanggal"].dt.date == today.date()]))
        col2.metric("Bulan Ini", len(df[df["tanggal"].dt.month == today.month]))
        col3.metric("Tahun Ini", len(df[df["tanggal"].dt.year == today.year]))

        st.subheader("📊 Distribusi Bidang")
        st.bar_chart(df["bidang"].value_counts())

        st.subheader("📈 Tren Kunjungan")
        st.line_chart(df.groupby(df["tanggal"].dt.date).size())

    else:
        st.info("Belum ada data tamu.")

# ================= DAFTAR =================
elif menu == "Daftar Buku Tamu":
    st.title("📑 Daftar Buku Tamu")

    data = sheet.get_all_values()

    if len(data) > 1:
        df = pd.DataFrame(data[1:], columns=data[0])

        # SEARCH
        search = st.text_input("🔍 Cari Nama")
        if search:
            df = df[df["nama_lengkap"].str.contains(search, case=False)]

        st.dataframe(df, use_container_width=True)

        st.subheader("📷 Dokumentasi")

        for _, row in df.iterrows():
            st.markdown(f"**{row['nama_lengkap']}** | {row['tanggal']}")

            col1, col2 = st.columns(2)

            with col1:
                if row["foto"]:
                    st.image(base64.b64decode(row["foto"]), width=200)

            with col2:
                if row["tanda_tangan"]:
                    st.image(base64.b64decode(row["tanda_tangan"]), width=200)

            st.divider()

        # EXPORT CSV
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("📥 Download CSV", csv, "buku_tamu.csv", "text/csv")

        # DELETE
        st.subheader("🗑️ Hapus Data")
        row_to_delete = st.number_input("Nomor baris (lihat tabel)", min_value=2)

        if st.button("Hapus Data"):
            sheet.delete_rows(int(row_to_delete))
            st.success("Data berhasil dihapus")

    else:
        st.info("Belum ada data tamu.")
