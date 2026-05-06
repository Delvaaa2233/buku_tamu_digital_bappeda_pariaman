import os
from datetime import date
from PIL import Image
import streamlit as st
from streamlit_drawable_canvas import st_canvas

FOTO_DIR = "data_upload"
os.makedirs(FOTO_DIR, exist_ok=True)

with st.form("form_tamu", clear_on_submit=True):
    tanggal = st.date_input("Tanggal", value=date.today())
    nama = st.text_input("Nama Lengkap")
    nip = st.text_input("NIP")
    jabatan = st.text_input("Jabatan")
    opd = st.text_input("Asal/OPD")
    nomor_hp = st.text_input("No. HP")

    bidang = st.selectbox("Bidang Tujuan", [
        "Sekretariat", "Bidang Litbang", "Bidang Ekonomi",
        "Bidang Sarana dan Prasarana Wilayah", "Bidang Pemerintahan dan Sosial Budaya"
    ])

    # ================= FOTO TAMU =================
    st.subheader("📷 Foto Tamu (Wajib)")
    foto = st.camera_input("Ambil foto tamu")

    # ================= FOTO / FILE SPT =================
    st.subheader("📄 Upload / Ambil Foto SPT")
    spt_file = st.file_uploader(
        "Upload SPT (JPG, PNG, PDF)",
        type=["jpg", "jpeg", "png", "pdf"]
    )
    spt_camera = st.camera_input("Atau ambil foto SPT")

    # ================= TANDA TANGAN =================
    st.subheader("✍️ Tanda Tangan Digital")
    canvas_result = st_canvas(
        fill_color="rgba(255,255,255,0)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        height=200,
        width=400,
        drawing_mode="freedraw",
        key="ttd",
    )

    submitted = st.form_submit_button("💾 Simpan Data")

    if submitted:
        # ================= VALIDASI =================
        if nama.strip() == "":
            st.warning("Nama wajib diisi!")
        elif opd.strip() == "":
            st.warning("Asal/OPD wajib diisi!")
        elif nomor_hp.strip() == "":
            st.warning("No. HP wajib diisi!")
        elif foto is None:
            st.warning("Foto tamu wajib diambil!")
        else:
            try:
                # Sanitasi nama file
                nama_file = nama.replace(" ", "_").replace("/", "_")

                # ================= SIMPAN FOTO TAMU =================
                foto_path = ""
                foto_filename = f"{FOTO_DIR}/foto_{nama_file}_{tanggal}.png"
                with open(foto_filename, "wb") as f:
                    f.write(foto.getbuffer())
                foto_path = foto_filename

                # ================= SIMPAN SPT =================
                spt_path = ""

                if spt_file is not None:
                    ext = spt_file.name.split(".")[-1]
                    spt_filename = f"{FOTO_DIR}/spt_{nama_file}_{tanggal}.{ext}"
                    with open(spt_filename, "wb") as f:
                        f.write(spt_file.getbuffer())
                    spt_path = spt_filename

                elif spt_camera is not None:
                    spt_filename = f"{FOTO_DIR}/spt_{nama_file}_{tanggal}.png"
                    with open(spt_filename, "wb") as f:
                        f.write(spt_camera.getbuffer())
                    spt_path = spt_filename

                # ================= SIMPAN TTD =================
                ttd_path = ""
                if canvas_result.image_data is not None:
                    ttd_filename = f"{FOTO_DIR}/ttd_{nama_file}_{tanggal}.png"
                    img = Image.fromarray(canvas_result.image_data.astype("uint8"))
                    img.save(ttd_filename)
                    ttd_path = ttd_filename

                # ================= SIMPAN KE GOOGLE SHEETS =================
                sheet.append_row([
                    str(tanggal),
                    nama,
                    nip,
                    jabatan,
                    opd,
                    nomor_hp,
                    bidang,
                    foto_path,
                    spt_path,
                    ttd_path
                ], value_input_option="USER_ENTERED")

                st.success(f"Data tamu {nama} berhasil disimpan!")

            except Exception as e:
                st.error(f"Gagal menyimpan data: {e}")
