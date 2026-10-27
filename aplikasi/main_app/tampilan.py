"""Komponen tampilan yang dipakai bersama oleh semua halaman (kepala halaman, gambar, kartu, grafik selisih)."""
from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from utils import angka, WARNA_STATUS, STATUS_ATAS, STATUS_SESUAI, STATUS_BAWAH

# Warna grafik dipilih supaya tetap terbaca di mode terang maupun gelap
WARNA_UTAMA = "#0F766E"      # satu-satunya warna aksen
WARNA_SEKUNDER = "#9CA3AF"   # abu-abu untuk pembanding
WARNA_REDUP = "#D1D5DB"      # abu-abu muda untuk latar/baseline
WARNA_GARIS = "#9CA3AF"

# Folder gambar. Simpan gambar dengan nama yang sama seperti di placeholder (format jpg, png, atau webp).
FOLDER_GAMBAR = Path(__file__).resolve().parent / "gambar"
EKSTENSI_GAMBAR = (".jpg", ".jpeg", ".png", ".webp", ".gif")


def transparan(warna_hex, alpha):
    """'#RRGGBB' -> 'rgba(r,g,b,alpha)'. Warna transparan menyatu dengan latar terang maupun gelap."""
    r, g, b = (int(warna_hex[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r},{g},{b},{alpha})"


# Warna latar lembut untuk setiap status (dipakai di tabel dan pita grafik)
LATAR_STATUS = {s: transparan(w, 0.16) for s, w in WARNA_STATUS.items()}
BADGE_STATUS = {STATUS_ATAS: "green", STATUS_SESUAI: "gray", STATUS_BAWAH: "red"}
IKON_STATUS = {STATUS_ATAS: ":material/trending_up:", STATUS_SESUAI: ":material/check_circle:",
               STATUS_BAWAH: ":material/trending_down:"}

CSS = """
<style>
/* Margin kiri-kanan yang wajar dan lebar isi maksimum */
[data-testid="stMainBlockContainer"], .block-container {
    padding: 4.2rem 2.5rem 2rem 2.5rem !important; max-width: 1480px;}
/* Kepala halaman: tanpa kotak, teks mengikuti warna tema */
.kepala {padding: .4rem 0 .2rem 0;}
.kepala-label {font-size: .78rem; letter-spacing: .1em; text-transform: uppercase; font-weight: 700;
               opacity: .6; margin-bottom: .4rem;}
.kepala-judul {font-size: 2.5rem; font-weight: 800; line-height: 1.15; letter-spacing: -.01em;}
.kepala-judul .aksen {color: #14918A;}   /* teal yang terbaca di mode terang dan gelap */
.kepala-judul.kecil {font-size: 2rem;}
.kepala-desk {margin-top: .7rem; font-size: 1.08rem; line-height: 1.55; opacity: .8; max-width: 42rem;}
.kepala-chip {display: flex; flex-wrap: wrap; gap: .5rem; margin-top: 1rem;}
.kepala-chip span {border: 1px solid rgba(120, 125, 135, .35); border-radius: 999px; padding: .25rem .8rem;
                   font-size: .88rem; font-weight: 600;}
.garis-kepala {border: none; border-top: 1px solid rgba(120, 125, 135, .28); margin: 1rem 0 1.4rem 0;}
/* Gambar dan tempat gambar */
[data-testid="stImage"] img {border-radius: 1rem; object-fit: cover;}
.tempat-gambar {border: 2px dashed rgba(120, 125, 135, .45); border-radius: 1rem; display: flex;
                flex-direction: column; align-items: center; justify-content: center; text-align: center;
                background: rgba(120, 125, 135, .06); padding: 1rem; gap: .3rem;}
.tempat-gambar b {font-size: .95rem;}
.tempat-gambar code {font-size: .8rem; white-space: normal; word-break: break-all;}
.tempat-gambar small {opacity: .65;}
/* Kartu memakai warna transparan dan warna teks bawaan tema, jadi cocok di mode terang dan gelap */
.kartu {background: rgba(120, 125, 135, .07); border: 1px solid rgba(120, 125, 135, .28);
        border-left: 6px solid var(--w); border-radius: .8rem; padding: .9rem 1.1rem;}
.kartu-label {font-size: .82rem; opacity: .72; font-weight: 600; text-transform: uppercase;
              letter-spacing: .04em;}
.kartu-angka {font-size: 1.85rem; font-weight: 700; color: var(--w); line-height: 1.25;}
.kartu-sub {font-size: .88rem; opacity: .85; line-height: 1.45;}
</style>
"""


def pasang_gaya():
    """Sisipkan CSS bersama. Dipanggil sekali di Beranda.py sebelum halaman dijalankan."""
    st.html(CSS)


def cari_gambar(nama):
    """Kembalikan path gambar gambar/<nama>.<ekstensi> jika ada, selain itu None."""
    for ekstensi in EKSTENSI_GAMBAR:
        path = FOLDER_GAMBAR / f"{nama}{ekstensi}"
        if path.exists():
            return path
    return None


def gambar(nama, tinggi=260, saran="1200 × 800 px"):
    """Tampilkan gambar/<nama>.jpg (atau .png/.webp). Jika belum ada, tampilkan kotak placeholder."""
    path = cari_gambar(nama)
    if path:
        st.image(str(path), width="stretch")
    else:
        st.markdown(
            f"<div class='tempat-gambar' style='height:{tinggi}px'>"
            f"<span style='font-size:1.8rem'>🖼️</span><b>Tempat gambar</b>"
            f"<code>gambar/{nama}.jpg</code><small>Saran ukuran {saran}</small></div>",
            unsafe_allow_html=True,
        )


def hero(judul, deskripsi, label="Prediksi IPM · XGBoost", gambar_nama=None, aksen="", chip=None, besar=False):
    """Kepala halaman tanpa kotak: label kecil, judul (bagian `aksen` berwarna), deskripsi, dan gambar di kanan."""
    teks_judul = judul + (f" <span class='aksen'>{aksen}</span>" if aksen else "")
    teks_chip = ("<div class='kepala-chip'>" + "".join(f"<span>{c}</span>" for c in chip) + "</div>") if chip else ""
    isi = (f"<div class='kepala'><div class='kepala-label'>{label}</div>"
           f"<div class='kepala-judul{'' if besar else ' kecil'}'>{teks_judul}</div>"
           f"<div class='kepala-desk'>{deskripsi}</div>{teks_chip}</div>")
    if gambar_nama:
        kiri, kanan = st.columns([3, 2] if besar else [2, 1], gap="large", vertical_alignment="center")
        kiri.markdown(isi, unsafe_allow_html=True)
        with kanan:
            gambar(gambar_nama, tinggi=280 if besar else 180, saran="1200 × 800 px" if besar else "900 × 500 px")
    else:
        st.markdown(isi, unsafe_allow_html=True)
    st.markdown("<hr class='garis-kepala'>", unsafe_allow_html=True)


def kartu(label, angka_utama, keterangan, warna=WARNA_UTAMA):
    """Kartu ringkas dengan garis warna di kiri."""
    st.markdown(
        f"<div class='kartu' style='--w:{warna}'><div class='kartu-label'>{label}</div>"
        f"<div class='kartu-angka'>{angka_utama}</div><div class='kartu-sub'>{keterangan}</div></div>",
        unsafe_allow_html=True,
    )


def kartu_status(status, jumlah, total):
    persen = jumlah / total * 100 if total else 0
    kartu(status, angka(jumlah, 0), f"{angka(persen, 1)}% dari {angka(total, 0)} baris", WARNA_STATUS[status])


def badge_status(status):
    st.badge(status, icon=IKON_STATUS[status], color=BADGE_STATUS[status])


def tentukan_status(selisih, ambang):
    if selisih > ambang:
        return STATUS_ATAS
    if selisih < -ambang:
        return STATUS_BAWAH
    return STATUS_SESUAI


def rapikan(fig, tinggi=380, legenda=True):
    """Gaya grafik Plotly yang seragam di semua halaman."""
    fig.update_layout(
        height=tinggi, margin=dict(l=10, r=10, t=30 if legenda else 10, b=10), separators=",.",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title=None),
        hoverlabel=dict(font_size=13), showlegend=legenda,
        uniformtext=dict(minsize=10, mode="hide"),     # sembunyikan label yang tidak muat di batang kecil
    )
    fig.update_traces(textangle=0, selector=dict(type="bar"))
    return fig


