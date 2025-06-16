import streamlit as st
import cv2
import numpy as np
import datetime
import os
import pandas as pd
from streamlit_option_menu import option_menu

# === Konfigurasi halaman ===
st.set_page_config(page_title="Deteksi Penyakit Kulit", layout="wide")

# === CSS untuk tampilan modern ===
st.markdown("""
    <style>
        body {
            background-color: #f0f2f6;
        }
        .stSidebar {
            background-color: #e3e7ed;
        }
        .title-center {
            text-align: center;
        }
        .judul-aplikasi {
            font-size: 36px;
            color: #0066cc;
            font-weight: bold;
        }
    </style>
""", unsafe_allow_html=True)

# === Inisialisasi Folder ===
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

if "mulai_deteksi" not in st.session_state:
    st.session_state.mulai_deteksi = False
if "last_saved" not in st.session_state:
    st.session_state.last_saved = datetime.datetime.min

# === Menu Navigasi ===
selected = option_menu(
    menu_title="Menu",
    options=["Beranda", "Pemeriksaan", "Riwayat", "Tentang"],
    icons=["house", "camera", "clock-history", "info-circle"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal"
)

face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# === Halaman Beranda ===
if selected == "Beranda":
    st.markdown(f"""
        <div style='text-align: center; padding: 2rem 0;'>
            <h1 style='font-size: 3rem; color: #00A8E8;'>🌿 SkinScan</h1>
            <p style='font-size: 1.2rem;'>Deteksi gejala kulit wajah dengan kamera </p>
        </div>
    """, unsafe_allow_html=True)
    st.info("Silakan buka menu **Pemeriksaan** dan isi data diri terlebih dahulu.")

# === Halaman Riwayat ===
elif selected == "Riwayat":
    st.title("🕒 Riwayat Pemeriksaan Anda")
    nama_pengguna = st.sidebar.text_input("🔐 Masukkan Nama Anda untuk melihat riwayat:", key="riwayat_nama")

    if nama_pengguna:
        nama_file = f"riwayat_{nama_pengguna.replace(' ', '_')}.csv"
        if os.path.exists(nama_file):
            df = pd.read_csv(nama_file)
            if not df.empty:
                for index, row in df.iterrows():
                    with st.container():
                        st.markdown(f"""
                            <div style='background-color:#fff;border-radius:10px;padding:1rem;margin-bottom:1rem;
                            box-shadow:0 2px 8px rgba(0,0,0,0.1);'>
                                <h4>👤 {row['Nama']} — {row['Tanggal']} {row['Waktu']}</h4>
                                <p>Usia: {row['Usia']} | Jenis Kelamin: {row['Jenis Kelamin']}</p>
                                <p>Gejala: {row['Gejala']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        if os.path.exists(row['Gambar']):
                            st.image(row['Gambar'], width=300)
            else:
                st.info("✅ Riwayat Anda masih kosong.")
            with open(nama_file, "rb") as file:
                st.download_button("⬇️ Unduh Riwayat Saya (.CSV)", file, file_name=f"riwayat_{nama_pengguna}.csv", mime="text/csv")
        else:
            st.warning("⚠️ Riwayat belum ditemukan untuk nama tersebut.")
    else:
        st.info("Masukkan nama Anda untuk melihat riwayat.")

# === Halaman Tentang ===
elif selected == "Tentang":
    st.title("ℹ️ Tentang Aplikasi")
    st.markdown("""
    Aplikasi ini dikembangkan untuk membantu pengguna mendeteksi gejala umum penyakit kulit wajah
    seperti ruam, kemerahan, bercak kuning, dan jerawat secara cepat menggunakan kamera webcam.

    **Disclaimer:** Aplikasi ini bukan pengganti konsultasi dengan tenaga medis profesional.
    """)

# === Halaman Pemeriksaan ===
elif selected == "Pemeriksaan":
    st.title("🯪 Deteksi Penyakit Kulit via Kamera")
    st.markdown("Aplikasi interaktif untuk mendeteksi ruam, kemerahan, bercak kuning, dan jerawat pada kulit wajah secara langsung.")

    st.sidebar.header("🧝‍♂️ Data Diri Pengguna")
    nama = st.sidebar.text_input("Nama Lengkap", "")
    usia = st.sidebar.number_input("Usia", min_value=1, max_value=120, value=20)
    gender = st.sidebar.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    tanggal_pemeriksaan = datetime.date.today()

    if not nama:
        st.sidebar.warning("⚠️ Masukkan nama lengkap terlebih dahulu.")
        st.stop()

    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Pengaturan Deteksi")
    deteksi_ruam = st.sidebar.checkbox("Deteksi Ruam / Kemerahan", value=True)
    deteksi_bercak = st.sidebar.checkbox("Deteksi Bercak Kuning", value=True)
    deteksi_jerawat = st.sidebar.checkbox("Deteksi Jerawat", value=True)

    sensitivitas_ruam = st.sidebar.slider("Sensitivitas Ruam", 100, 2000, 500, step=50)
    sensitivitas_bercak = st.sidebar.slider("Sensitivitas Bercak", 50, 1500, 300, step=50)
    sensitivitas_jerawat = st.sidebar.slider("Sensitivitas Jerawat", 30, 500, 120, step=10)

    col1, col2 = st.columns(2)
    with col1:
        start = st.button("▶️ Mulai Kamera")
    with col2:
        stop = st.button("⏹️ Stop Kamera")

    frame_placeholder = st.empty()
    saran_obat_placeholder = st.sidebar.empty()

    def deteksi_gejala_di_wajah(frame):
        wajah_kuning_terdeteksi = False
        wajah_pucat_terdeteksi = False
        wajah_merah_terdeteksi = False
        jerawat_terdeteksi = False

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

        for (x, y, w, h) in faces:
            wajah = frame[y:y + h, x:x + w]
            hsv = cv2.cvtColor(wajah, cv2.COLOR_BGR2HSV)

            if deteksi_bercak:
                kuning_bawah = np.array([20, 100, 100])
                kuning_atas = np.array([35, 255, 255])
                mask_kuning = cv2.inRange(hsv, kuning_bawah, kuning_atas)
                if cv2.countNonZero(mask_kuning) > sensitivitas_bercak:
                    wajah_kuning_terdeteksi = True
                    cv2.putText(frame, "Bercak Kuning", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

            if deteksi_ruam:
                merah_bawah = np.array([0, 70, 50])
                merah_atas = np.array([10, 255, 255])
                mask_merah = cv2.inRange(hsv, merah_bawah, merah_atas)
                if cv2.countNonZero(mask_merah) > sensitivitas_ruam:
                    wajah_merah_terdeteksi = True
                    cv2.putText(frame, "Ruam/Kemerahan", (x, y + h + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

            if deteksi_jerawat:
                mask_merah_jerawat = cv2.inRange(hsv, merah_bawah, merah_atas)
                contours, _ = cv2.findContours(mask_merah_jerawat, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contours:
                    area = cv2.contourArea(cnt)
                    if 30 < area < sensitivitas_jerawat:
                        jerawat_terdeteksi = True
                        x1, y1, w1, h1 = cv2.boundingRect(cnt)
                        cv2.rectangle(wajah, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 255), 1)
                        cv2.putText(frame, "Jerawat", (x + x1, y + y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)

            rata2_saturasi = np.mean(hsv[:, :, 1])
            if rata2_saturasi < 40:
                wajah_pucat_terdeteksi = True
                cv2.putText(frame, "Pucat", (x, y + h + 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

            cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 255, 100), 2)

        return frame, wajah_kuning_terdeteksi, wajah_pucat_terdeteksi, wajah_merah_terdeteksi, jerawat_terdeteksi

    if start:
        st.subheader("📋 Data Pemeriksaan")
        st.json({"Nama": nama, "Usia": usia, "Jenis Kelamin": gender, "Tanggal": str(tanggal_pemeriksaan)})
        cap = cv2.VideoCapture(0)

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                st.warning("⚠️ Gagal membuka kamera.")
                break

            frame = cv2.flip(frame, 1)
            frame, wajah_kuning, wajah_pucat, wajah_merah, jerawat = deteksi_gejala_di_wajah(frame)
            gejala_terdeteksi = any([wajah_kuning, wajah_pucat, wajah_merah, jerawat])
            waktu_sekarang = datetime.datetime.now()

            if gejala_terdeteksi and (waktu_sekarang - st.session_state.last_saved).total_seconds() > 10:
                timestamp = waktu_sekarang.strftime("%Y%m%d_%H%M%S")
                screenshot_path = f"screenshots/deteksi_{timestamp}.jpg"
                cv2.imwrite(screenshot_path, frame)
                st.session_state.last_saved = waktu_sekarang

                st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="📷 Gambar Deteksi Disimpan", use_container_width=True)
                st.markdown("### 📑 Hasil Deteksi:")
                gejala_list = []
                if wajah_kuning:
                    gejala_list.append("Bercak Kuning")
                if wajah_merah:
                    gejala_list.append("Ruam / Kemerahan")
                if wajah_pucat:
                    gejala_list.append("Wajah Pucat")
                if jerawat:
                    gejala_list.append("Jerawat")

                for g in gejala_list:
                    st.success(f"✅ {g} terdeteksi")

                hasil = {
                    "Nama": nama,
                    "Usia": usia,
                    "Jenis Kelamin": gender,
                    "Tanggal": str(tanggal_pemeriksaan),
                    "Waktu": waktu_sekarang.strftime("%H:%M:%S"),
                    "Gejala": ", ".join(gejala_list),
                    "Gambar": screenshot_path
                }
                nama_file = f"riwayat_{nama.replace(' ', '_')}.csv"
                pd.DataFrame([hasil]).to_csv(nama_file, mode='a', header=not os.path.exists(nama_file), index=False)
            else:
                frame_placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)

            saran_obat = ""
            if wajah_kuning:
                saran_obat += "- Gunakan salep antijamur atau antibiotik ringan.\n"
            if wajah_merah:
                saran_obat += "- Gunakan krim anti-inflamasi seperti hidrokortison.\n"
            if wajah_pucat:
                saran_obat += "- Periksa kadar hemoglobin, konsumsi makanan bergizi.\n"
            if jerawat:
                saran_obat += "- Gunakan obat jerawat dengan benzoyl peroxide atau salicylic acid.\n"

            saran_obat_placeholder.markdown("#💊 Saran Obat")
            if saran_obat:
                saran_obat_placeholder.markdown(saran_obat)
            else:
                saran_obat_placeholder.markdown("Tidak ada gejala terdeteksi")

            if stop:
                cap.release()
                break
