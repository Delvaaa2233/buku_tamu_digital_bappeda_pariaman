import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import pandas as pd
import base64
import io

# ================= CONFIG =================
st.set_page_config(
    page_title="Selamat Datang di Buku Tamu Digital BAPPEDA Kota Pariaman",
    page_icon="📘",
    layout="wide"
)

# ================= SAFE BASE64 =================
def safe_b64_image(data):
    try:
        if isinstance(data, str) and data.strip():
            return base64.b64decode(data)
    except Exception:
        return None
    return None

# ================= GOOGLE SHEETS =================
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

# ================= HEADER =================
st.markdown("""
<div style='background:linear-gradient(90deg,#0d47a1,#1976d2);
padding:20px;border-radius:10px;color:white;text-align:center'>
<h2>📘 BUKU TAMU DIGITAL</h2>
<h4>BAPPEDA KOTA PARIAMAN</h4>
</div>
""", unsafe_allow_html=True)

# ================= MENU =================
menu = st.sidebar.radio("📌 Menu", ["Input Tamu", "Dashboard", "Daftar Tamu"])

# ================= INPUT =================
if menu == "Input Tamu":

    st.title("Form Buku Tamu")

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
                "Litbang",
                "Ekonomi",
                "Sarana & Prasarana",
                "Pemerintahan & Sosial Budaya"
            ])

        maksud = st.text_area("Maksud Kunjungan *")
        kesan = st.text_area("Kesan & Pesan")

        # ================= FOTO =================
        st.subheader("📷 Foto Tamu")
        foto = st.camera_input("Ambil Foto")

        foto_base64 = ""
        if foto is not None:
            foto_base64 = base64.b64encode(foto.getvalue()).decode()
            st.image(foto.getvalue(), width=200)

        # ================= TTD =================
        st.subheader("✍️ Tanda Tangan")

        canvas = st_canvas(
            fill_color="rgba(255,255,255,0)",
            stroke_width=2,
            stroke_color="#000000",
            background_color="#FFFFFF",
            height=200,
            width=400,
            drawing_mode="freedraw",
            key="ttd"
        )

        ttd_base64 = ""
        if canvas.image_data is not None:
            img = Image.fromarray(canvas.image_data.astype("uint8"))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            ttd_base64 = base64.b64encode(buf.getvalue()).decode()
            st.image(buf.getvalue(), width=200)

        # ================= SUBMIT =================
        submit = st.form_submit_button("💾 Simpan Data")

        if submit:
            if not nama or not maksud:
                st.warning("Nama dan Maksud wajib diisi!")
            else:
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
                st.success("Data berhasil disimpan!")

# ================= DASHBOARD =================
elif menu == "Dashboard":

    st.title("📊 Dashboard Statistik")

    data = sheet.get_all_values()

    if len(data) > 1:

        df = pd.DataFrame(data[1:], columns=data[0])

        # amanin kolom
        for col in ["foto", "tanda_tangan", "nama_lengkap", "tanggal"]:
            if col not in df.columns:
                df[col] = ""

        df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")

        today = datetime.today()

        col1, col2, col3 = st.columns(3)
        col1.metric("Hari Ini", len(df[df["tanggal"].dt.date == today.date()]))
        col2.metric("Bulan Ini", len(df[df["tanggal"].dt.month == today.month]))
        col3.metric("Tahun Ini", len(df[df["tanggal"].dt.year == today.year]))

        st.subheader("📊 Bidang Kunjungan")
        st.bar_chart(df["bidang"].value_counts())

        st.subheader("📈 Tren Kunjungan")
        st.line_chart(df.groupby(df["tanggal"].dt.date).size())

    else:
        st.info("Belum ada data")

# ================= DAFTAR =================
elif menu == "Daftar Tamu":

    st.title("📑 Daftar Buku Tamu")

    data = sheet.get_all_values()

    if len(data) > 1:

        df = pd.DataFrame(data[1:], columns=data[0])

        # aman kolom
        for col in ["foto", "tanda_tangan", "nama_lengkap", "tanggal"]:
            if col not in df.columns:
                df[col] = ""

        # search aman
        search = st.text_input("🔍 Cari Nama")

        if search:
            df = df[df["nama_lengkap"].fillna("").str.contains(search, case=False)]

        st.dataframe(df, use_container_width=True)
        
# ================= DOKUMENTASI SUPER AMAN =================
st.subheader("📷 Dokumentasi Tamu")

for _, row in df.iterrows():

    nama = row.get("nama_lengkap", "-")
    tanggal = row.get("tanggal", "-")

    st.markdown(f"**👤 {nama}**  |  📅 {tanggal}")

    col1, col2 = st.columns(2)

    # ================= FOTO AMAN =================
    with col1:
        try:
            foto_b64 = row.get("foto", "")

            if foto_b64 and isinstance(foto_b64, str) and foto_b64.strip():

                foto_bytes = base64.b64decode(foto_b64)

                if len(foto_bytes) > 0:
                    img = Image.open(io.BytesIO(foto_bytes))
                    st.image(img, width=180)
                else:
                    st.info("Foto kosong")

            else:
                st.info("Foto tidak tersedia")

        except Exception:
            st.info("Foto rusak / tidak bisa dibaca")

    # ================= TTD AMAN =================
    with col2:
        try:
            ttd_b64 = row.get("tanda_tangan", "")

            if ttd_b64 and isinstance(ttd_b64, str) and ttd_b64.strip():

                ttd_bytes = base64.b64decode(ttd_b64)

                if len(ttd_bytes) > 0:
                    img = Image.open(io.BytesIO(ttd_bytes))
                    st.image(img, width=180)
                else:
                    st.info("TTD kosong")

            else:
                st.info("Tanda tangan tidak tersedia")

        except Exception:
            st.info("Tanda tangan rusak / tidak bisa dibaca")

    st.divider()

# ================= EXPORT =================
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "📥 Download Data CSV",
    csv,
    "buku_tamu.csv",
    "text/csv"
)
