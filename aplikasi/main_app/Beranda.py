import plotly.express as px
import streamlit as st

from utils import muat_info, muat_tabel, angka, URUTAN_STATUS, WARNA_STATUS, STATUS_ATAS, STATUS_SESUAI, STATUS_BAWAH
from tampilan import pasang_gaya, hero, kartu, kartu_status, rapikan

st.set_page_config(page_title="Prediksi IPM Wilayah Kemiskinan Tinggi", page_icon="📊", layout="wide")
pasang_gaya()


def beranda():
    info = muat_info()
    tabel = muat_tabel()
    jumlah = info["jumlah"]
    ambang = angka(info["ambang_status"])
    silang = info["metrik_prediksi_silang"]["tuning"]

    # ---------- Judul dan tujuan ----------
    hero(
        "Prediksi IPM di Wilayah dengan Kemiskinan Tinggi di Indonesia",
        "Aplikasi ini membandingkan IPM aktual setiap kabupaten/kota dengan <b>IPM prediksi</b>, yaitu IPM "
        "yang diperkirakan model XGBoost dari kondisi sosial-ekonomi daerah tersebut: persentase penduduk "
        "miskin, TPAK, TPT, PDRB per kapita, dan kepadatan penduduk.",
    )

    # ---------- Cakupan data ----------
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Kabupaten/Kota", jumlah["daerah"], border=True, icon=":material/location_city:")
    k2.metric("Provinsi", tabel["Provinsi"].nunique(), border=True, icon=":material/map:")
    k3.metric("Periode", f"{jumlah['tahun_awal']}–{jumlah['tahun_akhir']}", border=True,
              icon=":material/calendar_month:")
    k4.metric("Jumlah data", f"{angka(jumlah['baris'], 0)} baris", border=True, icon=":material/dataset:")
    st.caption(
        "Cakupan: kabupaten/kota dengan persentase penduduk miskin di atas 15% selama tiga tahun "
        "berturut-turut (2018–2020), mengikuti kriteria wilayah dengan kemiskinan tinggi Bappenas."
    )

    # ---------- Cara membaca hasil ----------
    st.subheader("Cara membaca hasil")
    st.markdown(
        f"**Selisih = IPM aktual − IPM prediksi.** Batas **±{ambang}** adalah MAE prediksi silang, "
        f"yaitu rata-rata kesalahan model pada daerah yang belum pernah dilihatnya."
    )
    arti = {
        STATUS_ATAS: f"Selisih lebih dari +{ambang}. Capaian IPM lebih tinggi daripada daerah lain dengan kondisi serupa.",
        STATUS_SESUAI: f"Selisih antara −{ambang} dan +{ambang}. Masih dalam batas kesalahan rata-rata model.",
        STATUS_BAWAH: f"Selisih kurang dari −{ambang}. Capaian IPM lebih rendah daripada daerah lain dengan kondisi serupa.",
    }
    jumlah_status = tabel["Status"].value_counts()
    for kolom, status in zip(st.columns(3), URUTAN_STATUS):
        with kolom:
            kartu(status, f"{angka(jumlah_status.get(status, 0), 0)} baris", arti[status], WARNA_STATUS[status])

    # ---------- Komposisi status per tahun ----------
    st.subheader("Komposisi status per tahun")
    komposisi = tabel.groupby(["Tahun", "Status"]).size().reset_index(name="Jumlah daerah")
    fig = px.bar(komposisi, x="Tahun", y="Jumlah daerah", color="Status", color_discrete_map=WARNA_STATUS,
                 category_orders={"Status": URUTAN_STATUS}, text="Jumlah daerah")
    fig.update_traces(textposition="inside", textfont_color="white")
    fig.update_xaxes(dtick=1, title=None)
    st.plotly_chart(rapikan(fig, tinggi=340), width="stretch")

    # ---------- Navigasi ----------
    st.subheader("Jelajahi aplikasi")
    halaman = [
        ("halaman/Daftar_wilayah.py", ":material/table_view:", "Daftar Wilayah",
         "Tabel seluruh daerah dengan pencarian dan filter provinsi, tahun, dan status."),
        ("halaman/Prediksi_Data_Tersedia.py", ":material/query_stats:", "Prediksi Data Tersedia",
         f"Detail satu daerah pada satu tahun beserta tren {jumlah['tahun_awal']}–{jumlah['tahun_akhir']}."),
        ("halaman/Prediksi_Data_Baru.py", ":material/edit_note:", "Prediksi Data Baru",
         "Masukkan nilai lima indikator untuk mendapatkan IPM prediksi."),
        ("halaman/Evaluasi_Model.py", ":material/analytics:", "Evaluasi Model",
         f"Kinerja model (R² prediksi silang {angka(silang['R2'], 3)}) dan kontribusi setiap indikator."),
    ]
    for kolom, (file, ikon, judul, desk) in zip(st.columns(4), halaman):
        with kolom.container(border=True, height="stretch"):
            st.markdown(f"**{judul}**")
            st.caption(desk)
            st.page_link(file, label="Buka halaman", icon=ikon)

    # ---------- Batasan ----------
    with st.expander("Batasan penggunaan", icon=":material/info:"):
        st.markdown(
            "- IPM prediksi **bukan ramalan** IPM tahun depan.\n"
            "- Hasil **tidak menunjukkan hubungan sebab-akibat** antara indikator dan IPM.\n"
            "- Model hanya andal untuk nilai indikator yang berada dalam rentang data penelitian."
        )


# ---------- Navigasi antarhalaman (menu di bagian atas) ----------
navigasi = st.navigation([
    st.Page(beranda, title="Beranda", icon=":material/home:", default=True),
    st.Page("halaman/Daftar_wilayah.py", title="Daftar Wilayah", icon=":material/table_view:"),
    st.Page("halaman/Prediksi_Data_Tersedia.py", title="Prediksi Data Tersedia", icon=":material/query_stats:"),
    st.Page("halaman/Prediksi_Data_Baru.py", title="Prediksi Data Baru", icon=":material/edit_note:"),
    st.Page("halaman/Evaluasi_Model.py", title="Evaluasi Model", icon=":material/analytics:"),
], position="top")

navigasi.run()

# ---------- Keterangan di bagian bawah setiap halaman ----------
_info = muat_info()
st.divider()
st.caption(
    f"Model: XGBoost dengan tuning · Batas status: ±{angka(_info['ambang_status'])} · "
    f"Data: {_info['jumlah']['daerah']} kab/kota, {_info['jumlah']['tahun_awal']}–{_info['jumlah']['tahun_akhir']}"
)
