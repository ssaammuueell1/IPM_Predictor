import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils import muat_info, muat_tabel, angka, LABEL_PREDIKTOR, WARNA_STATUS, URUTAN_STATUS, STATUS_BAWAH
from tampilan import hero, rapikan, WARNA_UTAMA, WARNA_SEKUNDER, WARNA_REDUP

info = muat_info()
tabel = muat_tabel()
METRIK = ["MAE", "RMSE", "R²"]
FORMAT_METRIK = dict(precision=3, decimal=",", thousands=".")
WARNA_MODEL = {"Baseline": WARNA_REDUP, "Tanpa tuning": WARNA_SEKUNDER, "Dengan tuning": WARNA_UTAMA}

hero("Evaluasi Model",
     "Kinerja model diukur dengan MAE, RMSE, dan R² melalui dua cara: data uji (pembagian 80/20 per "
     "kabupaten/kota) dan validasi silang GroupKFold 5 fold.")

with st.expander("Arti metrik", icon=":material/help:"):
    st.markdown(
        "- **MAE**: rata-rata besar kesalahan prediksi dalam poin IPM. Makin kecil makin baik.\n"
        "- **RMSE**: mirip MAE, tetapi kesalahan besar dihukum lebih berat. Makin kecil makin baik.\n"
        "- **R²**: proporsi keragaman IPM yang dapat dijelaskan model. Nilai 1 berarti sempurna, "
        "nilai 0 atau kurang berarti tidak lebih baik daripada menebak rata-rata.\n"
        "- **Baseline**: tebakan paling sederhana, yaitu selalu menebak rata-rata IPM data latih."
    )

# ---------- Ringkasan utama ----------
terbaik = info["metrik_uji"]["Dengan tuning"]
baseline = info["metrik_uji"]["Baseline"]
silang = info["metrik_prediksi_silang"]["tuning"]
k1, k2, k3, k4 = st.columns(4)
k1.metric("R² data uji", angka(terbaik["R2"], 3), border=True,
          delta=f"+{angka(terbaik['R2'] - baseline['R2'], 3)} dari baseline")
k2.metric("MAE data uji", angka(terbaik["MAE"], 3), border=True, delta_color="inverse",
          delta=f"{angka(terbaik['MAE'] - baseline['MAE'], 3)} dari baseline")
k3.metric("R² prediksi silang", angka(silang["R2"], 3), border=True,
          help=f"Gabungan prediksi semua {info['jumlah']['daerah']} daerah dari 5 fold.")
k4.metric("MAE prediksi silang", angka(silang["MAE"], 3), border=True,
          help="Dipakai sebagai batas status di seluruh aplikasi.")

tab_uji, tab_fold, tab_sebar, tab_prov, tab_fitur, tab_param = st.tabs([
    ":material/fact_check: Data uji", ":material/view_week: Validasi silang", ":material/scatter_plot: Aktual vs prediksi",
    ":material/map: Per provinsi", ":material/bar_chart: Kontribusi indikator", ":material/settings: Parameter",
])

# ---------- 1. Data uji ----------
with tab_uji:
    uji = pd.DataFrame(info["metrik_uji"]).T.rename(columns={"R2": "R²"})
    uji.index.name = "Model"
    panjang = uji.reset_index().melt(id_vars="Model", var_name="Metrik", value_name="Nilai")

    kiri, kanan = st.columns([3, 2])
    fig = px.bar(panjang[panjang["Metrik"] != "R²"], x="Metrik", y="Nilai", color="Model", barmode="group",
                 color_discrete_map=WARNA_MODEL, text_auto=".2f")
    fig.update_yaxes(title="Poin IPM")
    fig.update_xaxes(title=None)
    kiri.plotly_chart(rapikan(fig, tinggi=340), width="stretch")

    fig_r2 = px.bar(panjang[panjang["Metrik"] == "R²"], x="Model", y="Nilai", color="Model",
                    color_discrete_map=WARNA_MODEL, text_auto=".3f")
    fig_r2.update_traces(textposition="outside")
    fig_r2.update_yaxes(title="R²", range=[min(0, uji["R²"].min()) - 0.12, 1.05])
    fig_r2.update_xaxes(title=None)
    kanan.plotly_chart(rapikan(fig_r2, tinggi=340, legenda=False), width="stretch")

    st.dataframe(uji.reset_index().style.format(subset=METRIK, **FORMAT_METRIK), hide_index=True, width="stretch")
    st.caption("Data uji: 20% kabupaten/kota yang tidak dipakai saat melatih model.")

