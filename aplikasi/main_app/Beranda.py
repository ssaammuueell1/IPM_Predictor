import streamlit as st

from utils import muat_info, angka
from tampilan import pasang_gaya

st.set_page_config(page_title="Prediksi IPM Wilayah Kemiskinan Tinggi", page_icon="📊", layout="wide")
pasang_gaya()

# ---------- Navigasi antarhalaman (menu di bagian atas) ----------
# Halaman utama (Beranda) adalah peta persebaran; isi beranda lama sekarang ada di halaman Tentang.
navigasi = st.navigation([
    st.Page("halaman/Peta_Persebaran.py", title="Beranda", icon=":material/home:", default=True),
    st.Page("halaman/Daftar_wilayah.py", title="Daftar Wilayah", icon=":material/table_view:"),
    st.Page("halaman/Prediksi_Data_Tersedia.py", title="Prediksi Data Tersedia", icon=":material/query_stats:"),
    st.Page("halaman/Prediksi_Data_Baru.py", title="Prediksi Data Baru", icon=":material/edit_note:"),
    st.Page("halaman/Evaluasi_Model.py", title="Evaluasi Model", icon=":material/analytics:"),
    st.Page("halaman/Tentang.py", title="Tentang", icon=":material/info:"),
], position="top")

navigasi.run()

# ---------- Keterangan di bagian bawah setiap halaman ----------
_info = muat_info()
st.divider()
st.caption(
    f"Model: XGBoost dengan tuning · Batas status: ±{angka(_info['ambang_status'])} · "
    f"Data: {_info['jumlah']['daerah']} kab/kota, {_info['jumlah']['tahun_awal']}–{_info['jumlah']['tahun_akhir']}"
)
