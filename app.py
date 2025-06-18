import streamlit as st
import cv2
import numpy as np
import datetime
import os
import pandas as pd
from streamlit_option_menu import option_menu

# === Konfigurasi halaman ===
st.set_page_config(page_title="Deteksi Penyakit Kulit", layout="wide")

# === CSS Modern ===
st.markdown("""
    <style>
        body { background-color: #f0f2f6; }
        .stSidebar { background-color: #e3e7ed; }
        .judul-aplikasi { font-size: 36px; color: #0066cc; font-weight: bold; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# === Inisialisasi Folder ===
if not os.path.exists("screenshots"):
    os.makedirs("screenshots")

# === State Default ===
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

# === Model Deteksi Wajah ===
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# === Halaman Beranda ===
if selected == "Beranda":
    st.markdown("""
        <div class='judul-aplikasi'>🌿 SkinScan</div>
        <p style='text-align:center;'>Deteksi gejala kulit wajah dengan kamera</p>
    """, unsafe_allow_html=True)
    st.info("Silakan buka menu Pemeriksaan dan isi data diri terlebih dahulu.")

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
                                <p>Saran Obat: {row['Hasil Saran Obat']}</p>
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
    Selamat datang di SkinScan – solusi cerdas untuk memantau kesehatan kulit Anda secara cepat dan praktis.
Kami adalah tim pengembang yang peduli terhadap kesehatan dan kecantikan kulit, serta berkomitmen menghadirkan teknologi terkini dalam bidang deteksi dini penyakit kulit melalui kamera dan kecerdasan buatan.

Aplikasi SkinScan dirancang untuk membantu pengguna mendeteksi berbagai permasalahan kulit wajah, seperti jerawat, ruam, bercak kuning, atau tanda-tanda wajah pucat yang dapat mengindikasikan kondisi kesehatan tertentu.
Dengan dukungan analisis visual berbasis AI dan tampilan yang user-friendly, kami ingin memberikan kemudahan bagi siapa saja untuk lebih memahami kondisi kulit mereka, kapan pun dan di mana pun.

Kami percaya bahwa deteksi dini adalah langkah pertama menuju perawatan yang tepat. Karena itu, SkinScan terus dikembangkan dan diperbarui untuk memberikan hasil analisis yang lebih akurat dan saran yang lebih tepat sesuai kebutuhan Anda.

Terima kasih telah mempercayakan perawatan kulit Anda bersama SkinScan.
Kami selalu terbuka untuk saran dan masukan demi pengembangan aplikasi yang lebih baik di masa depan.



    Disclaimer: Aplikasi ini bukan pengganti konsultasi dengan tenaga medis profesional.
    """)
    st.markdown("---")
    st.subheader("🤖 Tanya Jawab Seputar Kulit Wajah")

    with st.chat_message("assistant"):
        st.markdown("Halo! Saya SkinBot, siap bantu kamu. Ketik pertanyaanmu ya!")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    user_input = st.chat_input("Tulis pertanyaan...")

    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        jawaban = "Maaf, saya belum mengerti. Coba tanyakan hal lain ya!"

        if "jerawat" in user_input.lower():
            jawaban = "Jerawat bisa disebabkan oleh hormon, stres, atau makanan berminyak. Cuci muka rutin dan gunakan obat yang sesuai."
        elif "pucat" in user_input.lower():
            jawaban = "Wajah pucat bisa menandakan kekurangan zat besi. Konsumsi sayur hijau atau konsultasi ke dokter."
        elif "ruam" in user_input.lower() or "kemerahan" in user_input.lower():
            jawaban = "Ruam biasanya disebabkan oleh iritasi atau alergi. Hindari produk baru dan gunakan krim penenang."
        elif "obat" in user_input.lower():
            jawaban = "Untuk jerawat ringan, gunakan benzoyl peroxide. Untuk kemerahan, bisa pakai hidrokortison ringan."
        elif "bercak" in user_input.lower():
            jawaban = "Bercak kuning bisa disebabkan infeksi bakteri atau jamur. Gunakan salep antibakteri/antijamur ringan."

        st.session_state.chat_history.append(("bot", jawaban))

    for role, msg in st.session_state.chat_history:
        with st.chat_message("user" if role == "user" else "assistant"):
            st.markdown(msg)

