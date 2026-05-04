import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas
import os
from PIL import Image

DATA_FILE = "data.xlsx"
FOTO_DIR = "foto_tamu"

# Pastikan folder foto ada
if not os.path.exists(FOTO_DIR):
    os.makedirs(FOTO_DIR)

# Load data
try:
    df = pd.read_excel(DATA_FILE, engine="openpyxl")
    # 🔹 Pastikan kolom tanggal jadi datetime
    if not df.empty and df["tanggal"].dtype == "object":
        df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "tanggal", "tanggal_spt", "nama_lengkap", "nip", "jabatan", "opd",
        "nomor_hp", "bidang_tujuan", "maksud_kunjungan", "foto", "tanda_tangan", "kesan_pesan"
    ])

# Sidebar menu (hapus menu Laporan)
menu = st.sidebar.radio("Menu", ["Halaman Utama", "Ringkasan Statistik", "Daftar Buku Tamu"])

# Halaman Utama
if menu == "Halaman Utama":
    st.title("📘 Selamat Datang di Buku Tamu Digital BAPPEDA Kota Pariaman")

    tanggal = st.date_input("Tanggal")
    tanggal_spt = st.date_input("Tanggal SPT")
    nama = st.text_input("Nama Lengkap")
    nip = st.text_input("NIP")
    jabatan = st.text_input("Jabatan")
    opd = st.text_input("OPD")
    nomor_hp = st.text_input("Nomor HP")
    bidang = st.selectbox("Bidang Tujuan", ["Sekretariat", "Bidang Litbang", "Bidang Ekonomi", "Bidang Sarana"])
    maksud = st.text_area("Maksud Kunjungan")
    kesan = st.text_area("Kesan dan Pesan")

    # 🔹 Fitur Kamera
    st.subheader("📷 Ambil Foto")
    foto = st.camera_input("Ambil foto tamu")

    foto_path = ""
    if foto is not None and nama:
        foto_filename = f"{FOTO_DIR}/foto_{nama}_{tanggal}.png"
        with open(foto_filename, "wb") as f:
            f.write(foto.getbuffer())
        foto_path = foto_filename

    # 🔹 Fitur Tanda Tangan
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

    if st.button("Simpan"):
        new_data = pd.DataFrame({
            "tanggal":[tanggal],
            "tanggal_spt":[tanggal_spt],
            "nama_lengkap":[nama],
            "nip":[nip],
            "jabatan":[jabatan],
            "opd":[opd],
            "nomor_hp":[nomor_hp],
            "bidang_tujuan":[bidang],
            "maksud_kunjungan":[maksud],
            "foto":[foto_path],
            "tanda_tangan":[tanda_tangan_path],
            "kesan_pesan":[kesan]
        })
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(DATA_FILE, index=False)
        st.success("Data berhasil disimpan!")

# Ringkasan Statistik
elif menu == "Ringkasan Statistik":
    st.header("📊 Ringkasan Statistik")
    if not df.empty:
        today = datetime.today().date()
        # Pastikan kolom tanggal sudah datetime
        df["tanggal"] = pd.to_datetime(df["tanggal"], errors="coerce")

        st.write(f"Tamu hari ini: {len(df[df['tanggal'].dt.date == today])}")
        st.write(f"Tamu bulan ini: {len(df[df['tanggal'].dt.month == today.month])}")
        st.write(f"Tamu tahun ini: {len(df[df['tanggal'].dt.year == today.year])}")
    else:
        st.info("Belum ada data tamu.")

# Daftar Buku Tamu
elif menu == "Daftar Buku Tamu":
    st.header("📑 Daftar Buku Tamu")
    if not df.empty:
        st.dataframe(df)

        # 🔹 Tampilkan foto & tanda tangan history
        st.subheader("📷 History Foto & ✍️ Tanda Tangan")
        for i, row in df.iterrows():
            st.write(f"Nama: {row['nama_lengkap']} | Tanggal: {row['tanggal']}")
            if row["foto"]:
                st.image(row["foto"], caption="Foto Tamu", width=200)
            if row["tanda_tangan"]:
                st.image(row["tanda_tangan"], caption="Tanda Tangan", width=200)
            st.write("---")

        # 🔹 Fitur Delete Data Tamu
        st.subheader("🗑️ Hapus Data Tamu berdasarkan Index")
        index_to_delete = st.number_input("Masukkan nomor index tamu", min_value=0, max_value=len(df)-1, step=1)
        if st.button("Delete by Index"):
            df = df.drop(index_to_delete).reset_index(drop=True)
            df.to_excel(DATA_FILE, index=False)
            st.success(f"Data tamu dengan index {index_to_delete} berhasil dihapus!")

        st.subheader("🗑️ Hapus Data Tamu berdasarkan Nama")
        nama_to_delete = st.selectbox("Pilih nama tamu", df["nama_lengkap"].unique())
        if st.button("Delete by Name"):
            df = df[df["nama_lengkap"] != nama_to_delete].reset_index(drop=True)
            df.to_excel(DATA_FILE, index=False)
            st.success(f"Data tamu dengan nama {nama_to_delete} berhasil dihapus!")

        
