import math

import plotly.graph_objects as go
import streamlit as st

from utils import muat_tabel, muat_info, muat_peta, angka
from tampilan import hero, transparan

tabel = muat_tabel()
info = muat_info()
peta = muat_peta()
ambang = info["ambang_status"]
jumlah = info["jumlah"]
SEMUA = "Seluruh Indonesia"

hero("Prediksi IPM di Wilayah dengan",
     "Membandingkan IPM aktual tiap kabupaten/kota dengan IPM yang diperkirakan model XGBoost "
     "dari kondisi sosial-ekonominya.",
     aksen="Kemiskinan Tinggi di Indonesia", gambar_nama="header_beranda", besar=True,
     chip=[f"{jumlah['daerah']} kabupaten/kota", f"{tabel['Provinsi'].nunique()} provinsi",
           f"{jumlah['tahun_awal']}–{jumlah['tahun_akhir']}",
           f"R² {angka(info['metrik_prediksi_silang']['tuning']['R2'], 2)}"])

# ---------- Pilihan ----------
PILIHAN = {
    # Skala dimulai dari warna muda (bukan abu-abu) supaya tidak tertukar dengan daerah di luar cakupan
    "IPM aktual": {"kolom": "IPM", "skala": [[0, "#CDE8E4"], [1, "#0F766E"]],
                   "arti": "Makin gelap (teal) = IPM makin tinggi."},
    "Penduduk miskin (%)": {"kolom": "PPM", "skala": [[0, "#F5D5CF"], [1, "#C0392B"]],
                            "arti": "Makin merah = makin banyak penduduk miskin."},
    "Selisih IPM": {"kolom": "Selisih", "skala": [[0, "#C0392B"], [0.5, "#C4CAD3"], [1, "#0F766E"]],
                    "arti": "Teal = IPM di atas prediksi, merah = di bawah prediksi."},
}
with st.container(border=True):
    k1, k2, k3 = st.columns([3, 2, 2])
    pilihan = k1.segmented_control("Warnai peta berdasarkan", list(PILIHAN), default="Selisih IPM")
    pilihan = pilihan or "Selisih IPM"
    wilayah = k2.selectbox("Wilayah", [SEMUA] + sorted(tabel["Provinsi"].unique()))
    daftar_tahun = sorted(tabel["Tahun"].unique())
    tahun = k3.select_slider("Tahun", options=daftar_tahun, value=daftar_tahun[-1])

atur = PILIHAN[pilihan]
data_tahun = tabel[tabel["Tahun"] == tahun]

# Batas skala warna dihitung dari seluruh 114 daerah, supaya warna antarprovinsi bisa dibandingkan
if atur["kolom"] == "Selisih":
    batas = max(data_tahun["Selisih"].abs().max(), ambang)
    zmin, zmax = -batas, batas
else:
    zmin, zmax = data_tahun[atur["kolom"]].min(), data_tahun[atur["kolom"]].max()

if wilayah == SEMUA:
    data = data_tahun
    fokus = peta["features"]
else:
    data = data_tahun[data_tahun["Provinsi"] == wilayah]
    fokus = [f for f in peta["features"] if f["properties"]["provinsi"] == wilayah]

id_fokus = {f["id"] for f in fokus}
luar = [f["id"] for f in fokus if not f["properties"]["cakupan"]]
latar = [f["id"] for f in peta["features"] if f["id"] not in id_fokus]


def posisi_peta(fitur, lebar=1100, tinggi=480):
    """Titik tengah dan tingkat zoom supaya semua daerah dalam `fitur` terlihat."""
    barat = min(f["bbox"][0] for f in fitur)
    selatan = min(f["bbox"][1] for f in fitur)
    timur = max(f["bbox"][2] for f in fitur)
    utara = max(f["bbox"][3] for f in fitur)
    lebar_bujur = max(timur - barat, 0.3)
    tinggi_lintang = max(utara - selatan, 0.3)
    zoom = min(math.log2(lebar * 360 / (512 * lebar_bujur)),
               math.log2(tinggi * 360 / (512 * tinggi_lintang))) - 0.2
    return {"lat": (selatan + utara) / 2, "lon": (barat + timur) / 2}, min(zoom, 8)


tengah, zoom = posisi_peta(fokus)

# ---------- Peta ----------
# Warna transparan supaya daerah di luar cakupan tetap terlihat di mode terang maupun gelap
ABU = "#9CA3AF"
fig = go.Figure()
if latar:
    fig.add_trace(go.Choroplethmap(
        geojson=peta, locations=latar, z=[0] * len(latar),
        colorscale=[[0, transparan(ABU, 0.08)], [1, transparan(ABU, 0.08)]], showscale=False,
        marker_line_color=transparan(ABU, 0.30), marker_line_width=0.3, hoverinfo="skip",
    ))
fig.add_trace(go.Choroplethmap(
    geojson=peta, locations=luar, z=[0] * len(luar),
    colorscale=[[0, transparan(ABU, 0.14)], [1, transparan(ABU, 0.14)]], showscale=False,
    marker_line_color=transparan(ABU, 0.45), marker_line_width=0.4, hoverinfo="skip",
))
fig.add_trace(go.Choroplethmap(
    geojson=peta, locations=data["Kabupaten/Kota"], z=data[atur["kolom"]],
    colorscale=atur["skala"], zmin=zmin, zmax=zmax,
    marker_line_color="rgba(255,255,255,0.6)", marker_line_width=0.6,
    customdata=data[["Provinsi", "IPM", "IPM_prediksi", "Selisih", "Status", "PPM"]],
    hovertemplate=("<b>%{location}</b> · %{customdata[0]}<br>"
                   "IPM aktual %{customdata[1]:.2f} · IPM prediksi %{customdata[2]:.2f}<br>"
                   "Selisih %{customdata[3]:+.2f} · %{customdata[4]}<br>"
                   "Penduduk miskin %{customdata[5]:.2f}%<extra></extra>"),
    colorbar=dict(title=dict(text=pilihan, side="top"), orientation="h", x=0.5, y=0.0,
                  len=0.5, thickness=12),
))
# Gaya peta kosong (tanpa latar putih), sehingga peta mengikuti warna latar halaman
PETA_TANPA_LATAR = {"version": 8, "sources": {}, "layers": []}
fig.update_layout(map=dict(style=PETA_TANPA_LATAR, center=tengah, zoom=zoom),
                  height=480, margin=dict(l=0, r=0, t=0, b=0), separators=",.")
with st.container(border=True):
    st.plotly_chart(fig, width="stretch", config={"scrollZoom": True, "displayModeBar": False})
st.caption(f"{atur['arti']} Abu-abu muda = di luar cakupan penelitian. Arahkan kursor ke daerah untuk rinciannya. "
           f"Batas wilayah: geoBoundaries (CC BY 4.0).")

# ---------- Lima tertinggi dan terendah ----------
kolom_tampil = ["Kabupaten/Kota", "Provinsi", atur["kolom"]]
urut = data.sort_values(atur["kolom"], ascending=False)[kolom_tampil].rename(columns={atur["kolom"]: pilihan})
n = min(5, len(urut))
kiri, kanan = st.columns(2)
kiri.markdown(f"**{n} tertinggi ({tahun})**")
kiri.dataframe(urut.head(n).style.format({pilihan: "{:.2f}"}, decimal=","), hide_index=True, width="stretch")
kanan.markdown(f"**{n} terendah ({tahun})**")
kanan.dataframe(urut.tail(n).iloc[::-1].style.format({pilihan: "{:.2f}"}, decimal=","), hide_index=True, width="stretch")