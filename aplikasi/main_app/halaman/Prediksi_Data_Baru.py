import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils import muat_info, muat_model, muat_tabel, angka, LABEL_PREDIKTOR, WARNA_STATUS, STATUS_BAWAH
from tampilan import hero, kartu, badge_status, grafik_selisih, tentukan_status, rapikan, WARNA_UTAMA, WARNA_REDUP

info = muat_info()
model = muat_model("tuning")
tabel = muat_tabel()
ambang = info["ambang_status"]
rentang = info["rentang_prediktor"]
kolom = info["kolom_prediktor"]
INDIKATOR_PERSEN = ["PPM", "TPAK", "TPT"]
KUNCI = {k: f"masukan_{k}" for k in kolom + ["IPM"]}

hero("Prediksi Data Baru",
     "Masukkan lima indikator, dapatkan perkiraan IPM. Data yang dimasukkan tidak disimpan.",
     label="Coba sendiri", gambar_nama="header_prediksi_baru")

# Isi awal kotak masukan (kosong)
for kunci in KUNCI.values():
    st.session_state.setdefault(kunci, None)


def isi_contoh():
    """Isi dengan median data penelitian tahun terakhir, supaya mudah dicoba."""
    terakhir = tabel[tabel["Tahun"] == tabel["Tahun"].max()]
    for k in kolom:
        st.session_state[KUNCI[k]] = round(float(terakhir[k].median()), 2)
    st.session_state[KUNCI["IPM"]] = round(float(terakhir["IPM"].median()), 2)


def kosongkan():
    for kunci in KUNCI.values():
        st.session_state[kunci] = None


# ---------- Form masukan ----------
b1, b2, _ = st.columns([1, 1, 3])
b1.button("Isi contoh", icon=":material/auto_fix_high:", on_click=isi_contoh, width="stretch",
          help="Nilai tengah (median) data tahun terakhir.")
b2.button("Kosongkan", icon=":material/restart_alt:", on_click=kosongkan, width="stretch")

with st.form("form_data_baru", border=True):
    st.markdown("**Indikator sosial-ekonomi**")
    kiri, kanan = st.columns(2)
    nilai = {}
    for i, k in enumerate(kolom):
        tempat = kiri if i % 2 == 0 else kanan
        nilai[k] = tempat.number_input(
            LABEL_PREDIKTOR[k],
            min_value=0.0,
            max_value=100.0 if k in INDIKATOR_PERSEN else None,
            step=0.01, format="%.2f", placeholder="Isi nilai", key=KUNCI[k],
            help=f"Rentang data: {angka(rentang[k]['min'])} – {angka(rentang[k]['max'])}",
        )
    ipm_aktual = kanan.number_input("IPM aktual (opsional)", min_value=0.0, max_value=100.0,
                                    step=0.01, format="%.2f", key=KUNCI["IPM"],
                                    placeholder="Kosongkan jika tidak ada",
                                    help="Isi untuk melihat selisih dan status.")
    kirim = st.form_submit_button("Hitung IPM prediksi", type="primary", icon=":material/calculate:")

# ---------- Hasil ----------
def tampilkan_hasil():
    if not kirim:
        st.info("Isi nilai indikator lalu tekan **Hitung IPM prediksi**.", icon=":material/arrow_upward:")
        return

    kosong = [LABEL_PREDIKTOR[k] for k in kolom if nilai[k] is None]
    if kosong:
        st.error("Isi semua indikator terlebih dahulu: " + ", ".join(kosong) + ".", icon=":material/error:")
        return

    data_baru = pd.DataFrame([nilai], columns=kolom)
    ipm_prediksi = float(model.predict(data_baru)[0])

    st.subheader("Hasil")
    if ipm_aktual is None:
        kiri, kanan = st.columns([1, 2])
        with kiri:
            kartu("IPM prediksi", angka(ipm_prediksi), "Isi IPM aktual untuk melihat statusnya.")
    else:
        selisih = ipm_aktual - ipm_prediksi
        status = tentukan_status(selisih, ambang)
        k1, k2, k3 = st.columns(3)
        with k1:
            kartu("IPM aktual", angka(ipm_aktual), "Nilai yang dimasukkan")
        with k2:
            kartu("IPM prediksi", angka(ipm_prediksi), "Perkiraan model")
        with k3:
            kartu("Selisih", ("+" if selisih > 0 else "") + angka(selisih), status, WARNA_STATUS[status])
        badge_status(status)
        st.plotly_chart(grafik_selisih(selisih, ambang), width="stretch", config={"displayModeBar": False})

    # ---------- Cek rentang ----------
    st.subheader("Apakah nilai masih dalam rentang data?")
    cek = pd.DataFrame({
        "Indikator": [LABEL_PREDIKTOR[k] for k in kolom],
        "Nilai input": [nilai[k] for k in kolom],
        "Minimum data": [rentang[k]["min"] for k in kolom],
        "Maksimum data": [rentang[k]["max"] for k in kolom],
    })
    cek["Keterangan"] = ["Dalam rentang" if mn <= v <= mx else "Di luar rentang"
                         for v, mn, mx in zip(cek["Nilai input"], cek["Minimum data"], cek["Maksimum data"])]

    jumlah_luar = int((cek["Keterangan"] == "Di luar rentang").sum())
    if jumlah_luar > 0:
        st.warning(f"{jumlah_luar} nilai di luar rentang data, jadi hasilnya kurang dapat diandalkan.",
                   icon=":material/warning:")
    else:
        st.success("Semua nilai dalam rentang data.", icon=":material/check_circle:")

    # Posisi setiap nilai pada skala 0 (minimum data) sampai 1 (maksimum data)
    posisi = ((cek["Nilai input"] - cek["Minimum data"]) / (cek["Maksimum data"] - cek["Minimum data"])).clip(-0.08, 1.08)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=[1] * len(cek), y=cek["Indikator"], orientation="h", marker_color=WARNA_REDUP,
                         width=0.25, hoverinfo="skip", showlegend=False))
    fig.add_trace(go.Scatter(
        x=posisi, y=cek["Indikator"], mode="markers",
        marker=dict(size=16, symbol="diamond", line=dict(color="white", width=2),
                    color=[WARNA_UTAMA if k == "Dalam rentang" else WARNA_STATUS[STATUS_BAWAH] for k in cek["Keterangan"]]),
        customdata=cek[["Nilai input", "Minimum data", "Maksimum data"]],
        hovertemplate="%{y}<br>Masukan %{customdata[0]:,.2f}<br>Rentang %{customdata[1]:,.2f} – %{customdata[2]:,.2f}<extra></extra>",
        showlegend=False,
    ))
    fig.update_xaxes(range=[-0.1, 1.1], tickvals=[0, 1], ticktext=["Minimum data", "Maksimum data"], showgrid=False)
    fig.update_yaxes(autorange="reversed", title=None)
    st.plotly_chart(rapikan(fig, tinggi=280, legenda=False), width="stretch", config={"displayModeBar": False})

    st.dataframe(cek.style.format(precision=2, decimal=",", thousands="."), hide_index=True, width="stretch")


tampilkan_hasil()
