import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import os

# --- Konfigurasi Google Sheets ---
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

# Ganti dengan nama file atau ID spreadsheet
sheet = client.open("Buku Tamu Digital").sheet1

FOTO_DIR = "foto_tamu"
if not os.path.exists(FOTO_DIR):
    os.makedirs(FOTO_DIR)

# --- UI Styling ---
st.set_page_config(page_title="Buku Tamu Digital BAPPEDA", page_icon="📘", layout="wide")

st.markdown(
    """
    <style>
    .main { background-color: #f9f9f9; }
    h1 { color: #2c3e50; text-align: center; }
    .stButton>button {
        background-color: #2ecc71;
        color: white;
        border-radius: 8px;
        padding: 0.6em 1.2em;
        font-weight: bold;
    }
    .stTextInput>div>input, .stDateInput>div>input, .stTextArea>div>textarea {
        border-radius: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# --- Sidebar Menu ---
menu = st.sidebar.radio("📌 Menu", ["Halaman Utama", "Ringkasan Statistik", "Daftar Buku Tamu"])

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
        bidang = st.selectbox("Bidang Tujuan", ["Sekretariat", "Bidang Litbang", "Bidang Ekonomi", "Bidang Sarana"])
        maksud = st.text_area("Maksud Kunjungan")
        kesan = st.text_area("Kesan dan Pesan")

        st.subheader("📷 Ambil Foto")
        foto = st.camera_input("Ambil foto tamu")
        foto_path = ""
        if foto is not None and nama:
            foto_filename = f"{FOTO_DIR}/foto_{nama}_{tanggal}.png"
            with open(foto_filename, "wb") as f:
                f.write(foto.getbuffer())
            foto_path = foto_filename

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
        tanda_tangan_path = ""
        if canvas_result.image_data is not None and nama:
            tanda_filename = f"{FOTO_DIR}/ttd_{nama}_{tanggal}.png"
            Image.fromarray(canvas_result.image_data.astype("uint8")).save(tanda_filename)
            tanda_tangan_path = tanda_filename

        submitted = st.form_submit_button("💾 Simpan Data")
        if submitted:
            sheet.append_row([
                str(tanggal), str(tanggal_spt), nama, nip, jabatan, opd,
                nomor_hp, bidang, maksud, foto_path, tanda_tangan_path, kesan
            ])
            st.success(f"Data tamu {nama} berhasil disimpan!")

# --- Ringkasan Statistik ---
elif menu == "Ringkasan Statistik":
    st.header("📊 Ringkasan Statistik")
    data = sheet.get_all_records()
    if data:
        df = pd.DataFrame(data)
        df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
        today = datetime.today().date()
        st.write(f"Tamu hari ini: {len(df[df['tanggal'].dt.date == today])}")
        st.write(f"Tamu bulan ini: {len(df[df['tanggal'].dt.month == today.month])}")
        st.write(f"Tamu tahun ini: {len(df[df['tanggal'].dt.year == today.year])}")
    else:
        st.info("Belum ada data tamu.")

# --- Daftar Buku Tamu ---
elif menu == "Daftar Buku Tamu":
    st.header("📑 Daftar Buku Tamu")
    data = sheet.get_all_records()
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        st.subheader("📷 History Foto & ✍️ Tanda Tangan")
        for i, row in df.iterrows():
            st.write(f"Nama: {row['nama_lengkap']} | Tanggal: {row['tanggal']}")
            if row["foto"]:
                st.image(row["foto"], caption="Foto Tamu", width=200)
            if row["tanda_tangan"]:
                st.image(row["tanda_tangan"], caption="Tanda Tangan", width=200)
            st.write("---")

        st.subheader("🗑️ Hapus Data Tamu")
        nama_to_delete = st.selectbox("Pilih nama tamu", df["nama_lengkap"].unique())
        if st.button("Delete by Name"):
            cell = sheet.find(nama_to_delete)
            if cell:
                sheet.delete_rows(cell.row)
                st.success(f"Data tamu {nama_to_delete} berhasil dihapus!")
    else:
        st.info("Belum ada data tamu.")
