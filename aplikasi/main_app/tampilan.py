"""Komponen tampilan yang dipakai bersama oleh semua halaman (header, kartu, grafik selisih)."""
import plotly.graph_objects as go
import streamlit as st

from utils import angka, WARNA_STATUS, STATUS_ATAS, STATUS_SESUAI, STATUS_BAWAH

WARNA_UTAMA = "#0F4C5C"
WARNA_SEKUNDER = "#8C8273"
WARNA_REDUP = "#C9D2DA"
# Warna latar lembut untuk setiap status (dipakai di tabel dan pita grafik)
LATAR_STATUS = {STATUS_ATAS: "#E7F3E8", STATUS_SESUAI: "#E6EEF6", STATUS_BAWAH: "#FBE9E9"}
BADGE_STATUS = {STATUS_ATAS: "green", STATUS_SESUAI: "blue", STATUS_BAWAH: "red"}
IKON_STATUS = {STATUS_ATAS: ":material/trending_up:", STATUS_SESUAI: ":material/check_circle:",
               STATUS_BAWAH: ":material/trending_down:"}

CSS = """
<style>
[data-testid="stMainBlockContainer"], .block-container {padding-top: 4.5rem !important; max-width: 1280px;}
.hero {background: linear-gradient(120deg, #0F4C5C 0%, #14606F 55%, #2A8C82 100%); color: #fff;
       padding: 1.5rem 2rem; border-radius: 1rem; margin-bottom: 1rem;
       box-shadow: 0 10px 28px rgba(15, 76, 92, .18);}
.hero-label {font-size: .75rem; letter-spacing: .09em; text-transform: uppercase; opacity: .8;
             margin-bottom: .3rem; font-weight: 600;}
.hero-judul {font-size: 1.85rem; font-weight: 700; line-height: 1.25;}
.hero-desk {margin-top: .55rem; opacity: .92; max-width: 62rem; font-size: 1.02rem; line-height: 1.5;}
.kartu {background: #fff; border: 1px solid #DCE4EA; border-left: 6px solid var(--w); border-radius: .8rem;
        padding: .9rem 1.1rem; box-shadow: 0 1px 2px rgba(16, 24, 40, .04);}
.kartu-label {font-size: .82rem; color: #5B6B79; font-weight: 600; text-transform: uppercase;
              letter-spacing: .04em;}
.kartu-angka {font-size: 1.85rem; font-weight: 700; color: var(--w); line-height: 1.25;}
.kartu-sub {font-size: .88rem; color: #4A5866; line-height: 1.45;}
.pill {display: inline-block; padding: .22rem .75rem; border-radius: 999px; font-weight: 600;
       font-size: .85rem; color: #fff; background: var(--w);}
</style>
"""


def pasang_gaya():
    """Sisipkan CSS bersama. Dipanggil sekali di Beranda.py sebelum halaman dijalankan."""
    st.html(CSS)


def hero(judul, deskripsi, label="Prediksi IPM · XGBoost Regression"):
    """Header berwarna di bagian atas halaman."""
    st.markdown(
        f"<div class='hero'><div class='hero-label'>{label}</div>"
        f"<div class='hero-judul'>{judul}</div><div class='hero-desk'>{deskripsi}</div></div>",
        unsafe_allow_html=True,
    )


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
        hoverlabel=dict(bgcolor="white", font_size=13), showlegend=legenda,
        uniformtext=dict(minsize=10, mode="hide"),     # sembunyikan label yang tidak muat di batang kecil
    )
    fig.update_traces(textangle=0, selector=dict(type="bar"))
    return fig


def grafik_selisih(selisih, ambang):
    """Pita horizontal: merah (di bawah), biru (sesuai), hijau (di atas), dengan penanda posisi selisih."""
    batas = max(abs(selisih) + 1.5, ambang * 2.2)
    status = tentukan_status(selisih, ambang)
    fig = go.Figure()
    for x0, x1, s in [(-batas, -ambang, STATUS_BAWAH), (-ambang, ambang, STATUS_SESUAI), (ambang, batas, STATUS_ATAS)]:
        fig.add_shape(type="rect", x0=x0, x1=x1, y0=0, y1=1, fillcolor=LATAR_STATUS[s], line_width=0, layer="below")
        fig.add_annotation(x=(x0 + x1) / 2, y=0.18, text=s, showarrow=False,
                           font=dict(size=11, color=WARNA_STATUS[s]))
    for x in (-ambang, ambang):
        fig.add_vline(x=x, line=dict(color="#9AA7B2", width=1, dash="dot"))
    fig.add_vline(x=0, line=dict(color="#9AA7B2", width=1))
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
