# =========================================================
# BUKU TAMU DIGITAL BAPPEDA KOTA PARIAMAN
# FULL PROFESSIONAL VERSION 2026
# SUPPORT:
# - ANDROID
# - IOS / IPHONE
# - WINDOWS
# - TABLET
# - STREAMLIT CLOUD
# =========================================================

# =========================================================
# REQUIREMENTS.TXT
# =========================================================
#
# streamlit
# pandas
# gspread
# google-auth
# openpyxl
# pillow
# python-docx
# reportlab
#
# =========================================================

# =========================================================
# IMPORT
# =========================================================

import streamlit as st
import pandas as pd
import gspread
import os
import re

from io import BytesIO
from datetime import datetime
from google.oauth2.service_account import Credentials

# =========================================================
# OPTIONAL IMPORT DOCX
# =========================================================

try:
    from docx import Document
    DOCX_AVAILABLE = True
except:
    DOCX_AVAILABLE = False

# =========================================================
# OPTIONAL IMPORT PDF
# =========================================================

try:

    from reportlab.platypus import (
        SimpleDocTemplate,
        Paragraph,
        Spacer,
        Table,
        TableStyle
    )

    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.pagesizes import letter

    PDF_AVAILABLE = True

except:
    PDF_AVAILABLE = False

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="Buku Tamu Digital BAPPEDA",
    page_icon="📘",
    layout="wide"
)

# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

/* =====================================================
GLOBAL
===================================================== */

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

/* =====================================================
MAIN BACKGROUND
===================================================== */

.main {
    background-color: #F4F7FE;
}

/* =====================================================
SIDEBAR
===================================================== */

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #081F4D 0%,
        #0D2F75 100%
    );
}

/* =====================================================
SIDEBAR TEXT
===================================================== */

section[data-testid="stSidebar"] * {
    color: white !important;
}

/* =====================================================
TITLE
===================================================== */

.sidebar-title {
    font-size: 30px;
    font-weight: 700;
    margin-bottom: 5px;
}

/* =====================================================
SUBTITLE
===================================================== */

.sidebar-subtitle {
    font-size: 15px;
    color: #D1D5DB !important;
    margin-bottom: 25px;
}

/* =====================================================
BUTTON
===================================================== */

.stButton > button {
    width: 100%;
    border: none;
    border-radius: 10px;
    padding: 0.8rem;
    font-weight: bold;
    color: white !important;
    background: linear-gradient(
        90deg,
        #2563EB,
        #1D4ED8
    );
}

/* =====================================================
DOWNLOAD BUTTON
===================================================== */

.stDownloadButton > button {
    width: 100%;
    border: none;
    border-radius: 10px;
    padding: 0.8rem;
    font-weight: bold;
    color: white !important;
    background: linear-gradient(
        90deg,
        #10B981,
        #059669
    );
}

/* =====================================================
CARD
===================================================== */

