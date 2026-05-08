"""signal_utils 核心逻辑的单元测试。"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

import signal_utils as su


@pytest.fixture
def tiny_csv(tmp_path: Path) -> Path:
    """构造最小合法 CSV，便于在临时目录中测试加载与筛选。"""
    p = tmp_path / "mini.csv"
    p.write_text(
        "Latitude,Longitude,CellID,Band,RSRP_dBm,SINR_dB,TerminalType,Download_Mbps\n"
        "31.0,121.0,1,n28,-85.0,10.0,Smartphone,100.0\n"
        "31.1,121.1,2,n41,-115.0,5.0,CPE,200.0\n"
        "31.2,121.2,3,n78,-100.0,8.0,IoT,300.0\n",
        encoding="utf-8",
    )
    return p


def test_load_signal_data(tiny_csv: Path) -> None:
    df = su.load_signal_data(tiny_csv)
    assert len(df) == 3
    assert set(df["Band"]) == {"n28", "n41", "n78"}


def test_load_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        su.load_signal_data(Path("/nonexistent/signal.csv"))


def test_rsrp_to_rgba_extremes() -> None:
    r, g, b, _a = su.rsrp_to_rgba(-80.0)
    assert g > r and g > b  # 偏绿
    r2, g2, b2, _a2 = su.rsrp_to_rgba(-120.0)
    assert r2 > g2  # 偏红


def test_attach_rsrp_colors() -> None:
    df = pd.DataFrame({"RSRP_dBm": [-80.0, -100.0, -120.0]})
    out = su.attach_rsrp_colors(df)
    assert list(out.columns[-4:]) == ["color_r", "color_g", "color_b", "color_a"]


def test_filter_signals_band_and_rsrp(tiny_csv: Path) -> None:
    df = su.load_signal_data(tiny_csv)
    only_n28 = su.filter_signals(df, ["n28"], -200.0, 0.0)
    assert len(only_n28) == 1
    assert only_n28.iloc[0]["CellID"] == 1
    mid_rsrp = su.filter_signals(df, None, -105.0, -95.0)
    assert len(mid_rsrp) == 1
    assert mid_rsrp.iloc[0]["Band"] == "n78"


def test_band_cell_counts() -> None:
    df = pd.DataFrame(
        {
            "Band": ["n28", "n28", "n41"],
            "CellID": [1, 1, 2],
            "RSRP_dBm": [-90, -91, -92],
        }
    )
    s = su.band_cell_counts(df)
    assert int(s["n28"]) == 1
    assert int(s["n41"]) == 1


def test_validate_rsrp_range() -> None:
    a, b = su.validate_rsrp_range(10.0, 5.0)
    assert (a, b) == (5.0, 10.0)
