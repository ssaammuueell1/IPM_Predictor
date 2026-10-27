from pathlib import Path
import json

import pandas as pd
import streamlit as st
from xgboost import XGBRegressor

# Lokasi folder, dihitung dari letak file utils.py ini
FOLDER_APP = Path(__file__).parent
FOLDER_DATA = FOLDER_APP / "data"
FOLDER_MODEL = FOLDER_APP / "model"

# Nama status (harus sama persis dengan isi kolom Status di tabel_prediksi.csv)
STATUS_ATAS = "Di atas prediksi"
STATUS_SESUAI = "Sesuai prediksi"
STATUS_BAWAH = "Di bawah prediksi"
URUTAN_STATUS = [STATUS_ATAS, STATUS_SESUAI, STATUS_BAWAH]
WARNA_STATUS = {STATUS_ATAS: "#0F766E", STATUS_SESUAI: "#6B7280", STATUS_BAWAH: "#C0392B"}

@st.cache_data
def muat_tabel():
    """Tabel IPM prediksi (prediksi silang) untuk 1.026 baris."""
    return pd.read_csv(FOLDER_DATA / "tabel_prediksi.csv")


@st.cache_data
def muat_info():
    """Info model: jumlah data, parameter, metrik, ambang, rentang prediktor, kontribusi fitur."""
    with open(FOLDER_MODEL / "info_model.json", encoding="utf-8") as f:
        return json.load(f)


@st.cache_data
def muat_peta():
    """Batas wilayah kabupaten/kota dalam format GeoJSON (sumber: geoBoundaries, CC BY 4.0)."""
    with open(FOLDER_DATA / "batas_kabkota.geojson", encoding="utf-8") as f:
        return json.load(f)

@st.cache_resource
def muat_model(nama="tuning"):
    """Model final. nama = 'tuning' atau 'awal'."""
    model = XGBRegressor()
    model.load_model(str(FOLDER_MODEL / f"model_{nama}.json"))
    return model
    # Alternatif format joblib (butuh joblib + scikit-learn di requirements.txt):
    # import joblib
    # return joblib.load(FOLDER_MODEL / f"model_{nama}.joblib")


def angka(x, desimal=2):
    """Format angka gaya Indonesia: 1234.5 -> '1.234,50'."""
    teks = f"{x:,.{desimal}f}"
    return teks.replace(",", "#").replace(".", ",").replace("#", ".")


# Nama lengkap dan satuan setiap prediktor (dipakai halaman Prediksi Data Tersedia dan Data Baru)
LABEL_PREDIKTOR = {
    "PPM": "Persentase penduduk miskin (%)",
    "TPAK": "Tingkat partisipasi angkatan kerja (%)",
    "TPT": "Tingkat pengangguran terbuka (%)",
    "PDRB": "PDRB per kapita ADHK (ribu Rp)",
    "KP": "Kepadatan penduduk (jiwa/km²)",
}