.card {
    background: white;
    padding: 20px;
    border-radius: 15px;
    box-shadow:
        0px 3px 10px rgba(0,0,0,0.08);
    margin-bottom: 20px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# GOOGLE SHEETS CONNECTION
# =========================================================

try:

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds_dict = st.secrets["gcp_service_account"]

    creds = Credentials.from_service_account_info(
        creds_dict,
        scopes=scope
    )

    client = gspread.authorize(creds)

    SPREADSHEET_ID = "1lBGe8ZTLBICZz5dbDgPqwNiv4FO-CEFmcSnczYNUxz8"

    sheet = client.open_by_key(
        SPREADSHEET_ID
    ).sheet1

except Exception as e:

    st.error(
        f"Gagal koneksi Google Spreadsheet: {e}"
    )

    st.stop()

# =========================================================
# FOLDER FOTO
# =========================================================

FOTO_DIR = "foto_tamu"

if not os.path.exists(FOTO_DIR):
    os.makedirs(FOTO_DIR)

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.markdown("""
<div class="sidebar-title">
📘 Buku Tamu Digital
</div>

<div class="sidebar-subtitle">
BAPPEDA Kota Pariaman
</div>
""", unsafe_allow_html=True)

menu = st.sidebar.radio(
    "📌 Menu",
    [
        "Dashboard",
        "Input Buku Tamu",
        "Daftar Buku Tamu",
        "Ringkasan Statistik"
    ]
)

# =========================================================
# LOAD DATA
# =========================================================

def load_data():

    try:

        data = sheet.get_all_values()

        if len(data) > 1:

            headers = [
                h.lower().strip()
                for h in data[0]
            ]

            df = pd.DataFrame(
                data[1:],
                columns=headers
            )

            expected_cols = [
                "tanggal",
                "nama",
                "opd",
                "nomor_hp",
                "bidang",
                "foto",
                "spt"
            ]

            for col in expected_cols:

                if col not in df.columns:
                    df[col] = ""

            return df

        return pd.DataFrame()

    except Exception as e:

        st.error(
            f"Gagal memuat data: {e}"
        )

        return pd.DataFrame()

# =========================================================
# SAFE FILE NAME
# =========================================================

def safe_filename(text):

    text = text.strip()

    text = re.sub(
        r'[^a-zA-Z0-9_]',
        '_',
        text
    )

    return text

# =========================================================
# DASHBOARD
# =========================================================

if menu == "Dashboard":

    st.title("📊 Dashboard Buku Tamu")

    df = load_data()

    if not df.empty:

        df["tanggal"] = pd.to_datetime(
            df["tanggal"],
            errors="coerce"
        )

        today = datetime.now()

        total_tamu = len(df)

        harian = len(
            df[
                df["tanggal"].dt.date == today.date()
            ]
        )

        bulanan = len(
            df[
                (df["tanggal"].dt.month == today.month) &
                (df["tanggal"].dt.year == today.year)
            ]
        )

        tahunan = len(
            df[
                df["tanggal"].dt.year == today.year
            ]
        )

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("👥 Total Tamu", total_tamu)

        with col2:
            st.metric("📅 Hari Ini", harian)

        with col3:
            st.metric("🗓️ Bulan Ini", bulanan)

        with col4:
            st.metric("📆 Tahun Ini", tahunan)

        st.divider()

        st.subheader("📈 Grafik Kunjungan")

        grafik = (
            df.groupby(df["tanggal"].dt.date)
            .size()
            .reset_index(name="Jumlah")
        )

        grafik.columns = [
            "Tanggal",
            "Jumlah"
        ]

        st.line_chart(
            grafik.set_index("Tanggal")
        )

        st.divider()

        st.subheader("📋 Data Terbaru")

        st.dataframe(
            df.tail(10),
            use_container_width=True,
            height=350
        )

    else:

        st.info("Belum ada data tamu.")

# =========================================================
# INPUT BUKU TAMU
# =========================================================

elif menu == "Input Buku Tamu":

    st.title("📝 Input Buku Tamu")

    st.warning(
        "⚠️ Semua form wajib diisi."
    )

    st.markdown("""
    ### 📸 Petunjuk Foto
    - Android/iPhone:
      pilih Kamera untuk foto langsung
    - Bisa menggunakan kamera depan
      atau belakang
    - Bisa upload dari galeri
    - Support Windows webcam
    """)

    with st.form(
        "form_tamu",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)

        # =====================================================
        # KOLOM KIRI
        # =====================================================

        with col1:

            tanggal = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )

            st.text_input(
                "Tanggal",
                value=tanggal,
                disabled=True
            )

            nama = st.text_input(
                "Nama Lengkap *"
            )

            opd = st.text_input(
                "Asal / OPD *"
            )

            nomor_hp = st.text_input(
                "Nomor HP *"
            )

        # =====================================================
        # KOLOM KANAN
        # =====================================================

        with col2:

            bidang = st.selectbox(
                "Bidang Tujuan *",
                [
                    "",
                    "Sekretariat",
                    "Bidang Litbang",
                    "Bidang Ekonomi",
                    "Bidang Sarana dan Prasarana Wilayah",
                    "Bidang Pemerintahan dan Sosial Budaya"
                ]
            )

            foto_tamu = st.file_uploader(
                "📷 Upload / Ambil Foto Tamu *",
                type=["jpg", "jpeg", "png"],
                key="foto_tamu"
            )

            foto_spt = st.file_uploader(
                "📄 Upload / Ambil Foto SPT *",
                type=["jpg", "jpeg", "png"],
                key="foto_spt"
            )

        # =====================================================
        # PREVIEW FOTO
        # =====================================================

        st.subheader("👁️ Preview Foto")

        p1, p2 = st.columns(2)

        with p1:

            if foto_tamu:

                st.image(
                    foto_tamu,
                    caption="Foto Tamu",
                    use_container_width=True
                )

        with p2:

            if foto_spt:

                st.image(
                    foto_spt,
                    caption="Foto SPT",
                    use_container_width=True
                )

        # =====================================================
        # SUBMIT
        # =====================================================

        submit = st.form_submit_button(
            "💾 Simpan Data"
        )

        # =====================================================
        # VALIDASI
        # =====================================================

        if submit:

            if nama.strip() == "":
                st.error("Nama wajib diisi.")

            elif opd.strip() == "":
                st.error("Asal / OPD wajib diisi.")

            elif nomor_hp.strip() == "":
                st.error("Nomor HP wajib diisi.")

            elif bidang == "":
                st.error("Bidang wajib dipilih.")

            elif foto_tamu is None:
                st.error("Foto tamu wajib diupload.")

            elif foto_spt is None:
                st.error("Foto SPT wajib diupload.")

            else:

                try:

                    nama_file = safe_filename(
                        nama
                    )

                    timestamp = datetime.now().strftime(
                        "%Y%m%d%H%M%S"
                    )

                    # =================================================
                    # FOTO TAMU
                    # =================================================

                    ext_foto = (
                        foto_tamu.name
                        .split(".")[-1]
                        .lower()
                    )

                    foto_path = (
                        f"{FOTO_DIR}/"
                        f"foto_{nama_file}_{timestamp}.{ext_foto}"
                    )

                    with open(
                        foto_path,
                        "wb"
                    ) as f:

                        f.write(
                            foto_tamu.getbuffer()
                        )

                    # =================================================
                    # FOTO SPT
                    # =================================================

                    ext_spt = (
                        foto_spt.name
                        .split(".")[-1]
                        .lower()
                    )

                    spt_path = (
                        f"{FOTO_DIR}/"
                        f"spt_{nama_file}_{timestamp}.{ext_spt}"
                    )

                    with open(
                        spt_path,
                        "wb"
                    ) as f:

                        f.write(
                            foto_spt.getbuffer()
                        )

                    # =================================================
                    # SAVE TO SHEETS
                    # =================================================

                    sheet.append_row([
                        tanggal,
                        nama,
                        opd,
                        nomor_hp,
                        bidang,
                        foto_path,
                        spt_path
                    ])

                    st.success(
                        "✅ Data berhasil disimpan."
                    )

                    st.balloons()

                except Exception as e:

                    st.error(
                        f"Gagal menyimpan data: {e}"
                    )

