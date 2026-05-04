import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, date
from streamlit_drawable_canvas import st_canvas
from PIL import Image
import pandas as pd
import base64
import io

st.set_page_config(page_title="Buku Tamu Digital", layout="wide")

# Koneksi Google Sheets
scope = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

creds = Credentials.from_service_account_info(
    st.secrets["gcp_service_account"], scopes=scope
)
client = gspread.authorize(creds)

sheet = client.open_by_key("1lBGe8ZTLBICZz5dbDgPqwNiv4FO-CEFmcSnczYNUxz8").sheet1

# Header
header = [
    "tanggal","tanggal_spt","nama_lengkap","nip","jabatan","opd",
    "nomor_hp","bidang","maksud","foto","tanda_tangan","kesan"
]

if sheet.row_values(1) != header:
    sheet.insert_row(header, 1)

# UI
st.title("📘 Buku Tamu Digital BAPPEDA")

menu = st.sidebar.radio("Menu", ["Input", "Statistik", "Daftar"])

# INPUT
if menu == "Input":
    with st.form("form"):
        nama = st.text_input("Nama")
        tanggal = st.date_input("Tanggal")

        foto = st.camera_input("Foto")
        foto_base64 = ""
        if foto:
            foto_base64 = base64.b64encode(foto.getvalue()).decode()

        canvas = st_canvas(height=200, width=400)
        ttd_base64 = ""
        if canvas.image_data is not None:
            img = Image.fromarray(canvas.image_data.astype("uint8"))
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            ttd_base64 = base64.b64encode(buf.getvalue()).decode()

        submit = st.form_submit_button("Simpan")

        if submit:
            sheet.append_row([str(tanggal),"",nama,"","","","","","",foto_base64,ttd_base64,""])
            st.success("Data tersimpan")

# DAFTAR
elif menu == "Daftar":
    data = sheet.get_all_values()
    if len(data) > 1:
        df = pd.DataFrame(data[1:], columns=data[0])
        st.dataframe(df)

        for _, row in df.iterrows():
            st.write(row["nama_lengkap"])

            if row["foto"]:
                st.image(base64.b64decode(row["foto"]), width=150)

            if row["tanda_tangan"]:
                st.image(base64.b64decode(row["tanda_tangan"]), width=150)
