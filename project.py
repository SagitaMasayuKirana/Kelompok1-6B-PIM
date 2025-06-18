import streamlit as st
import cv2
import numpy as np
import datetime
import os
import pandas as pd
import base64
from streamlit_option_menu import option_menu

# === Konfigurasi halaman ===
st.set_page_config(
    page_title="Deteksi Penyakit Kulit",
    layout="wide",
    page_icon="🧑‍⚕️"
)
st.markdown("""
    <style>
        :root {
            --primary: #4a8bfc;
            --secondary: #f0f7ff;
            --accent: #ff6b6b;
            --dark: #2e4057;
            --light: #ffffff;
            --gray: #f8f9fa;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--gray);
            color: var(--dark);
        }

        .stApp {
            background: linear-gradient(135deg, var(--secondary) 0%, var(--gray) 100%);
        }

        .judul-aplikasi {
            font-size: 2.5rem;
            color: var(--primary);
            font-weight: 800;
            text-align: center;
            margin-bottom: 0.5rem;
            background: linear-gradient(90deg, var(--primary) 0%, #6c5ce7 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .stSidebar {
            background-color: var(--light);
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            border-radius: 0 12px 12px 0;
        }

        .stButton>button {
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            transition: all 0.3s;
            border: none;
        }

        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }

        .css-1v3fvcr {
            border-radius: 12px;
            padding: 1.5rem;
            background-color: var(--light);
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        }

        .history-card {
            background: white;
            border-radius: 10px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border-left: 4px solid var(--primary);
            transition: transform 0.3s;
        }

        .history-card:hover {
            transform: translateY(-3px);
            box-shadow: 0 6px 16px rgba(0,0,0,0.1);
        }

        .chat-message {
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 0.5rem;
            max-width: 80%;
        }

        .user-message {
            background-color: var(--primary);
            color: white;
            margin-left: auto;
            border-bottom-right-radius: 4px;
        }

        .bot-message {
            background-color: var(--secondary);
            border-bottom-left-radius: 4px;
        }

        .feature-card {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin: 1rem 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border-top: 3px solid var(--primary);
        }

        .feature-icon {
            font-size: 2rem;
            margin-bottom: 1rem;
            color: var(--primary);
        }

        /* Perbaikan untuk tampilan mobile */
        @media (max-width: 768px) {
            .judul-aplikasi {
                font-size: 1.8rem;
            }
            .feature-card {
                padding: 1rem;
            }
        }
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
if "cap" not in st.session_state:
    st.session_state.cap = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# === Model Deteksi Wajah ===
try:
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
except Exception as e:
    st.error(f"Error loading face detection model: {str(e)}")
    st.stop()


# === Fungsi Bantuan ===
def stop_camera():
    if st.session_state.cap is not None:
        st.session_state.cap.release()
        st.session_state.cap = None


def save_detection_result(nama, usia, gender, gejala_list, screenshot):
    waktu = datetime.datetime.now()
    tanggal_pemeriksaan = datetime.date.today()

    saran = ""
    if "Bercak Kuning" in gejala_list:
        saran += "- Gunakan salep antijamur/antibiotik ringan\n"
    if "Ruam / Kemerahan" in gejala_list:
        saran += "- Gunakan krim anti-inflamasi (hidrokortison)\n"
    if "Wajah Pucat" in gejala_list:
        saran += "- Periksa darah, konsumsi makanan bergizi\n"
    if "Jerawat" in gejala_list:
        saran += "- Obat jerawat: benzoyl peroxide/salicylic acid\n"

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

    nama_file = f"riwayat_{nome.replace(' ', '_')}.csv"

    try:
        if os.path.exists(nama_file):
            df = pd.read_csv(nama_file)

            # Konversi kolom waktu ke datetime
            df['Waktu_combined'] = pd.to_datetime(df['Tanggal'] + ' ' + df['Waktu'])

            # Pastikan semua datetime naive (tanpa timezone)
            waktu = waktu.replace(tzinfo=None)
            df['Waktu_combined'] = df['Waktu_combined'].dt.tz_localize(None)

            # Cek apakah ada entri yang sama dalam 5 menit terakhir
            mask = (df['Nama'] == nome) & \
                   (df['Gejala'] == ", ".join(gejala_list)) & \
                   ((waktu - df['Waktu_combined']).dt.total_seconds() < 300)

            if not df[mask].empty:
                return saran

            df = pd.concat([df, pd.DataFrame([hasil])], ignore_index=True)
        else:
            df = pd.DataFrame([hasil])

        df.to_csv(nama_file, index=False)
    except Exception as e:
        st.error(f"Gagal menyimpan riwayat: {str(e)}")

    return saran


# === Menu Navigasi ===
selected = option_menu(
    menu_title=None,
    options=["Beranda", "Pemeriksaan", "Riwayat", "Tentang"],
    icons=["house-heart", "camera", "clock-history", "info-circle"],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "white",
                      "box-shadow": "0 4px 12px rgba(0,0,0,0.1)"},
        "icon": {"color": "#4a8bfc", "font-size": "16px"},
        "nav-link": {"font-size": "16px", "text-align": "left", "margin": "0px", "--hover-color": "#f0f7ff"},
        "nav-link-selected": {"background-color": "#4a8bfc", "font-weight": "normal"},
    }
)

# === Halaman Beranda ===
if selected == "Beranda":
    st.markdown("""
        <div class='judul-aplikasi'>SkinScan</div>
        <p style='text-align:center; font-size: 1.1rem; color: #555; margin-bottom: 2rem;'>
            Deteksi cerdas untuk kesehatan kulit wajah Anda
        </p>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)



    st.markdown("""
        <div style='text-align: center; margin-top: 2rem;'>
            <p style='font-size: 0.9rem; color: #777;'>
                © 2025 SkinScan Pro | Kelompok 1 | Dermatologi Digital
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.info("🎯 Silakan buka menu **Pemeriksaan** dan isi data diri terlebih dahulu untuk memulai deteksi.")

# === Halaman Riwayat ===
elif selected == "Riwayat":
    st.title("📋 Riwayat Pemeriksaan")
    st.markdown("""
        <p style='color: #555; margin-bottom: 1.5rem;'>
            Tinjau hasil pemeriksaan sebelumnya dan pantau perkembangan kesehatan kulit Anda
        </p>
    """, unsafe_allow_html=True)

    nome_pengguna = st.sidebar.text_input("🔍 Masukkan Nama Anda untuk melihat riwayat:", key="riwayat_nome")

    if nome_pengguna:
        nome_file = f"riwayat_{nome_pengguna.replace(' ', '_')}.csv"
        if os.path.exists(nome_file):
            try:
                df = pd.read_csv(nome_file)

                # Konversi kolom waktu dengan penanganan timezone yang benar
                df['Waktu_combined'] = pd.to_datetime(df['Tanggal'] + ' ' + df['Waktu'])
                df['Waktu_combined'] = df['Waktu_combined'].dt.tz_localize(None)  # Pastikan semua naive

                # Urutkan berdasarkan waktu terbaru
                df = df.sort_values('Waktu_combined', ascending=False)

                # Hapus duplikat berdasarkan gejala dan tanggal
                df = df.drop_duplicates(subset=['Gejala', 'Tanggal'], keep='first')

                if not df.empty:
                    # Tampilkan maksimal 10 riwayat terbaru
                    for index, row in df.head(10).iterrows():
                        with st.container():
                            st.markdown(f"""
                                <div class='history-card'>
                                    <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
                                        <h4 style='margin: 0; color: var(--primary);'>👤 {row['Nama']}</h4>
                                        <span style='font-size: 0.9rem; color: #666;'>{row['Tanggal']} {row['Waktu']}</span>
                                    </div>
                                    <div style='display: flex; gap: 1rem; margin-bottom: 0.5rem;'>
                                        <span style='background: #e3f2fd; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8rem;'>Usia: {row['Usia']}</span>
                                        <span style='background: #e8f5e9; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8rem;'>Jenis Kelamin: {row['Jenis Kelamin']}</span>
                                    </div>
                                    <p style='margin-bottom: 0.5rem;'><strong>Gejala:</strong> {row['Gejala']}</p>
                                    <p style='margin-bottom: 0;'><strong>Saran Obat:</strong> {row['Hasil Saran Obat']}</p>
                                </div>
                            """, unsafe_allow_html=True)

                            # === Tambahan Edukasi ===
                            with st.expander("📚 Informasi Tambahan tentang Gejala"):
                                gejala_str = str(row['Gejala']).lower()

                                if "jerawat" in gejala_str:
                                    st.info("""
                                    **Jerawat**  
                                    Biasanya muncul karena pori-pori tersumbat oleh minyak berlebih, sel kulit mati, dan bakteri. 
                                    Faktor lain seperti hormon, stres, makanan berminyak, serta kebiasaan menyentuh wajah juga bisa memperparah.
                                    """)
                                if "ruam" in gejala_str or "kemerahan" in gejala_str:
                                    st.info("""
                                    **Ruam/Kemerahan**  
                                    Di wajah bisa muncul karena alergi, iritasi produk, infeksi, atau kondisi kulit seperti eksim. 
                                    Gejalanya biasanya berupa kemerahan, gatal, atau bintik-bintik.
                                    """)
                                if "pucat" in gejala_str:
                                    st.info("""
                                    **Wajah pucat**  
                                    Biasanya terjadi karena aliran darah ke kulit berkurang. Penyebabnya bisa karena kelelahan, 
                                    kurang tidur, kurang darah (anemia), stres, atau cuaca dingin.
                                    """)
                                if "bercak kuning" in gejala_str:
                                    st.info("""
                                    **Bercak kuning**  
                                    Di wajah bisa muncul karena penumpukan minyak, sel kulit mati, atau infeksi ringan seperti jamur. 
                                    Kadang juga muncul akibat gangguan kulit seperti seborrheic dermatitis.
                                    """)

                            if os.path.exists(row['Gambar']):
                                st.image(row['Gambar'], width=300, caption="Gambar Hasil Pemeriksaan")

                    st.markdown(
                        f"<p style='text-align: right; color: #666;'>Menampilkan {min(len(df), 10)} dari {len(df)} riwayat</p>",
                        unsafe_allow_html=True)

                    if len(df) > 10:
                        if st.button("Tampilkan Lebih Banyak Riwayat"):
                            for index, row in df[10:].iterrows():
                                with st.container():
                                    st.markdown(f"""
                                        <div class='history-card'>
                                            <div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;'>
                                                <h4 style='margin: 0; color: var(--primary);'>👤 {row['Nama']}</h4>
                                                <span style='font-size: 0.9rem; color: #666;'>{row['Tanggal']} {row['Waktu']}</span>
                                            </div>
                                            <div style='display: flex; gap: 1rem; margin-bottom: 0.5rem;'>
                                                <span style='background: #e3f2fd; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8rem;'>Usia: {row['Usia']}</span>
                                                <span style='background: #e8f5e9; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.8rem;'>Jenis Kelamin: {row['Jenis Kelamin']}</span>
                                            </div>
                                            <p style='margin-bottom: 0.5rem;'><strong>Gejala:</strong> {row['Gejala']}</p>
                                            <p style='margin-bottom: 0;'><strong>Saran Obat:</strong> {row['Hasil Saran Obat']}</p>
                                        </div>
                                    """, unsafe_allow_html=True)

                                    # === Tambahan Edukasi untuk riwayat tambahan ===
                                    with st.expander("📚 Informasi Tambahan tentang Gejala", key=f"expander_{index}"):
                                        gejala_str = str(row['Gejala']).lower()

                                        if "jerawat" in gejala_str:
                                            st.info("""
                                            **Jerawat**  
                                            Biasanya muncul karena pori-pori tersumbat oleh minyak berlebih, sel kulit mati, dan bakteri. 
                                            Faktor lain seperti hormon, stres, makanan berminyak, serta kebiasaan menyentuh wajah juga bisa memperparah.
                                            """)
                                        if "ruam" in gejala_str or "kemerahan" in gejala_str:
                                            st.info("""
                                            **Ruam/Kemerahan**  
                                            Di wajah bisa muncul karena alergi, iritasi produk, infeksi, atau kondisi kulit seperti eksim. 
                                            Gejalanya biasanya berupa kemerahan, gatal, atau bintik-bintik.
                                            """)
                                        if "pucat" in gejala_str:
                                            st.info("""
                                            **Wajah pucat**  
                                            Biasanya terjadi karena aliran darah ke kulit berkurang. Penyebabnya bisa karena kelelahan, 
                                            kurang tidur, kurang darah (anemia), stres, atau cuaca dingin.
                                            """)
                                        if "bercak kuning" in gejala_str:
                                            st.info("""
                                            **Bercak kuning**  
                                            Di wajah bisa muncul karena penumpukan minyak, sel kulit mati, atau infeksi ringan seperti jamur. 
                                            Kadang juga muncul akibat gangguan kulit seperti seborrheic dermatitis.
                                            """)

                                    if os.path.exists(row['Gambar']):
                                        st.image(row['Gambar'], width=300, caption="Gambar Hasil Pemeriksaan")
                else:
                    st.info("📭 Riwayat Anda masih kosong.")

                with open(nome_file, "rb") as file:
                    st.download_button(
                        "💾 Unduh Riwayat Saya (.CSV)",
                        file,
                        file_name=f"riwayat_{nome_pengguna}.csv",
                        mime="text/csv",
                        help="Unduh seluruh riwayat pemeriksaan Anda dalam format CSV"
                    )
            except Exception as e:
                st.error(f"Gagal memuat riwayat: {str(e)}")
        else:
            st.warning("⚠️ Riwayat belum ditemukan untuk nama tersebut.")
    else:
        st.info("🔍 Masukkan nama Anda untuk melihat riwayat pemeriksaan.")

# === Halaman Tentang ===
elif selected == "Tentang":
    st.title("Tentang SkinScan")
    st.markdown("""
        <div style='background-color: white; border-radius: 12px; padding: 2rem; margin-bottom: 2rem;'>
            <h3 style='color: var(--primary);'>Selamat datang di SkinScan</h3>
            Solusi cerdas untuk memantau kesehatan kulit Anda secara cepat dan praktis.
            Kami adalah tim pengembang yang peduli terhadap kesehatan dan kecantikan kulit, serta berkomitmen menghadirkan teknologi terkini dalam bidang deteksi dini penyakit kulit melalui kamera dan kecerdasan buatan.
            Aplikasi SkinScan dirancang untuk membantu pengguna mendeteksi berbagai permasalahan kulit wajah, seperti jerawat, ruam, bercak kuning, atau tanda-tanda wajah pucat yang dapat mengindikasikan kondisi kesehatan tertentu.
            Dengan dukungan analisis visual berbasis AI dan tampilan yang user-friendly, kami ingin memberikan kemudahan bagi siapa saja untuk lebih memahami kondisi kulit mereka, kapan pun dan di mana pun.
            Kami percaya bahwa deteksi dini adalah langkah pertama menuju perawatan yang tepat. Karena itu, SkinScan terus dikembangkan dan diperbarui untuk memberikan hasil analisis yang lebih akurat dan saran yang lebih tepat sesuai kebutuhan Anda.
            Terima kasih telah mempercayakan perawatan kulit Anda bersama SkinScan.
            Kami selalu terbuka untuk saran dan masukan demi pengembangan aplikasi yang lebih baik di masa depan.
        </div> """, unsafe_allow_html=True)

    (st.markdown
     ("""
        <div style='background-color: #f8f9fa; border-radius: 12px; padding: 2rem; margin-bottom: 2rem; border-left: 4px solid var(--primary);'>
            <h4 style='margin-top: 0;'>Disclaimer Penting</h4>
            <p style='margin-bottom: 0;'>
                Aplikasi ini bukan pengganti konsultasi dengan tenaga medis profesional. Hasil deteksi bersifat 
                informatif dan tidak dapat dijadikan sebagai diagnosis medis. Selalu konsultasikan dengan dokter 
                spesialis kulit untuk pemeriksaan lebih lanjut.
            </p>
        </div>
    """, unsafe_allow_html=True))

    st.markdown("---")
    st.subheader("💬 Tanya Jawab Seputar Kulit Wajah")

    with st.chat_message("assistant", avatar="🧑‍⚕️"):
        st.markdown(
            "Halo! Saya SkinBot, asisten virtual SkinScan. Saya siap membantu menjawab pertanyaan Anda seputar kesehatan kulit wajah.")

    user_input = st.chat_input("Tulis pertanyaan Anda...")

    if user_input:
        st.session_state.chat_history.append(("user", user_input))
        jawaban = "Maaf, saya belum mengerti pertanyaan Anda. Coba tanyakan hal lain seputar kesehatan kulit wajah ya!"

        if "jerawat" in user_input.lower():
            jawaban = """
            **Tentang Jerawat:**  
            Jerawat bisa disebabkan oleh beberapa faktor:
            - Perubahan hormon
            - Produksi minyak berlebih
            - Penumpukan sel kulit mati
            - Bakteri P. acnes  

            **Penanganan:**  
            - Cuci muka 2x sehari dengan pembersih lembut
            - Gunakan produk non-komedogenik
            - Hindari memencet jerawat
            - Untuk jerawat ringan, bisa gunakan produk dengan benzoyl peroxide 2.5% atau salicylic acid
            """
        elif "pucat" in user_input.lower():
            jawaban = """
            **Wajah Pucat:**  
            Bisa menandakan beberapa kondisi:
            - Kekurangan zat besi (anemia)
            - Tekanan darah rendah
            - Kurang paparan sinar matahari  

            **Saran:**  
            - Konsumsi makanan kaya zat besi (daging, bayam, kacang-kacangan)
            - Periksa kadar hemoglobin
            - Pastikan tidur cukup dan hidrasi terpenuhi
            """
        elif "ruam" in user_input.lower() or "kemerahan" in user_input.lower():
            jawaban = """
            **Ruam/Kemerahan di Wajah:**  
            Penyebab umum:
            - Alergi produk skincare/makeup
            - Iritasi (kontak dengan bahan kimia)
            - Eksim atau dermatitis  

            **Penanganan Awal:**  
            - Hentikan penggunaan produk baru
            - Kompres dingin untuk mengurangi kemerahan
            - Gunakan pelembab hypoallergenic
            - Hindari menggaruk area yang terkena
            """
        elif "obat" in user_input.lower():
            jawaban = """
            **Rekomendasi Obat:**  
            1. Untuk jerawat ringan:  
               - Benzoyl peroxide 2.5-5%  
               - Salicylic acid 0.5-2%  
            2. Untuk kemerahan/iritasi:  
               - Krim hidrokortison 1% (jangka pendek)  
               - Pelembab mengandung ceramide  
            3. Untuk bercak kuning:  
               - Salep antijamur (jika disebabkan jamur)  
               - Antibiotik topikal (jika infeksi bakteri)  

            *Konsultasikan dengan dokter sebelum menggunakan obat-obatan.*
            """
        elif "bercak" in user_input.lower():
            jawaban = """
            **Bercak Kuning di Wajah:**  
            Kemungkinan penyebab:
            - Infeksi jamur ringan (tinea versicolor)
            - Penumpukan sebum/minyak
            - Reaksi terhadap produk tertentu  

            **Saran:**  
            - Jaga kebersihan wajah
            - Gunakan pembersih lembut
            - Jika menetap >2 minggu, periksakan ke dokter kulit
            """

        st.session_state.chat_history.append(("bot", jawaban))

    for role, msg in st.session_state.chat_history:
        if role == "user":
            with st.chat_message("user", avatar="👤"):
                st.markdown(msg)
        else:
            with st.chat_message("assistant", avatar="🧑‍⚕️"):
                st.markdown(msg)

# === Halaman Pemeriksaan ===
elif selected == "Pemeriksaan":
    st.title("🔍 Pemeriksaan Kulit Wajah")
    st.markdown("""
        <p style='color: #555; margin-bottom: 1.5rem;'>
            Lakukan pemeriksaan kulit wajah menggunakan kamera perangkat Anda. Pastikan pencahayaan cukup 
            dan wajah terlihat jelas.
        </p>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("""
            <div style='background-color: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
                <h3 style='margin-top: 0; color: var(--primary);'>🧑‍⚕️ Data Pasien</h3>
        """, unsafe_allow_html=True)

        nome = st.text_input("Nama Lengkap", "", key="pemeriksaan_nome")
        idade = st.number_input("Usia", min_value=1, max_value=120, value=20, key="pemeriksaan_usia")
        genero = st.selectbox("Jenis Kelamin", ["Laki-laki", "Perempuan"], key="pemeriksaan_gender")
        data_pemeriksaan = datetime.date.today()

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
            <div style='background-color: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
                <h3 style='margin-top: 0; color: var(--primary);'>⚙️ Pengaturan Deteksi</h3>
        """, unsafe_allow_html=True)

        deteksi_ruam = st.checkbox("Deteksi Ruam / Kemerahan", value=True, key="deteksi_ruam")
        deteksi_bercak = st.checkbox("Deteksi Bercak Kuning", value=True, key="deteksi_bercak")
        deteksi_jerawat = st.checkbox("Deteksi Jerawat", value=True, key="deteksi_jerawat")

        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("""
            <div style='background-color: white; border-radius: 12px; padding: 1.5rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
                <h3 style='margin-top: 0; color: var(--primary);'>🎚️ Sensitivitas</h3>
        """, unsafe_allow_html=True)

        sensitivitas_ruam = st.slider("Sensitivitas Ruam", 100, 2000, 500, step=50, key="sens_ruam")
        sensitivitas_bercak = st.slider("Sensitivitas Bercak", 50, 1500, 300, step=50, key="sens_bercak")
        sensitivitas_jerawat = st.slider("Sensitivitas Jerawat", 30, 500, 120, step=10, key="sens_jerawat")

        st.markdown("</div>", unsafe_allow_html=True)

    if not nome:
        st.warning("⚠️ Mohon lengkapi data diri Anda terlebih dahulu di sidebar sebelum memulai pemeriksaan.")
        st.stop()

    # Container untuk tombol aksi
    with st.container():
        col1, col2, col3 = st.columns([1, 1, 2])
        with col1:
            start_btn = st.button("🎥 Mulai Kamera", key="start_btn", help="Aktifkan kamera untuk memulai pemeriksaan")
        with col2:
            stop_btn = st.button("⏹️ Stop Kamera", key="stop_btn", help="Matikan kamera", on_click=stop_camera)

    # Placeholder untuk tampilan kamera dan hasil
    frame_placeholder = st.empty()
    saran_obat_placeholder = st.empty()
    result_placeholder = st.empty()

    # State untuk menyimpan hasil terakhir
    if "last_detection" not in st.session_state:
        st.session_state.last_detection = None
    if "last_detection_time" not in st.session_state:
        st.session_state.last_detection_time = None


    def deteksi_gejala_di_wajah(frame, deteksi_ruam, deteksi_bercak, deteksi_jerawat,
                                sensitivitas_ruam, sensitivitas_bercak, sensitivitas_jerawat):
        gejala = {
            "Bercak Kuning": False,
            "Ruam / Kemerahan": False,
            "Wajah Pucat": False,
            "Jerawat": False
        }

        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))

            if len(faces) == 0:
                return frame, gejala

            for (x, y, w, h) in faces:
                x, y, w, h = int(x), int(y), int(w), int(h)
                if x < 0: x = 0
                if y < 0: y = 0
                if x + w > frame.shape[1]: w = frame.shape[1] - x
                if y + h > frame.shape[0]: h = frame.shape[0] - y

                wajah = frame[y:y + h, x:x + w]

                if wajah.size == 0:
                    continue

                hsv = cv2.cvtColor(wajah, cv2.COLOR_BGR2HSV)
                h_channel, s_channel, v_channel = cv2.split(hsv)

                # Deteksi Bercak Kuning
                if deteksi_bercak:
                    kuning_lower = np.array([20, 100, 100])
                    kuning_upper = np.array([35, 255, 255])
                    kuning_mask = cv2.inRange(hsv, kuning_lower, kuning_upper)
                    kuning_pixels = cv2.countNonZero(kuning_mask)
                    if kuning_pixels > sensitivitas_bercak:
                        gejala["Bercak Kuning"] = True
                        cv2.putText(frame, "Bercak Kuning", (x, max(10, y - 10)),
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

                # Deteksi Ruam/Kemerahan
                if deteksi_ruam:
                    merah_lower1 = np.array([0, 70, 50])
                    merah_upper1 = np.array([10, 255, 255])
                    merah_lower2 = np.array([170, 70, 50])
                    merah_upper2 = np.array([180, 255, 255])
                    merah_mask1 = cv2.inRange(hsv, merah_lower1, merah_upper1)
                    merah_mask2 = cv2.inRange(hsv, merah_lower2, merah_upper2)
                    merah_mask = cv2.bitwise_or(merah_mask1, merah_mask2)
                    merah_pixels = cv2.countNonZero(merah_mask)
                    if merah_pixels > sensitivitas_ruam:
                        gejala["Ruam / Kemerahan"] = True
                        text_position = (x, y + h + 20)
                        cv2.putText(frame, "Ruam", text_position,
                                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)

                # Deteksi Jerawat
                if deteksi_jerawat:
                    contours, _ = cv2.findContours(merah_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    jerawat_count = 0
                    for cnt in contours:
                        area = cv2.contourArea(cnt)
                        if 30 < area < sensitivitas_jerawat:
                            jerawat_count += 1
                            x1, y1, w1, h1 = cv2.boundingRect(cnt)
                            x1, y1, w1, h1 = int(x1), int(y1), int(w1), int(h1)
                            cv2.rectangle(wajah, (x1, y1), (x1 + w1, y1 + h1), (255, 0, 255), 1)
                            cv2.putText(wajah, "Jerawat", (x1, max(5, y1 - 5)),
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 0, 255), 1)
                    if jerawat_count > 3:
                        gejala["Jerawat"] = True

                # Deteksi Wajah Pucat
                if np.mean(s_channel) < 40:
                    gejala["Wajah Pucat"] = True
                    cv2.putText(frame, "Pucat", (x, y + h + 40),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 2)

                # Gambar persegi panjang di wajah
                cv2.rectangle(frame, (x, y), (x + w, y + h), (100, 255, 100), 2)

        except Exception as e:
            st.error(f"Error dalam deteksi wajah: {str(e)}")
            import traceback
            st.error(traceback.format_exc())

        return frame, gejala


    if start_btn:
        # Tampilkan data pasien dalam card
        with st.expander("📋 Data Pemeriksaan Pasien", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"""
                    <div style='background-color: #f0f7ff; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;'>
                        <p style='margin: 0; font-weight: bold;'>Nama Lengkap</p>
                        <p style='margin: 0;'>{nome}</p>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                    <div style='background-color: #f0f7ff; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;'>
                        <p style='margin: 0; font-weight: bold;'>Usia</p>
                        <p style='margin: 0;'>{idade} tahun</p>
                    </div>
                """, unsafe_allow_html=True)

            with col2:
                st.markdown(f"""
                    <div style='background-color: #f0f7ff; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;'>
                        <p style='margin: 0; font-weight: bold;'>Jenis Kelamin</p>
                        <p style='margin: 0;'>{genero}</p>
                    </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                    <div style='background-color: #f0f7ff; border-radius: 8px; padding: 1rem; margin-bottom: 1rem;'>
                        <p style='margin: 0; font-weight: bold;'>Tanggal Pemeriksaan</p>
                        <p style='margin: 0;'>{data_pemeriksaan.strftime('%d %B %Y')}</p>
                    </div>
                """, unsafe_allow_html=True)

        try:
            st.session_state.cap = cv2.VideoCapture(0)
            if not st.session_state.cap.isOpened():
                st.error("⚠️ Gagal membuka kamera. Pastikan kamera tersedia dan diizinkan.")
                st.stop()
        except Exception as e:
            st.error(f"Error membuka kamera: {str(e)}")
            st.stop()

        while st.session_state.cap.isOpened():
            ret, frame = st.session_state.cap.read()
            if not ret:
                st.error("⚠️ Gagal mengambil frame dari kamera.")
                break

            frame = cv2.flip(frame, 1)
            frame, gejala = deteksi_gejala_di_wajah(frame, deteksi_ruam, deteksi_bercak, deteksi_jerawat,
                                                    sensitivitas_ruam, sensitivitas_bercak, sensitivitas_jerawat)
            tempo = datetime.datetime.now()

            gejala_list = [g for g, detected in gejala.items() if detected]
            gejala_terdeteksi = any(gejala.values())

            # Hanya proses jika wajah terdeteksi
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5, minSize=(100, 100))

            if len(faces) > 0:
                frame_placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB",
                                        use_container_width=True, caption="Tampilan Kamera Real-time")

                # Jika ada gejala terdeteksi dan belum pernah disimpan atau sudah lebih dari 5 detik sejak deteksi terakhir
                if gejala_terdeteksi and (st.session_state.last_detection_time is None or
                                          (tempo - st.session_state.last_detection_time).total_seconds() > 5):

                    timestamp = tempo.strftime("%Y%m%d_%H%M%S")
                    screenshot = f"screenshots/deteksi_{timestamp}.jpg"
                    try:
                        cv2.imwrite(screenshot, frame)
                        st.session_state.last_detection_time = tempo
                        st.session_state.last_detection = {
                            "frame": frame,
                            "gejala_list": gejala_list,
                            "screenshot": screenshot
                        }

                        # Tampilkan hasil deteksi
                        result_placeholder.empty()  # Kosongkan placeholder hasil sebelumnya
                        with result_placeholder.container():
                            st.success("✅ Gejala Terdeteksi")

                            gejala_text = "\n".join([f"- {gejala}" for gejala in gejala_list])

                            st.markdown(f"""
                                <div style='background-color: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; box-shadow: 0 2px 8px rgba(0,0,0,0.05);'>
                                    <h4 style='margin-top: 0; color: var(--primary);'>📌 Hasil Deteksi</h4>
                                    <div style='display: flex; gap: 1rem;'>
                                        <div style='flex: 1;'>
                                            <img src='data:image/jpeg;base64,{base64.b64encode(cv2.imencode('.jpg', frame)[1]).decode()}' width='100%' style='border-radius: 8px;' />
                                        </div>
                                        <div style='flex: 1;'>
                                            <p style='font-weight: bold;'>Gejala yang terdeteksi:</p>
                                            {gejala_text or "Tidak ada gejala terdeteksi"}
                                        </div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)

                            saran = save_detection_result(nome, idade, genero, gejala_list, screenshot)

                            # Tampilkan saran obat
                            with saran_obat_placeholder.container():
                                if gejala_list:
                                    st.markdown(f"""
                                        <div style='background-color: #fff8e1; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; border-left: 4px solid #ffc107;'>
                                            <h4 style='margin-top: 0; color: #ff9800;'>💊 Saran Obat</h4>
                                            {saran.replace('<br>', '<br>')}
                                        </div>
                                    """, unsafe_allow_html=True)
                                else:
                                    st.markdown("""
                                        <div style='background-color: #e8f5e9; border-radius: 12px; padding: 1.5rem; border-left: 4px solid #4caf50;'>
                                            <h4 style='margin-top: 0; color: #2e7d32;'>ℹ️ Status</h4>
                                            <p style='margin-bottom: 0;'>Tidak ada gejala terdeteksi. Posisikan wajah dengan baik di depan kamera.</p>
                                        </div>
                                    """, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Gagal menyimpan hasil deteksi: {str(e)}")
                elif not gejala_terdeteksi:
                    with saran_obat_placeholder.container():
                        st.markdown("""
                            <div style='background-color: #e8f5e9; border-radius: 12px; padding: 1.5rem; border-left: 4px solid #4caf50;'>
                                <h4 style='margin-top: 0; color: #2e7d32;'>ℹ️ Status</h4>
                                <p style='margin-bottom: 0;'>Tidak ada gejala terdeteksi. Posisikan wajah dengan baik di depan kamera.</p>
                            </div>
                        """, unsafe_allow_html=True)
            else:
                frame_placeholder.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), channels="RGB",
                                        use_container_width=True, caption="Tidak ada wajah terdeteksi")
                with saran_obat_placeholder.container():
                    st.warning("⚠️ Wajah tidak terdeteksi. Pastikan wajah Anda terlihat jelas di depan kamera.")

            if stop_btn:
                stop_camera()
                st.info("🛑 Pemeriksaan dihentikan. Anda dapat memulai kembali kapan saja.")
                break

    elif stop_btn:
        st.info("🛑 Kamera belum diaktifkan. Tekan tombol 'Mulai Kamera' untuk memulai pemeriksaan")