# =========================================================
# DAFTAR BUKU TAMU
# =========================================================

elif menu == "Daftar Buku Tamu":

    st.title("📑 Daftar Buku Tamu")

    df = load_data()

    if not df.empty:

        search = st.text_input(
            "🔍 Cari Nama / OPD"
        )

        if search:

            df = df[
                df.apply(
                    lambda row:
                    row.astype(str)
                    .str.contains(
                        search,
                        case=False
                    )
                    .any(),
                    axis=1
                )
            ]

        st.dataframe(
            df,
            use_container_width=True,
            height=400
        )

        st.divider()

        # =====================================================
        # DOWNLOAD
        # =====================================================

        st.subheader("📥 Download Data")

        d1, d2, d3, d4 = st.columns(4)

        # CSV

        csv = df.to_csv(
            index=False
        ).encode("utf-8")

        with d1:

            st.download_button(
                "⬇️ CSV",
                csv,
                "data_buku_tamu.csv",
                "text/csv"
            )

        # =====================================================
        # EXCEL
        # =====================================================

        excel_buffer = BytesIO()

        with pd.ExcelWriter(
            excel_buffer,
            engine="openpyxl"
        ) as writer:

            df.to_excel(
                writer,
                index=False
            )

        with d2:

            st.download_button(
                "⬇️ Excel",
                excel_buffer.getvalue(),
                "data_buku_tamu.xlsx"
            )

        # =====================================================
        # WORD
        # =====================================================

        with d3:

            if DOCX_AVAILABLE:

                try:

                    doc = Document()

                    doc.add_heading(
                        "Data Buku Tamu",
                        level=1
                    )

                    table = doc.add_table(
                        rows=1,
                        cols=len(df.columns)
                    )

                    hdr = table.rows[0].cells

                    for i, col in enumerate(df.columns):
                        hdr[i].text = col

                    for _, row in df.iterrows():

                        cells = table.add_row().cells

                        for i, value in enumerate(row):
                            cells[i].text = str(value)

                    word_buffer = BytesIO()

                    doc.save(word_buffer)

                    st.download_button(
                        "⬇️ Word",
                        word_buffer.getvalue(),
                        "data_buku_tamu.docx"
                    )

                except Exception as e:

                    st.warning(
                        f"Gagal membuat Word: {e}"
                    )

        # =====================================================
        # PDF
        # =====================================================

        with d4:

            if PDF_AVAILABLE:

                try:

                    pdf_buffer = BytesIO()

                    pdf_doc = SimpleDocTemplate(
                        pdf_buffer,
                        pagesize=letter
                    )

                    styles = getSampleStyleSheet()

                    elements = []

                    title = Paragraph(
                        "Data Buku Tamu",
                        styles["Heading1"]
                    )

                    elements.append(title)

                    elements.append(
                        Spacer(1, 12)
                    )

                    pdf_data = [
                        df.columns.tolist()
                    ] + df.values.tolist()

                    pdf_table = Table(
                        pdf_data
                    )

                    pdf_table.setStyle(
                        TableStyle([
                            ('BACKGROUND', (0,0), (-1,0), colors.grey),
                            ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                            ('GRID', (0,0), (-1,-1), 1, colors.black),
                        ])
                    )

                    elements.append(
                        pdf_table
                    )

                    pdf_doc.build(
                        elements
                    )

                    st.download_button(
                        "⬇️ PDF",
                        pdf_buffer.getvalue(),
                        "data_buku_tamu.pdf"
                    )

                except Exception as e:

                    st.warning(
                        f"Gagal membuat PDF: {e}"
                    )

        st.divider()

        # =====================================================
        # DOKUMENTASI FOTO
        # =====================================================

        st.subheader("📷 Dokumentasi Tamu")

        for i, row in df.iterrows():

            with st.expander(
                f"👤 {row['nama']}"
            ):

                c1, c2 = st.columns(2)

                with c1:

                    st.write(
                        f"🏢 OPD : {row['opd']}"
                    )

                    st.write(
                        f"📞 HP : {row['nomor_hp']}"
                    )

                    st.write(
                        f"🏛️ Bidang : {row['bidang']}"
                    )

                    foto = str(
                        row["foto"]
                    )

                    if os.path.exists(foto):

                        st.image(
                            foto,
                            caption="Foto Tamu",
                            use_container_width=True
                        )

                    else:

                        st.warning(
                            "Foto tidak ditemukan."
                        )

                with c2:

                    spt = str(
                        row["spt"]
                    )

                    if os.path.exists(spt):

                        st.image(
                            spt,
                            caption="Foto SPT",
                            use_container_width=True
                        )

                    else:

                        st.warning(
                            "Foto SPT tidak ditemukan."
                        )

        st.divider()

        # =====================================================
        # HAPUS DATA
        # =====================================================

        st.subheader("🗑️ Hapus Data")

        nama_hapus = st.selectbox(
            "Pilih Nama",
            df["nama"].unique()
        )

        if st.button("🗑️ Hapus"):

            try:

                cell = sheet.find(
                    nama_hapus
                )

                if cell:

                    sheet.delete_rows(
                        cell.row
                    )

                    st.success(
                        "Data berhasil dihapus."
                    )

                    st.rerun()

            except Exception as e:

                st.error(
                    f"Gagal hapus data: {e}"
                )

    else:

        st.info(
            "Belum ada data tamu."
        )

