import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF

DATA_FILE = "data.xlsx"

# Load data
try:
    df = pd.read_excel(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "tanggal", "tanggal_spt", "nama_lengkap", "nip", "jabatan", "opd",
        "nomor_hp", "bidang_tujuan", "maksud_kunjungan", "foto", "tanda_tangan", "kesan_pesan"
    ])

# Sidebar menu
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
            "foto":[""],  # placeholder
            "tanda_tangan":[""],  # placeholder
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
        st.write(f"Tamu hari ini: {len(df[df['tanggal'] == today])}")
        st.write(f"Tamu bulan ini: {len(df[df['tanggal'].dt.month == today.month])}")
        st.write(f"Tamu tahun ini: {len(df[df['tanggal'].dt.year == today.year])}")
    else:
        st.info("Belum ada data tamu.")

# Daftar Buku Tamu
elif menu == "Daftar Buku Tamu":
    st.header("📑 Daftar Buku Tamu")
    if not df.empty:
        st.dataframe(df)
        if st.button("Export PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for i, row in df.iterrows():
                pdf.cell(200, 10, txt=str(row.to_dict()), ln=True)
            pdf.output("daftar_buku_tamu.pdf")
            st.success("PDF berhasil dibuat!")
    else:
        st.info("Belum ada data tamu.")