# ---------- 2. Validasi silang ----------
with tab_fold:
    st.write(
        f"Seluruh {info['jumlah']['daerah']} daerah dibagi menjadi 5 kelompok. Setiap kelompok bergiliran "
        f"menjadi data validasi, sehingga setiap daerah diprediksi oleh model yang tidak pernah melihatnya."
    )
    semua_fold = pd.concat([pd.DataFrame(info["tabel_fold"][n]).assign(Model=label)
                            for n, label in [("awal", "Tanpa tuning"), ("tuning", "Dengan tuning")]])
    pilih = st.segmented_control("Metrik per fold", ["R2", "MAE", "RMSE"], default="R2",
                                 format_func=lambda m: "R²" if m == "R2" else m)
    pilih = pilih or "R2"
    fig = px.bar(semua_fold, x="Fold", y=pilih, color="Model", barmode="group", color_discrete_map=WARNA_MODEL,
                 text_auto=".3f", labels={"R2": "R²"})
    fig.update_xaxes(dtick=1)
    st.plotly_chart(rapikan(fig, tinggi=340), width="stretch")

    tab_tuning, tab_awal = st.tabs(["Dengan tuning", "Tanpa tuning"])
    for tab, nama in [(tab_tuning, "tuning"), (tab_awal, "awal")]:
        with tab:
            fold = pd.DataFrame(info["tabel_fold"][nama]).rename(columns={"R2": "R²"})
            ringkas = (fold[METRIK].agg(["mean", "std"])
                       .rename(index={"mean": "Rata-rata", "std": "Simpangan baku"}))
            kiri, kanan = st.columns([3, 2])
            kiri.dataframe(fold.style.format(subset=METRIK, **FORMAT_METRIK), hide_index=True, width="stretch")
            kanan.dataframe(ringkas.style.format(**FORMAT_METRIK), width="stretch")

            hasil_silang = info["metrik_prediksi_silang"][nama]
            c1, c2, c3 = st.columns(3)
            c1.metric("MAE prediksi silang", angka(hasil_silang["MAE"], 3), border=True)
            c2.metric("RMSE prediksi silang", angka(hasil_silang["RMSE"], 3), border=True)
            c3.metric("R² prediksi silang", angka(hasil_silang["R2"], 3), border=True)
    st.caption(
        f"MAE prediksi silang model dengan tuning (±{angka(info['ambang_status'])}) "
        f"dipakai sebagai batas status di seluruh aplikasi."
    )

# ---------- 3. Grafik aktual vs prediksi ----------
with tab_sebar:
    fig = px.scatter(tabel, x="IPM", y="IPM_prediksi", color="Status", color_discrete_map=WARNA_STATUS,
                     category_orders={"Status": URUTAN_STATUS},
                     hover_data=["Kabupaten/Kota", "Provinsi", "Tahun"], opacity=0.7,
                     labels={"IPM": "IPM aktual", "IPM_prediksi": "IPM prediksi"})
    garis = [tabel[["IPM", "IPM_prediksi"]].min().min(), tabel[["IPM", "IPM_prediksi"]].max().max()]
    fig.add_trace(go.Scatter(x=garis, y=garis, mode="lines", name="Prediksi tepat (y = x)",
                             line=dict(color="gray", dash="dash")))
    st.plotly_chart(rapikan(fig, tinggi=500), width="stretch")
    st.caption("Makin dekat titik ke garis putus-putus, makin tepat prediksinya.")

# ---------- 4. MAE per provinsi ----------
with tab_prov:
    mae_provinsi = (tabel.assign(Galat=tabel["Selisih"].abs())
                    .groupby("Provinsi")
                    .agg(MAE=("Galat", "mean"), Daerah=("Kabupaten/Kota", "nunique"))
                    .sort_values("MAE")
                    .reset_index())
    mae_total = info["metrik_prediksi_silang"]["tuning"]["MAE"]
    mae_provinsi["Posisi"] = ["Di atas MAE keseluruhan" if m > mae_total else "Di bawah MAE keseluruhan"
                              for m in mae_provinsi["MAE"]]
    fig2 = px.bar(mae_provinsi, x="MAE", y="Provinsi", orientation="h", text_auto=".2f", hover_data=["Daerah"],
                  color="Posisi", color_discrete_map={"Di atas MAE keseluruhan": WARNA_STATUS[STATUS_BAWAH],
                                                      "Di bawah MAE keseluruhan": WARNA_UTAMA})
    fig2.add_vline(x=mae_total, line_dash="dash", line_color="gray", annotation_text="MAE keseluruhan")
    fig2.update_yaxes(title=None)
    st.plotly_chart(rapikan(fig2, tinggi=40 + 28 * len(mae_provinsi), legenda=False), width="stretch")
    st.caption("Merah: MAE provinsi di atas MAE keseluruhan. Provinsi dengan sedikit daerah (lihat jumlah "
               "daerah saat di-hover) memiliki MAE yang kurang stabil.")

# ---------- 5. Kontribusi fitur ----------
with tab_fitur:
    kontribusi = pd.Series(info["kontribusi_fitur"]).rename(index=LABEL_PREDIKTOR).sort_values()
    fig3 = px.bar(x=kontribusi.values, y=kontribusi.index, orientation="h", text_auto=".1f",
                  labels={"x": "Kontribusi (%)", "y": ""}, color_discrete_sequence=[WARNA_UTAMA])
    st.plotly_chart(rapikan(fig3, tinggi=320, legenda=False), width="stretch")
    st.caption(
        "Kontribusi dihitung dari total gain: seberapa besar setiap indikator mengurangi kesalahan model "
        "saat dipakai untuk membelah data. Nilai ini tidak menunjukkan arah pengaruh maupun hubungan sebab-akibat."
    )

# ---------- 6. Parameter ----------
with tab_param:
    param = pd.DataFrame(info["param"]).rename(columns={"tuning": "Dengan tuning", "awal": "Tanpa tuning"})
    param.index.name = "Parameter"
    st.dataframe(param.reset_index(), hide_index=True, width="stretch")
    st.caption("Parameter lain sama untuk kedua model: reg_lambda = 1, reg_alpha = 0, gamma = 0, tree_method = exact.")
