import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas

# File Excel
DATA_FILE = "data.xlsx"

# Load data
try:
    df = pd.read_excel(DATA_FILE)
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "Tanggal", "Tanggal SPT", "Nama Lengkap", "NIP", "Jabatan", "OPD",
        "Nomor HP", "Bidang Tujuan", "Maksud Kunjungan", "Foto", "Tanda Tangan", "Kesan Pesan"
    ])

# Sidebar menu
menu = st.sidebar.radio("Menu", ["Halaman Utama", "Ringkasan Statistik", "Daftar Buku Tamu", "Laporan"])

# Halaman Utama
if menu == "Halaman Utama":
    st.title("📖 Selamat Datang di Buku Tamu Digital BAPPEDA Kota Pariaman")
    st.write("Silakan isi data tamu di bawah ini:")

    # Form input
    tanggal = st.date_input("Tanggal")
    tanggal_spt = st.date_input("Tanggal SPT")
    nama = st.text_input("Nama Lengkap")
    nip = st.text_input("NIP")
    jabatan = st.text_input("Jabatan")
    opd = st.text_input("OPD")
    nomor_hp = st.text_input("Nomor HP")
    bidang = st.selectbox("Bidang Tujuan", [
        "Sekretariat", "Bidang Litbang & Evlap", "Bidang Pemerintahan dan Sosial Budaya",
        "Bidang Ekonomi", "Bidang Sarana dan Prasarana Wilayah"
    ])
    maksud = st.text_area("Maksud dan Tujuan Kunjungan")

    # Kamera & Upload
    foto_camera = st.camera_input("Ambil Foto")
    foto_upload = st.file_uploader("Upload Foto", type=["jpg", "png"])

    # Tanda tangan
    st.write("Tanda Tangan:")
    canvas_result = st_canvas(
        fill_color="rgba(255, 255, 255, 0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#ffffff",
        height=150,
        width=400,
        drawing_mode="freedraw",
        key="canvas",
    )

    kesan = st.text_area("Kesan dan Pesan")

    if st.button("Simpan"):
        new_data = pd.DataFrame({
            "Tanggal":[tanggal],
            "Tanggal SPT":[tanggal_spt],
            "Nama Lengkap":[nama],
            "NIP":[nip],
            "Jabatan":[jabatan],
            "OPD":[opd],
            "Nomor HP":[nomor_hp],
            "Bidang Tujuan":[bidang],
            "Maksud Kunjungan":[maksud],
            "Foto":[foto_upload.name if foto_upload else ("camera.jpg" if foto_camera else "")],
            "Tanda Tangan":["canvas.png" if canvas_result.image_data is not None else ""],
            "Kesan Pesan":[kesan]
        })
        df = pd.concat([df, new_data], ignore_index=True)
        df.to_excel(DATA_FILE, index=False)
        st.success("Data berhasil disimpan!")

# Ringkasan Statistik
elif menu == "Ringkasan Statistik":
    st.header("📊 Ringkasan Statistik Pengunjung")
    if not df.empty:
        today = datetime.today().date()
        st.write(f"Tamu hari ini: {len(df[df['Tanggal'] == today])}")
        st.write(f"Tamu bulan ini: {len(df[df['Tanggal'].dt.month == today.month])}")
        st.write(f"Tamu tahun ini: {len(df[df['Tanggal'].dt.year == today.year])}")

        # Grafik
        st.subheader("Grafik Pengunjung per Bulan")
        df['Bulan'] = df['Tanggal'].dt.month
        chart_data = df['Bulan'].value_counts().sort_index()
        fig, ax = plt.subplots()
        chart_data.plot(kind="bar", ax=ax)
        st.pyplot(fig)
    else:
        st.info("Belum ada data tamu.")

# Daftar Buku Tamu
elif menu == "Daftar Buku Tamu":
    st.header("📑 Daftar Buku Tamu")
    if not df.empty:
        st.dataframe(df)

        # Filter
        nama_filter = st.text_input("Cari Nama")
        if nama_filter:
            st.dataframe(df[df["Nama Lengkap"].str.contains(nama_filter, case=False)])

        # Export PDF
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

# Laporan
elif menu == "Laporan":
    st.header("📝 Laporan")
    if not df.empty:
        st.write("Laporan Harian, Bulanan, Tahunan")

        # Export PDF
        if st.button("Export Laporan PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt="Laporan Buku Tamu", ln=True)
            for i, row in df.iterrows():
                pdf.cell(200, 10, txt=str(row.to_dict()), ln=True)
            pdf.output("laporan_buku_tamu.pdf")
            st.success("PDF laporan berhasil dibuat!")
    else:
        st.info("Belum ada data tamu.")