# === Halaman Pemeriksaan ===
elif selected == "Pemeriksaan":
    st.title("🯪 Deteksi Penyakit Kulit via Kamera")
    st.markdown("Aplikasi interaktif untuk mendeteksi ruam, kemerahan, bercak kuning, dan jerawat pada kulit wajah.")

    st.sidebar.header("🧝‍♂️ Data Diri Pengguna")
    nama = st.sidebar.text_input("Nama Lengkap", "")
    usia = st.sidebar.number_input("Usia", min_value=1, max_value=120, value=20)
    gender = st.sidebar.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"])
    tanggal_pemeriksaan = datetime.date.today()

    if not nama:
        st.sidebar.warning("⚠️ Masukkan nama lengkap terlebih dahulu.")
        st.stop()

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
        kuning, pucat, merah, jerawat = False, False, False, False
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.1, 5)
        for (x, y, w, h) in faces:
            wajah = frame[y:y+h, x:x+w]
            hsv = cv2.cvtColor(wajah, cv2.COLOR_BGR2HSV)

            if deteksi_bercak:
                kuning_mask = cv2.inRange(hsv, np.array([20, 100, 100]), np.array([35, 255, 255]))
                if cv2.countNonZero(kuning_mask) > sensitivitas_bercak:
                    kuning = True
                    cv2.putText(frame, "Bercak Kuning", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,255), 2)

            if deteksi_ruam:
                merah_mask = cv2.inRange(hsv, np.array([0, 70, 50]), np.array([10, 255, 255]))
                if cv2.countNonZero(merah_mask) > sensitivitas_ruam:
                    merah = True
                    cv2.putText(frame, "Ruam", (x, y+h+20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

            if deteksi_jerawat:
                contours, _ = cv2.findContours(merah_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                for cnt in contours:
                    if 30 < cv2.contourArea(cnt) < sensitivitas_jerawat:
                        jerawat = True
                        x1, y1, w1, h1 = cv2.boundingRect(cnt)
                        cv2.rectangle(wajah, (x1, y1), (x1+w1, y1+h1), (255,0,255), 1)
                        cv2.putText(frame, "Jerawat", (x+x1, y+y1-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255,0,255), 1)

            if np.mean(hsv[:,:,1]) < 40:
                pucat = True
                cv2.putText(frame, "Pucat", (x, y+h+40), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200,200,200), 2)

            cv2.rectangle(frame, (x, y), (x+w, y+h), (100,255,100), 2)
        return frame, kuning, pucat, merah, jerawat

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
            frame, kuning, pucat, merah, jerawat = deteksi_gejala_di_wajah(frame)
            waktu = datetime.datetime.now()
            gejala_terdeteksi = any([kuning, pucat, merah, jerawat])

            if gejala_terdeteksi and (waktu - st.session_state.last_saved).total_seconds() > 10:
                timestamp = waktu.strftime("%Y%m%d_%H%M%S")
                screenshot = f"screenshots/deteksi_{timestamp}.jpg"
                cv2.imwrite(screenshot, frame)
                st.session_state.last_saved = waktu

                st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="📷 Gambar Disimpan", use_container_width=True)
                gejala_list = []
                if kuning: gejala_list.append("Bercak Kuning")
                if merah: gejala_list.append("Ruam / Kemerahan")
                if pucat: gejala_list.append("Wajah Pucat")
                if jerawat: gejala_list.append("Jerawat")

                saran = ""
                if kuning: saran += "- Gunakan salep antijamur/antibiotik ringan.\n"
                if merah: saran += "- Gunakan krim anti-inflamasi (hidrokortison).\n"
                if pucat: saran += "- Periksa darah, konsumsi makanan bergizi.\n"
                if jerawat: saran += "- Obat jerawat: benzoyl peroxide/salicylic acid.\n"

                hasil = {
                    "Nama": nama,
                    "Usia": usia,
                    "Jenis Kelamin": gender,
                    "Tanggal": str(tanggal_pemeriksaan),
                    "Waktu": waktu.strftime("%H:%M:%S"),
                    "Gejala": ", ".join(gejala_list),
                    "Gambar": screenshot,
                    "Hasil Saran Obat": saran.replace('\n', ' ')
                }

                nama_file = f"riwayat_{nama.replace(' ', '_')}.csv"
                pd.DataFrame([hasil]).to_csv(nama_file, mode='a', header=not os.path.exists(nama_file), index=False)

                st.success("✅ Gejala terdeteksi:")
                for g in gejala_list:
                    st.write(f"- {g}")

                with saran_obat_placeholder.container():
                    st.markdown("### 💊 Saran Obat")
                    st.markdown(saran)
            else:
                frame_placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB", use_container_width=True)
                with saran_obat_placeholder.container():
                    st.markdown("### 💊 Saran Obat")
                    st.markdown("Tidak ada gejala terdeteksi.")

            if stop:
                cap.release()
                break