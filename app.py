"""
5G 信号可视化看板 — Streamlit 入口。

地图与图表数据经侧边栏筛选后实时刷新；二维散点与三维柱图均基于 pydeck。
"""

from __future__ import annotations

import pydeck as pdk
import streamlit as st

import signal_utils as su

st.set_page_config(page_title="5G 信号可视化看板", layout="wide")

st.title("📡 5G 信号可视化看板")
st.caption("Code with AI 海选赛 · 路测数据交互分析（pandas + pydeck + Streamlit）")


@st.cache_data(show_spinner="正在加载 CSV …")
def _cached_load():
    return su.load_signal_data()


df_source = _cached_load()
all_band_values = su.all_bands(df_source)
rsrp_floor = float(df_source["RSRP_dBm"].min())
rsrp_ceil = float(df_source["RSRP_dBm"].max())

with st.sidebar:
    st.header("筛选器")
    st.markdown("调整下方控件后，右侧地图与图表会**即时**按筛选结果更新。")
    selected_bands = st.multiselect(
        "频段 Band",
        options=all_band_values,
        default=all_band_values,
        help="可多选；全部选中等价于不限制频段。",
    )
    if not selected_bands:
        st.warning("请至少选择一个频段，已暂时恢复为全选。")
        selected_bands = list(all_band_values)

    rsrp_range = st.slider(
        "RSRP 范围 (dBm)",
        min_value=rsrp_floor,
        max_value=rsrp_ceil,
        value=(rsrp_floor, rsrp_ceil),
        help="仅保留 RSRP 落在该闭区间内的采样点。",
    )
    rsrp_min, rsrp_max = su.validate_rsrp_range(rsrp_range[0], rsrp_range[1])

band_arg = None if set(selected_bands) == set(all_band_values) else selected_bands
filtered = su.filter_signals(df_source, band_arg, rsrp_min, rsrp_max)
filtered = su.attach_rsrp_colors(filtered)

st.metric(
    "当前点数",
    len(filtered),
    delta=(len(filtered) - len(df_source)) if len(filtered) != len(df_source) else None,
)

# ---------- 二维：RSRP 着色散点 ----------
st.subheader("二维信号地图（散点颜色 = RSRP）")
st.markdown(
    "着色规则：**RSRP > -90 dBm 为绿色**，**RSRP < -110 dBm 为红色**，"
    "中间区段为黄—橙渐变。"
)

if filtered.empty:
    st.warning("当前筛选条件下无数据，请放宽 RSRP 或频段范围。")
else:
    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=filtered,
        id="rsrp-scatter",
        get_position="[Longitude, Latitude]",
        get_fill_color="[color_r, color_g, color_b, 200]",
        get_line_color="[40, 40, 40, 120]",
        line_width_min_pixels=1,
        get_radius=120,
        pickable=True,
        auto_highlight=True,
    )
    view_2d = pdk.ViewState(**su.initial_view_state(filtered))
    deck_2d = pdk.Deck(
        layers=[scatter_layer],
        initial_view_state=view_2d,
        map_style="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
        tooltip={
            "html": "<b>Cell</b> {CellID}<br/><b>Band</b> {Band}<br/>"
            "<b>RSRP</b> {RSRP_dBm} dBm<br/><b>SINR</b> {SINR_dB} dB<br/>"
            "<b>终端</b> {TerminalType}<br/><b>下行</b> {Download_Mbps} Mbps",
            "style": {"color": "white"},
        },
    )
    st.pydeck_chart(deck_2d, use_container_width=True)

# ---------- 三维：柱高 = 下载速率 ----------
st.subheader("三维下载速率（柱体高度 ∝ Download_Mbps）")
st.markdown("通过俯仰视角观察柱高；柱体颜色仍表示 RSRP 强弱。")

if not filtered.empty:
    column_layer = pdk.Layer(
        "ColumnLayer",
        data=filtered,
        id="rate-columns",
        get_position="[Longitude, Latitude]",
        get_elevation="Download_Mbps",
        elevation_scale=90,
        radius=90,
        coverage=0.88,
        get_fill_color="[color_r, color_g, color_b, 210]",
        extruded=True,
        pickable=True,
    )
    view_3d = pdk.ViewState(**su.view_state_3d(filtered))
    deck_3d = pdk.Deck(
        layers=[column_layer],
        initial_view_state=view_3d,
        map_style="https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
        tooltip={
            "html": "<b>下行速率</b> {Download_Mbps} Mbps<br/><b>RSRP</b> {RSRP_dBm} dBm<br/>"
            "<b>Band</b> {Band} · <b>Cell</b> {CellID}",
            "style": {"color": "white"},
        },
    )
    st.pydeck_chart(deck_3d, use_container_width=True)

# ---------- 概览图表 ----------
st.subheader("数据概览")
c1, c2 = st.columns(2, gap="large")

with c1:
    st.markdown("**各频段唯一小区数量**（按 CellID 去重统计）")
    band_counts = su.band_cell_counts(filtered)
    if band_counts.empty:
        st.caption("无数据可绘。")
    else:
        st.bar_chart(band_counts.rename("小区数"))

with c2:
    st.markdown("**终端类型样本占比**（计数）")
    term_counts = su.terminal_type_shares(filtered)
    if term_counts.empty:
        st.caption("无数据可绘。")
    else:
        st.bar_chart(term_counts.rename("样本数"))

with st.expander("原始数据预览（筛选后）"):
    st.dataframe(filtered.head(200), use_container_width=True)
