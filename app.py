# =========================================================
# BUKU TAMU DIGITAL BAPPEDA KOTA PARIAMAN
# FULL PROFESSIONAL VERSION 2026
# FINAL STABLE VERSION
# =========================================================

# =========================================================
# IMPORT
# =========================================================

import streamlit as st
import pandas as pd
import gspread
import base64

from io import BytesIO
from datetime import datetime
from google.oauth2.service_account import Credentials

# =========================================================
# OPTIONAL IMPORT DOCX
# =========================================================

try:
    from docx import Document
    DOCX_AVAILABLE = True
except Exception:
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

except Exception:
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

html, body, [class*="css"] {
    font-family: 'Segoe UI', sans-serif;
}

.main {
    background-color: #F4F7FE;
}

section[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #081F4D 0%,
        #0D2F75 100%
    );
}

section[data-testid="stSidebar"] * {
    color: white !important;
}

.stButton > button {
    width: 100%;
    border-radius: 10px;
    border: none;
    padding: 0.7rem;
    font-weight: bold;
    color: white !important;
    background: linear-gradient(
        90deg,
        #2563EB,
        #1D4ED8
    );
}

.stDownloadButton > button {
    width: 100%;
    border-radius: 10px;
    border: none;
    padding: 0.7rem;
    font-weight: bold;
    color: white !important;
    background: linear-gradient(
        90deg,
        #10B981,
        #059669
    );
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# GOOGLE SHEETS CONNECTION
# =========================================================

@st.cache_resource
def connect_sheet():

    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)

    spreadsheet = client.open_by_key(
        "1lBGe8ZTLBICZz5dbDgPqwNiv4FO-CEFmcSnczYNUxz8"
    )

    return spreadsheet.sheet1

try:

    sheet = connect_sheet()

except Exception as e:

    st.error(
        f"Gagal koneksi Google Sheets: {e}"
    )

    st.stop()

# =========================================================
# SIDEBAR
# =========================================================

st.sidebar.title("📘 Buku Tamu Digital")
st.sidebar.caption("BAPPEDA Kota Pariaman")

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

@st.cache_data(ttl=30)
def load_data():

    try:

        data = sheet.get_all_values()

        columns = [
            "tanggal",
            "nama",
            "opd",
            "nomor_hp",
            "bidang",
            "foto",
            "spt"
        ]

        if len(data) <= 1:
            return pd.DataFrame(columns=columns)

        headers = [
            h.lower().strip()
            for h in data[0]
        ]

        df = pd.DataFrame(
            data[1:],
            columns=headers
        )

        for col in columns:

            if col not in df.columns:
                df[col] = ""

        return df

    except Exception as e:

        st.error(
            f"Gagal memuat data: {e}"
        )

        return pd.DataFrame()

# =========================================================
# SHOW IMAGE
# =========================================================

def show_image(base64_string, caption):

    try:

        if str(base64_string).strip() == "":
            st.warning("Gambar kosong.")
            return

        image_bytes = base64.b64decode(
            base64_string
        )

        st.image(
            image_bytes,
            caption=caption,
            use_container_width=True
        )

    except Exception:
        st.warning("Gambar gagal ditampilkan.")

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

        total = len(df)

        hari_ini = len(
            df[
                df["tanggal"].dt.date == today.date()
            ]
        )

        bulan_ini = len(
            df[
                (df["tanggal"].dt.month == today.month)
                &
                (df["tanggal"].dt.year == today.year)
            ]
        )

        tahun_ini = len(
            df[
                df["tanggal"].dt.year == today.year
            ]
        )

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("👥 Total", total)
        c2.metric("📅 Hari Ini", hari_ini)
        c3.metric("🗓️ Bulan Ini", bulan_ini)
        c4.metric("📆 Tahun Ini", tahun_ini)

        st.divider()

        grafik = (
            df.groupby(
                df["tanggal"].dt.date
            )
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

    else:

        st.info("Belum ada data.")

# =========================================================
# INPUT BUKU TAMU
# =========================================================

elif menu == "Input Buku Tamu":

    st.title("📝 Input Buku Tamu")

    with st.form("form_tamu"):

        col1, col2 = st.columns(2)

        with col1:

            nama = st.text_input(
                "Nama Lengkap"
            )

            opd = st.text_input(
                "Asal / OPD"
            )

            nomor_hp = st.text_input(
                "Nomor HP"
            )

        with col2:

            bidang = st.selectbox(
                "Bidang",
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
                "Upload Foto Tamu",
                type=["jpg", "jpeg", "png"]
            )

            foto_spt = st.file_uploader(
                "Upload Foto SPT",
                type=["jpg", "jpeg", "png"]
            )

        submit = st.form_submit_button(
            "💾 Simpan Data"
        )

        if submit:

            if nama == "":
                st.error("Nama wajib diisi.")

            elif opd == "":
                st.error("OPD wajib diisi.")

            elif nomor_hp == "":
                st.error("Nomor HP wajib diisi.")

            elif bidang == "":
                st.error("Bidang wajib dipilih.")

            elif foto_tamu is None:
                st.error("Foto tamu wajib diupload.")

            elif foto_spt is None:
                st.error("Foto SPT wajib diupload.")

            else:

                try:

                    foto_base64 = base64.b64encode(
                        foto_tamu.getvalue()
                    ).decode()

                    spt_base64 = base64.b64encode(
                        foto_spt.getvalue()
                    ).decode()

                    tanggal = datetime.now().strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )

                    sheet.append_row([
                        tanggal,
                        nama,
                        opd,
                        nomor_hp,
                        bidang,
                        foto_base64,
                        spt_base64
                    ])

                    st.success(
                        "✅ Data berhasil disimpan."
                    )

                    st.cache_data.clear()

                    st.rerun()

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

        st.dataframe(
            df.drop(columns=["foto", "spt"]),
            use_container_width=True,
            hide_index=True
        )

        st.divider()

        st.subheader("📷 Dokumentasi")

        for _, row in df.iterrows():

            with st.expander(
                f"👤 {row['nama']}"
            ):

                c1, c2 = st.columns(2)

                with c1:
                    show_image(
                        row["foto"],
                        "Foto Tamu"
                    )

                with c2:
                    show_image(
                        row["spt"],
                        "Foto SPT"
                    )

    else:

        st.info("Belum ada data.")

# =========================================================
# RINGKASAN STATISTIK
# =========================================================

elif menu == "Ringkasan Statistik":

    st.title("📊 Ringkasan Statistik")

    df = load_data()

    if not df.empty:

        st.metric(
            "👥 Total Tamu",
            len(df)
        )

        st.divider()

        st.subheader("📷 Dokumentasi Visual")

        for _, row in df.tail(10).iterrows():

            with st.expander(
                f"👤 {row['nama']}"
            ):

                col1, col2 = st.columns(2)

                with col1:
                    show_image(
                        row["foto"],
                        "Foto Tamu"
                    )

                with col2:
                    show_image(
                        row["spt"],
                        "Foto SPT"
                    )

    else:

        st.info("Belum ada data statistik.")
```
