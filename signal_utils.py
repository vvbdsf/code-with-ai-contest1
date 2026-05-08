"""
5G 路测数据处理与可视化辅助函数。

将 CSV 加载、RSRP 分级配色、侧边栏筛选等逻辑集中于此，便于单元测试与复用。
"""

from __future__ import annotations

from pathlib import Path
from typing import Sequence

import pandas as pd

# 默认数据路径（相对项目根目录）
DEFAULT_CSV_PATH = Path(__file__).resolve().parent / "data" / "signal_samples.csv"

# RSRP 着色阈值（单位 dBm）：优于 -90 视为强覆盖，劣于 -110 视为弱覆盖
RSRP_STRONG_DB = -90
RSRP_WEAK_DB = -110


def load_signal_data(csv_path: Path | str | None = None) -> pd.DataFrame:
    """
    使用 pandas 读取标准 5G 模拟数据集。

    参数:
        csv_path: CSV 文件路径；默认读取仓库内 data/signal_samples.csv。

    返回:
        包含 Latitude, Longitude, CellID, Band, RSRP_dBm 等字段的 DataFrame。
    """
    path = Path(csv_path) if csv_path else DEFAULT_CSV_PATH
    if not path.is_file():
        raise FileNotFoundError(f"数据文件不存在: {path}")
    df = pd.read_csv(path)
    required = {
        "Latitude",
        "Longitude",
        "CellID",
        "Band",
        "RSRP_dBm",
        "SINR_dB",
        "TerminalType",
        "Download_Mbps",
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"CSV 缺少必要列: {sorted(missing)}")
    return df


def rsrp_to_rgba(rsrp: float) -> tuple[int, int, int, int]:
    """
    将 RSRP(dBm) 映射为 RGBA，用于地图散点/柱体填色。

    规则（与赛题一致）:
        - RSRP > -90: 绿色（强信号）
        - RSRP < -110: 红色（弱信号）
        - 介于两者之间: 黄—橙渐变，便于区分中等覆盖
    """
    if rsrp > RSRP_STRONG_DB:
        return 34, 197, 94, 220
    if rsrp < RSRP_WEAK_DB:
        return 239, 68, 68, 220
    # [-110, -90] 线性插值：红 -> 黄 -> 绿
    t = (rsrp - RSRP_WEAK_DB) / (RSRP_STRONG_DB - RSRP_WEAK_DB)
    t = max(0.0, min(1.0, t))
    r = int(239 + (234 - 239) * t)
    g = int(68 + (179 - 68) * t)
    b = int(68 + (8 - 68) * t)
    return r, g, b, 220


def attach_rsrp_colors(df: pd.DataFrame) -> pd.DataFrame:
    """为每一行计算 RSRP 对应的 RGB，写入 color_r/color_g/color_b/color_a 列。"""
    out = df.copy()
    colors = out["RSRP_dBm"].astype(float).map(rsrp_to_rgba)
    out["color_r"] = colors.map(lambda c: c[0])
    out["color_g"] = colors.map(lambda c: c[1])
    out["color_b"] = colors.map(lambda c: c[2])
    out["color_a"] = colors.map(lambda c: c[3])
    return out


def filter_signals(
    df: pd.DataFrame,
    bands: Sequence[str] | None,
    rsrp_min: float,
    rsrp_max: float,
) -> pd.DataFrame:
    """
    按频段与 RSRP 范围筛选路测点。

    参数:
        df: 原始数据。
        bands: 选中的 Band 列表；None 或空序列表示不限制频段。
        rsrp_min/rsrp_max: RSRP 闭区间 [min, max]。
    """
    out = df.copy()
    out = out[(out["RSRP_dBm"] >= rsrp_min) & (out["RSRP_dBm"] <= rsrp_max)]
    if bands:
        out = out[out["Band"].isin(bands)]
    return out.reset_index(drop=True)


def band_cell_counts(df: pd.DataFrame) -> pd.Series:
    """各频段唯一小区（CellID）数量，用于柱状图。"""
    if df.empty:
        return pd.Series(dtype=int)
    return df.groupby("Band")["CellID"].nunique().sort_index()


def terminal_type_shares(df: pd.DataFrame) -> pd.Series:
    """各终端类型样本数占比（计数），用于饼图。"""
    if df.empty:
        return pd.Series(dtype=int)
    return df["TerminalType"].value_counts()


def initial_view_state(df: pd.DataFrame) -> dict[str, float]:
    """根据数据经纬度范围计算 pydeck 初始视角（中心与缩放）。"""
    if df.empty:
        return {"latitude": 31.23, "longitude": 121.47, "zoom": 10, "pitch": 0, "bearing": 0}
    lat_m, lon_m = float(df["Latitude"].mean()), float(df["Longitude"].mean())
    lat_span = max(float(df["Latitude"].max() - df["Latitude"].min()), 0.01)
    zoom = max(9.0, min(13.0, 11.5 - lat_span * 80))
    return {"latitude": lat_m, "longitude": lon_m, "zoom": zoom, "pitch": 0, "bearing": 0}


def view_state_3d(df: pd.DataFrame) -> dict[str, float]:
    """三维柱图使用的视角（带俯仰角）。"""
    base = initial_view_state(df)
    base["pitch"] = 52.0
    base["bearing"] = -25.0
    base["zoom"] = min(base["zoom"] + 0.3, 13.5)
    return base


def all_bands(df: pd.DataFrame) -> list[str]:
    """数据中出现的全部 Band，排序后用于多选默认值。"""
    return sorted(df["Band"].astype(str).unique().tolist())


def validate_rsrp_range(rsrp_min: float, rsrp_max: float) -> tuple[float, float]:
    """确保 RSRP 滑块 min <= max。"""
    if rsrp_min > rsrp_max:
        return rsrp_max, rsrp_min
    return rsrp_min, rsrp_max