# =========================================================
# STATISTIK
# =========================================================

elif menu == "Ringkasan Statistik":

    st.title("📊 Ringkasan Statistik")

    df = load_data()

    if not df.empty:

        df["tanggal"] = pd.to_datetime(
            df["tanggal"],
            errors="coerce"
        )

        statistik = (
            df.groupby(
                df["tanggal"].dt.date
            )
            .size()
            .reset_index(name="Jumlah")
        )

        statistik.columns = [
            "Tanggal",
            "Jumlah"
        ]

        st.subheader(
            "📈 Statistik Kunjungan"
        )

        st.bar_chart(
            statistik.set_index("Tanggal")
        )

        st.divider()

        st.subheader(
            "📸 Statistik Dokumentasi"
        )

        col1, col2 = st.columns(2)

        with col1:

            total_foto = (
                df["foto"]
                .astype(str)
                .apply(
                    lambda x:
                    os.path.exists(x)
                )
                .sum()
            )

            st.metric(
                "📷 Total Foto",
                total_foto
            )

        with col2:

            total_spt = (
                df["spt"]
                .astype(str)
                .apply(
                    lambda x:
                    os.path.exists(x)
                )
                .sum()
            )

            st.metric(
                "📄 Total Foto SPT",
                total_spt
            )

    else:

        st.info(
            "Belum ada data statistik."
        )
