import plotly.express as px
import streamlit as st

from utils import muat_info, muat_tabel, angka, URUTAN_STATUS, WARNA_STATUS, STATUS_ATAS, STATUS_SESUAI, STATUS_BAWAH
from tampilan import hero, gambar, kartu, rapikan

info = muat_info()
tabel = muat_tabel()
jumlah = info["jumlah"]
ambang = angka(info["ambang_status"])

hero("Tentang aplikasi",
     "Cara kerja aplikasi, cara membaca hasil, dan batasannya.",
     label="Tentang", gambar_nama="header_tentang")

# ---------- Apa yang dilakukan aplikasi ini ----------
kiri, kanan = st.columns([3, 2], gap="large", vertical_alignment="center")
with kiri:
    st.subheader("Apa yang dilakukan aplikasi ini?")
    st.markdown(
        "Model **XGBoost** memperkirakan IPM setiap kabupaten/kota dari lima indikator: persentase penduduk miskin, "
        "Tingkat Partisipasi Angkatan Kerja, Tingkat Pengangguran Terbuka, Produk Domestik Regional Bruto (PDRB) per kapita, dan kepadatan penduduk.\n\n"
        "Perkiraan ini disebut **IPM prediksi**. Dengan membandingkannya dengan IPM aktual, kita bisa melihat "
        "daerah mana yang capaiannya lebih tinggi atau lebih rendah daripada daerah lain dengan kondisi serupa."
    )
with kanan:
    gambar("tentang_ilustrasi", tinggi=230, saran="900 × 600 px")

# ---------- Cakupan data ----------
st.subheader("Data yang dipakai")
k1, k2, k3, k4 = st.columns(4)
k1.metric("Kabupaten/Kota", jumlah["daerah"], border=True, icon=":material/location_city:")
k2.metric("Provinsi", tabel["Provinsi"].nunique(), border=True, icon=":material/map:")
k3.metric("Periode", f"{jumlah['tahun_awal']}–{jumlah['tahun_akhir']}", border=True, icon=":material/calendar_month:")
k4.metric("Jumlah data", f"{angka(jumlah['baris'], 0)} baris", border=True, icon=":material/dataset:")
st.caption("Daerah dengan penduduk miskin di atas 15% selama 2018-2020 (kriteria wilayah kemiskinan tinggi Bappenas).")

# ---------- Cara membaca hasil ----------
st.subheader("Cara membaca hasil")
st.markdown(f"**Selisih = IPM aktual - IPM prediksi.** Batas ±{ambang} adalah rata-rata kesalahan model.")
arti = {
    STATUS_ATAS: f"Selisih lebih dari +{ambang}. IPM lebih tinggi dari daerah serupa.",
    STATUS_SESUAI: f"Selisih antara -{ambang} dan +{ambang}. Sesuai perkiraan.",
    STATUS_BAWAH: f"Selisih kurang dari -{ambang}. IPM lebih rendah dari daerah serupa.",
}
jumlah_status = tabel["Status"].value_counts()
for kolom, status in zip(st.columns(3), URUTAN_STATUS):
    with kolom:
        kartu(status, f"{angka(jumlah_status.get(status, 0), 0)} baris", arti[status], WARNA_STATUS[status])

# ---------- Komposisi status per tahun ----------
st.subheader("Status per tahun")
komposisi = tabel.groupby(["Tahun", "Status"]).size().reset_index(name="Jumlah daerah")
fig = px.bar(komposisi, x="Tahun", y="Jumlah daerah", color="Status", color_discrete_map=WARNA_STATUS,
             category_orders={"Status": URUTAN_STATUS}, text="Jumlah daerah")
fig.update_traces(textposition="inside", textfont_color="white")
fig.update_xaxes(dtick=1, title=None)
st.plotly_chart(rapikan(fig, tinggi=340), width="stretch")

# ---------- Batasan ----------
st.subheader("Batasan")
st.markdown(
    "- IPM prediksi **bukan ramalan** IPM tahun depan.\n"
    "- Hasilnya **bukan hubungan sebab-akibat**.\n"
    "- Model hanya andal untuk nilai indikator di dalam rentang data penelitian."
)
