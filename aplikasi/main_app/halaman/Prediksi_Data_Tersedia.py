import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import muat_tabel, muat_info, angka, WARNA_STATUS, LABEL_PREDIKTOR
from tampilan import hero, badge_status, grafik_selisih, rapikan, WARNA_UTAMA, WARNA_SEKUNDER

tabel = muat_tabel()
info = muat_info()
ambang = info["ambang_status"]
jumlah_daerah = info["jumlah"]["daerah"]

hero("Prediksi Data Tersedia",
     "Lihat IPM satu daerah: aktual, prediksi, dan selisihnya dari tahun ke tahun.",
     label="Per daerah", gambar_nama="header_prediksi_tersedia")

# ---------- Pilihan daerah dan tahun ----------
with st.container(border=True):
    p1, p2 = st.columns(2)
    provinsi = p1.selectbox("Provinsi", sorted(tabel["Provinsi"].unique()))
    daftar_daerah = sorted(tabel.loc[tabel["Provinsi"] == provinsi, "Kabupaten/Kota"].unique())
    daerah = p2.selectbox("Kabupaten/Kota", daftar_daerah)

    data_daerah = tabel[(tabel["Provinsi"] == provinsi) & (tabel["Kabupaten/Kota"] == daerah)].sort_values("Tahun")
    daftar_tahun = data_daerah["Tahun"].tolist()
    tahun = st.segmented_control("Tahun", daftar_tahun, default=daftar_tahun[-1])
    if tahun is None:                      # tombol tahun yang aktif diklik lagi -> kembali ke tahun terakhir
        tahun = daftar_tahun[-1]

baris = data_daerah[data_daerah["Tahun"] == tahun].iloc[0]
data_tahun = tabel[tabel["Tahun"] == tahun]
peringkat = int(data_tahun["IPM"].rank(ascending=False, method="min")[baris.name])

# ---------- Hasil ----------
judul, status_kolom = st.columns([3, 1], vertical_alignment="center")
judul.subheader(f"{daerah}, {provinsi} · {tahun}")
with status_kolom:
    badge_status(baris["Status"])

k1, k2, k3, k4 = st.columns(4)
k1.metric("IPM aktual", angka(baris["IPM"]), border=True)
k2.metric("IPM prediksi", angka(baris["IPM_prediksi"]), border=True)
k3.metric("Selisih", ("+" if baris["Selisih"] > 0 else "") + angka(baris["Selisih"]), border=True,
          help="Selisih = IPM aktual − IPM prediksi")
k4.metric("Peringkat IPM aktual", f"{peringkat} / {len(data_tahun)}", border=True,
          help="1 = IPM tertinggi pada tahun itu.")

st.plotly_chart(grafik_selisih(float(baris["Selisih"]), ambang), width="stretch",
                config={"displayModeBar": False})
st.caption(f"Diprediksi oleh model yang tidak pernah melihat data daerah ini (fold {baris['Fold']}).")

tab_tren, tab_indikator = st.tabs([":material/show_chart: Tren IPM", ":material/tune: Nilai indikator"])

# ---------- Grafik tren ----------
with tab_tren:
    tahun_x = data_daerah["Tahun"]
    prediksi = data_daerah["IPM_prediksi"]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=tahun_x, y=prediksi + ambang, mode="lines", line=dict(width=0),
                             showlegend=False, hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=tahun_x, y=prediksi - ambang, mode="lines", line=dict(width=0), fill="tonexty",
                             fillcolor="rgba(156,163,175,0.2)", name=f"Batas ±{angka(ambang)}", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=tahun_x, y=prediksi, mode="lines+markers", name="IPM prediksi",
                             line=dict(color=WARNA_SEKUNDER, dash="dash"),
                             hovertemplate="IPM prediksi %{y:.2f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=tahun_x, y=data_daerah["IPM"], mode="lines+markers", name="IPM aktual",
                             line=dict(color=WARNA_UTAMA, width=3),
                             marker=dict(size=11, color=[WARNA_STATUS[s] for s in data_daerah["Status"]],
                                         line=dict(color="white", width=2)),
                             customdata=data_daerah["Status"],
                             hovertemplate="IPM aktual %{y:.2f} · %{customdata}<extra></extra>"))
    fig.add_vline(x=tahun, line_dash="dot", line_color="gray")
    fig.update_layout(hovermode="x unified", yaxis_title="IPM")
    fig.update_xaxes(dtick=1)
    st.plotly_chart(rapikan(fig, tinggi=400), width="stretch")
    st.caption(f"Warna titik = status tiap tahun. Area abu-abu = batas ±{angka(ambang)}.")

# ---------- Posisi prediktor ----------
with tab_indikator:
    kolom = list(LABEL_PREDIKTOR)
    rata = data_tahun[kolom].mean()
    posisi = pd.DataFrame({
        "Indikator": list(LABEL_PREDIKTOR.values()),
        "Nilai daerah": [baris[k] for k in kolom],
        f"Rata-rata {jumlah_daerah} daerah ({tahun})": rata.values,
    })
    posisi["Beda dari rata-rata (%)"] = (posisi["Nilai daerah"] / posisi.iloc[:, 2] - 1) * 100

    fig2 = go.Figure(go.Bar(
        x=posisi["Beda dari rata-rata (%)"], y=posisi["Indikator"], orientation="h",
        marker_color=[WARNA_UTAMA if v >= 0 else WARNA_SEKUNDER for v in posisi["Beda dari rata-rata (%)"]],
        text=[("+" if v > 0 else "") + angka(v, 1) + "%" for v in posisi["Beda dari rata-rata (%)"]],
        textposition="outside", hovertemplate="%{y}: %{x:.1f}%<extra></extra>",
    ))
    fig2.add_vline(x=0, line_color="#9CA3AF")
    fig2.update_xaxes(title=f"Beda dari rata-rata {jumlah_daerah} daerah tahun {tahun} (%)", ticksuffix="%")
    fig2.update_yaxes(autorange="reversed", title=None)
    st.plotly_chart(rapikan(fig2, tinggi=300, legenda=False), width="stretch")

    st.dataframe(posisi.style.format(precision=2, decimal=",", thousands="."), hide_index=True, width="stretch")
    st.caption("Hanya menunjukkan posisi daerah, bukan penyebab selisih IPM.")
