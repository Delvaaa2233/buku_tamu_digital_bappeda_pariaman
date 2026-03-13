import streamlit as st
import pandas as pd
from datetime import datetime
from fpdf import FPDF
from streamlit_drawable_canvas import st_canvas

DATA_FILE = "data.xlsx"

# Load data
try:
    df = pd.read_excel(DATA_FILE, engine="openpyxl")
except FileNotFoundError:
    df = pd.DataFrame(columns=[
        "tanggal", "tanggal_spt", "nama_lengkap", "nip", "jabatan", "opd",
        "nomor_hp", "bidang_tujuan", "maksud_kunjungan", "foto", "tanda_tangan", "kesan_pesan"
    ])

# Sidebar menu
menu = st.sidebar.radio("Menu", ["Halaman Utama", "Ringkasan Statistik", "Daftar Buku Tamu", "Laporan"])

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
            "foto":[str(foto) if foto else ""],
            "tanda_tangan":[str(canvas_result.image_data) if canvas_result.image_data is not None else ""],
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

        # 🔹 Fitur Delete Data Tamu (berdasarkan index)
        st.subheader("🗑️ Hapus Data Tamu berdasarkan Index")
        index_to_delete = st.number_input(
            "Masukkan nomor index tamu yang ingin dihapus (mulai dari 0)",
            min_value=0,
            max_value=len(df)-1,
            step=1
        )
        if st.button("Delete by Index"):
            df = df.drop(index_to_delete).reset_index(drop=True)
            df.to_excel(DATA_FILE, index=False)
            st.success(f"Data tamu dengan index {index_to_delete} berhasil dihapus!")

        # 🔹 Fitur Delete Data Tamu (berdasarkan nama)
        st.subheader("🗑️ Hapus Data Tamu berdasarkan Nama")
        nama_to_delete = st.selectbox("Pilih nama tamu yang ingin dihapus", df["nama_lengkap"].unique())
        if st.button("Delete by Name"):
            df = df[df["nama_lengkap"] != nama_to_delete].reset_index(drop=True)
            df.to_excel(DATA_FILE, index=False)
            st.success(f"Data tamu dengan nama {nama_to_delete} berhasil dihapus!")

        # 🔹 Export PDF daftar tamu
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

# Menu Laporan
elif menu == "Laporan":
    st.header("📊 Laporan")

    if not df.empty:
        # Laporan Harian
        st.subheader("📅 Laporan Harian")
        tanggal_laporan = st.date_input("Pilih tanggal laporan")
        if st.button("Generate Laporan Harian"):
            laporan_harian = df[df["tanggal"] == tanggal_laporan]
            st.write(laporan_harian)
            st.write(f"Total tamu pada {tanggal_laporan}: {len(laporan_harian)}")

            # Export PDF Harian
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Laporan Harian {tanggal_laporan}", ln=True)
            for i, row in laporan_harian.iterrows():
                pdf.cell(200, 10, txt=str(row.to_dict()), ln=True)
            pdf.output("laporan_harian.pdf")
            st.success("PDF Laporan Harian berhasil dibuat!")

        # Laporan Bulanan
        st.subheader("📆 Laporan Bulanan")
        bulan_laporan = st.selectbox("Pilih bulan laporan", range(1,13))
        tahun_bulan = st.number_input("Masukkan tahun laporan", min_value=2000, max_value=2100, value=datetime.today().year)
        if st.button("Generate Laporan Bulanan"):
            laporan_bulanan = df[(df["tanggal"].dt.month == bulan_laporan) & (df["tanggal"].dt.year == tahun_bulan)]
            st.write(laporan_bulanan)
            st.write(f"Total tamu bulan {bulan_laporan}-{tahun_bulan}: {len(laporan_bulanan)}")

            # Export PDF Bulanan
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Laporan Bulanan {bulan_laporan}-{tahun_bulan}", ln=True)
            for i, row in laporan_bulanan.iterrows():
                pdf.cell(200, 10, txt=str(row.to_dict()), ln=True)
            pdf.output("laporan_bulanan.pdf")
            st.success("PDF Laporan Bulanan berhasil dibuat!")

        # Laporan Tahunan
        st.subheader("📆 Laporan Tahunan")
        tahun_laporan = st.number_input("Masukkan tahun laporan tahunan", min_value=2000, max_value=2100, value=datetime.today().year)
        if st.button("Generate Laporan Tahunan"):
            laporan_tahunan = df[df["tanggal"].dt.year == tahun_laporan]
            st.write(laporan_tahunan)
            st.write(f"Total tamu tahun {tahun_laporan}: {len(laporan_tahunan)}")

            # Export PDF Tahunan
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.cell(200, 10, txt=f"Laporan Tahunan {tahun_laporan}", ln=True)
            for i, row in laporan_tahunan.iterrows():
                pdf.cell(200, 10, txt=str(row.to_dict()), ln=True)
            pdf.output("laporan_tahunan.pdf")
            st.success("PDF Laporan Tahunan berhasil dibuat!")
    else:
        st.info("Belum ada data tamu.")
