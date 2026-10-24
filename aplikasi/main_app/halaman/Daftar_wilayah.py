import plotly.express as px
import streamlit as st

from utils import muat_tabel, muat_info, angka, URUTAN_STATUS, WARNA_STATUS, STATUS_ATAS, STATUS_BAWAH
from tampilan import hero, kartu_status, rapikan, LATAR_STATUS

tabel = muat_tabel()
info = muat_info()
ambang = angka(info["ambang_status"])

hero("Daftar Wilayah",
     "Tabel IPM aktual dan IPM prediksi seluruh kabupaten/kota. Kosongkan filter untuk menampilkan "
     "semua data. Klik judul kolom tabel untuk mengurutkan.")

# ---------- Filter ----------
with st.container(border=True):
    f1, f2, f3 = st.columns([2, 2, 1])
    cari = f1.text_input("Cari kabupaten/kota", placeholder="Contoh: Aceh Barat", icon=":material/search:")
    pilih_provinsi = f2.multiselect("Provinsi", sorted(tabel["Provinsi"].unique()), placeholder="Semua provinsi")
    pilih_tahun = f3.selectbox("Tahun", ["Semua tahun"] + sorted(tabel["Tahun"].unique(), reverse=True))
    pilih_status = st.pills("Status", URUTAN_STATUS, selection_mode="multi",
                            help="Kosongkan untuk menampilkan semua status.")

hasil = tabel
if cari:
    hasil = hasil[hasil["Kabupaten/Kota"].str.contains(cari, case=False, regex=False)]
if pilih_provinsi:
    hasil = hasil[hasil["Provinsi"].isin(pilih_provinsi)]
if pilih_tahun != "Semua tahun":
    hasil = hasil[hasil["Tahun"] == pilih_tahun]
if pilih_status:
    hasil = hasil[hasil["Status"].isin(pilih_status)]

# ---------- Ringkasan jumlah per status ----------
jumlah_status = hasil["Status"].value_counts()
for kolom, status in zip(st.columns(3), URUTAN_STATUS):
    with kolom:
        kartu_status(status, int(jumlah_status.get(status, 0)), len(hasil))
st.caption(f"Menampilkan {angka(len(hasil), 0)} dari {angka(len(tabel), 0)} baris · batas status ±{ambang}")

if hasil.empty:
    st.warning("Tidak ada data yang cocok dengan filter.", icon=":material/search_off:")
else:
    tab_tabel, tab_provinsi = st.tabs([":material/table_view: Tabel", ":material/bar_chart: Ringkasan per provinsi"])

    # ---------- Tabel ----------
    with tab_tabel:
        tampil = (hasil[["Kabupaten/Kota", "Provinsi", "Tahun", "IPM", "IPM_prediksi", "Selisih", "Status"]]
                  .rename(columns={"IPM": "IPM aktual", "IPM_prediksi": "IPM prediksi"})
                  .sort_values(["Tahun", "Kabupaten/Kota"], ascending=[False, True]))

        def warna_status(nilai):
            return (f"color: {WARNA_STATUS.get(nilai, 'inherit')}; background-color: {LATAR_STATUS.get(nilai, 'transparent')}; "
                    f"font-weight: 600")

        def warna_selisih(nilai):
            if nilai > info["ambang_status"]:
                return f"color: {WARNA_STATUS[STATUS_ATAS]}; font-weight: 600"
            if nilai < -info["ambang_status"]:
                return f"color: {WARNA_STATUS[STATUS_BAWAH]}; font-weight: 600"
            return ""

        gaya = (tampil.style
                .format({"IPM aktual": "{:.2f}", "IPM prediksi": "{:.2f}", "Selisih": "{:+.2f}"}, decimal=",")
                .map(warna_status, subset=["Status"])
                .map(warna_selisih, subset=["Selisih"]))

        st.dataframe(gaya, hide_index=True, width="stretch", height=520,
                     column_config={"Tahun": st.column_config.NumberColumn(format="%d")})

        st.download_button(
            "Unduh tabel (CSV)", tampil.to_csv(index=False, sep=";", decimal=",").encode("utf-8-sig"),
            file_name="daftar_wilayah_ipm.csv", mime="text/csv", icon=":material/download:",
            help="Pemisah titik koma dan desimal koma, sehingga langsung terbaca di Excel berbahasa Indonesia.",
        )

    # ---------- Ringkasan per provinsi ----------
    with tab_provinsi:
        per_prov = hasil.groupby(["Provinsi", "Status"]).size().reset_index(name="Jumlah")
        urutan = hasil["Provinsi"].value_counts().sort_values().index.tolist()
        fig = px.bar(per_prov, x="Jumlah", y="Provinsi", color="Status", orientation="h",
                     color_discrete_map=WARNA_STATUS,
                     category_orders={"Status": URUTAN_STATUS, "Provinsi": urutan[::-1]})
        fig.update_yaxes(title=None)
        fig.update_xaxes(title="Jumlah baris (daerah × tahun)")
        st.plotly_chart(rapikan(fig, tinggi=120 + 26 * len(urutan)), width="stretch")

        rata = (hasil.groupby("Provinsi")
                .agg(Daerah=("Kabupaten/Kota", "nunique"), Rata_IPM=("IPM", "mean"),
                     Rata_selisih=("Selisih", "mean"))
                .sort_values("Rata_selisih", ascending=False).reset_index()
                .rename(columns={"Rata_IPM": "Rata-rata IPM aktual", "Rata_selisih": "Rata-rata selisih"}))
        st.dataframe(rata.style.format({"Rata-rata IPM aktual": "{:.2f}", "Rata-rata selisih": "{:+.2f}"}, decimal=","),
                     hide_index=True, width="stretch")
        st.caption("Rata-rata selisih positif berarti daerah di provinsi itu cenderung memiliki IPM di atas prediksi.")
