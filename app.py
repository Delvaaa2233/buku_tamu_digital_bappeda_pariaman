import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import os
import pandas as pd

# --- Konfigurasi Google Sheets ---
scope = ["https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive"]

creds_dict = st.secrets["gcp_service_account"]
creds = Credentials.from_service_account_info(creds_dict, scopes=scope)
client = gspread.authorize(creds)

# Pakai Spreadsheet ID langsung
SPREADSHEET_ID = "1lBGe8ZTLBICZz5dbDgPqwNiv4FO-CEFmcSnczYNUxz8"
sheet = client.open_by_key(SPREADSHEET_ID).sheet1

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
        nama = st.text_input("Nama Lengkap")
        opd = st.text_input("Asal / OPD") 
        nomor_hp = st.text_input("Nomor HP")
        bidang = st.selectbox("Bidang Tujuan", [
            "Sekretariat", "Bidang Litbang", "Bidang Ekonomi",
            "Bidang Sarana dan Prasarana Wilayah", "Bidang Pemeritahan dan Sosia Budaya"
        ])
        
# ================= FOTO TAMU =================
st.subheader("📷 Foto Tamu")
foto_tamu = st.camera_input("Ambil foto tamu")

foto_tamu_path = ""
if foto_tamu is not None and nama.strip() != "":
    nama_file = nama.replace(" ", "_").replace("/", "_")
    foto_tamu_filename = f"{FOTO_DIR}/foto_{nama_file}_{tanggal}.png"

    with open(foto_tamu_filename, "wb") as f:
        f.write(foto_tamu.getbuffer())

    foto_tamu_path = foto_tamu_filename


# ================= FOTO SPT =================
st.subheader("📄 Foto SPT")
foto_spt = st.camera_input("Ambil foto SPT")

foto_spt_path = ""
if foto_spt is not None and nama.strip() != "":
    nama_file = nama.replace(" ", "_").replace("/", "_")
    foto_spt_filename = f"{FOTO_DIR}/spt_{nama_file}_{tanggal}.png"

    with open(foto_spt_filename, "wb") as f:
        f.write(foto_spt.getbuffer())

    foto_spt_path = foto_spt_filename

submitted = st.form_submit_button("💾 Simpan Data")

if submitted:
    try:
        sheet.append_row([
            str(tanggal),
            nama,
            nip,
            jabatan,
            opd,
            nomor_hp,
            bidang,
            foto_tamu_path,
            foto_spt_path,
            tanda_tangan_path
        ], value_input_option="USER_ENTERED")

        st.success(f"Data tamu {nama} berhasil disimpan!")

    except Exception as e:
        st.error(f"Gagal menyimpan data: {e}")

# --- Ringkasan Statistik ---
elif menu == "Ringkasan Statistik":
    st.header("📊 Ringkasan Statistik")
    data = sheet.get_all_values()
    if len(data) > 1:  # ada header + isi
        df = pd.DataFrame(data[1:], columns=data[0])
        df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
        today = datetime.today().date()
        st.write(f"Tamu hari ini: {len(df[df['tanggal'].dt.date == today])}")
        st.write(f"Tamu bulan ini: {len(df[df['tanggal'].dt.month == today.month])}")
        st.write(f"Tamu tahun ini: {len(df[df['tanggal'].dt.year == today.year])}")
    else:
        st.info("Belum ada data tamu.")

elif menu == "Daftar Buku Tamu":
    st.header("📑 Daftar Buku Tamu")

    data = sheet.get_all_values()

    if len(data) > 1:
        df = pd.DataFrame(data[1:], columns=[col.lower().strip() for col in data[0]])

        st.dataframe(df, use_container_width=True)

        # ================= FOTO, SPT, TTD =================
        st.subheader("📷 Foto | 📄 SPT | ✍️ TTD")

        for i, row in df.iterrows():
            st.write(f"Nama: {row.get('nama')} | Tanggal: {row.get('tanggal')}")

            # FOTO TAMU
            foto = row.get("foto")
            if foto:
                if foto.startswith("http"):
                    st.image(foto, caption="Foto Tamu", width=200)
                elif os.path.exists(foto):
                    st.image(foto, caption="Foto Tamu", width=200)
                else:
                    st.warning("Foto tidak tersedia")

            # SPT
            spt = row.get("spt")
            if spt:
                if spt.endswith(".pdf"):
                    st.write(f"📄 SPT (PDF): {spt}")
                elif os.path.exists(spt):
                    st.image(spt, caption="SPT", width=200)

            # TTD
            ttd = row.get("ttd")
            if ttd and os.path.exists(ttd):
                st.image(ttd, caption="Tanda Tangan", width=200)

            st.markdown("---")

        # ================= HAPUS DATA =================
        st.subheader("🗑️ Hapus Data Tamu")

        if "nama" in df.columns:
            nama_list = df["nama"].dropna().unique()

            nama_to_delete = st.selectbox("Pilih nama tamu", nama_list)

            if st.button("Hapus Data"):
                try:
                    cell = sheet.find(nama_to_delete)
                    if cell:
                        sheet.delete_rows(cell.row)
                        st.success(f"Data tamu {nama_to_delete} berhasil dihapus!")
                    else:
                        st.warning("Data tidak ditemukan")

                except Exception as e:
                    st.error(f"Gagal menghapus data: {e}")
        else:
            st.warning("Kolom 'nama' tidak ditemukan di Google Sheets")

    else:
        st.info("Belum ada data tamu.")