def grafik_selisih(selisih, ambang):
    """Pita horizontal: terakota (di bawah), abu hangat (sesuai), teal (di atas), dengan penanda posisi selisih."""
    batas = max(abs(selisih) + 1.5, ambang * 2.2)
    status = tentukan_status(selisih, ambang)
    fig = go.Figure()
    for x0, x1, s in [(-batas, -ambang, STATUS_BAWAH), (-ambang, ambang, STATUS_SESUAI), (ambang, batas, STATUS_ATAS)]:
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=0, y1=1, fillcolor=LATAR_STATUS[s], line_width=0, layer="below")
        fig.add_annotation(x=(x0 + x1) / 2, y=0.18, text=s, showarrow=False,
                           font=dict(size=11, color=WARNA_STATUS[s]))
    for x in (-ambang, ambang):
        fig.add_vline(x=x, line=dict(color=WARNA_GARIS, width=1, dash="dot"))
    fig.add_vline(x=0, line=dict(color=WARNA_GARIS, width=1))
    fig.add_trace(go.Scatter(
        x=[selisih], y=[0.6], mode="markers+text", text=[("+" if selisih > 0 else "") + angka(selisih)],
        textposition="top center", textfont=dict(size=14, color=WARNA_STATUS[status]),
        marker=dict(symbol="diamond", size=20, color=WARNA_STATUS[status], line=dict(color="white", width=2)),
        hovertemplate="Selisih %{x:.2f}<extra></extra>",
    ))
    fig.update_xaxes(range=[-batas, batas], zeroline=False, showgrid=False,
                     tickvals=[-ambang, 0, ambang], ticktext=[f"−{angka(ambang)}", "0", f"+{angka(ambang)}"])
    fig.update_yaxes(range=[0, 1.15], visible=False)
    return rapikan(fig, tinggi=150, legenda=False)
