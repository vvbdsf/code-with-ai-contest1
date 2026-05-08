# 5G 信号可视化看板

基于 **Streamlit + pandas + pydeck** 的本地 Web 看板，用于展示与筛选 5G 路测模拟数据（经纬度、小区、频段、RSRP、SINR、终端类型、下行速率等），适用于「Code with AI」类赛事或教学演示。

---

## 项目做什么

| 模块 | 说明 |
|------|------|
| **数据加载** | 使用 pandas 读取 `data/signal_samples.csv`，启动时缓存加载。 |
| **二维地图** | pydeck `ScatterplotLayer`，按 **RSRP (dBm)** 着色：优于 -90 偏绿，劣于 -110 偏红，中间为黄—橙渐变。 |
| **三维视图** | pydeck `ColumnLayer`，柱高与 **Download_Mbps** 成正比，颜色仍反映 RSRP。 |
| **侧边栏筛选** | 多选 **Band**、**RSRP** 范围滑块；筛选后地图与下方图表同步更新。 |
| **统计图表** | 各频段 **唯一 CellID 数量**柱状图；**终端类型**样本数柱状图。 |
| **可测试逻辑** | `signal_utils.py` 封装加载、筛选、配色等，配套 `pytest` 单元测试。 |

---

## 目录结构（建议）

```
├── app.py                 # Streamlit 入口
├── signal_utils.py        # 数据处理与配色（便于单测）
├── requirements.txt       # Python 依赖
├── data/
│   └── signal_samples.csv # 赛题提供的路测样例数据
├── tests/
│   └── test_signal_utils.py
├── AI_PROMPTS.md          # AI Agent 交互日志（参赛时按主办方要求填写）
└── README.md              # 本文件
```

---

## 环境要求

- Python **3.10+**（推荐 **3.12**）
- 可访问公网以下载 pip 包（或使用国内镜像源）

---

## 安装与运行

```bash
# 进入项目根目录后
python -m pip install -r requirements.txt

# Windows 若安装了多个 Python，可用启动器指定版本，例如：
# py -3.12 -m pip install -r requirements.txt

streamlit run app.py
```

浏览器打开终端提示的地址（一般为 **http://localhost:8501**）。

---

## 运行单元测试

```bash
python -m pytest tests -q
```

---

## 数据字段说明

`signal_samples.csv` 主要列：

- `Latitude` / `Longitude`：采样点坐标  
- `CellID`：小区标识  
- `Band`：频段（如 n28、n41、n78）  
- `RSRP_dBm`：参考信号接收功率  
- `SINR_dB`：信噪比  
- `TerminalType`：终端类型（如 Smartphone、CPE、IoT）  
- `Download_Mbps`：下行速率（用于三维柱高）

---

## Git 提交与赛题打卡（可选）

若仓库为比赛用 Git 远程仓，完成度可按主办方要求打 Tag，例如：

```bash
git add .
git commit -m "完成基础/进阶功能说明"
git tag basic-done      # 基础关卡
# git tag advanced-done # 进阶关卡
git push origin main --tags
```

具体以当前届比赛 README 为准。

---

## 许可证与致谢

数据与赛题背景由活动主办方提供；本看板实现为示例工程，可按队伍需要修改署名与说明。
# 5G 信号可视化看板

基于 **Streamlit + pandas + pydeck** 的本地 Web 看板，用于展示与筛选 5G 路测模拟数据（经纬度、小区、频段、RSRP、SINR、终端类型、下行速率等），适用于「Code with AI」类赛事或教学演示。

---

## 项目做什么

| 模块 | 说明 |
|------|------|
| **数据加载** | 使用 pandas 读取 `data/signal_samples.csv`，启动时缓存加载。 |
| **二维地图** | pydeck `ScatterplotLayer`，按 **RSRP (dBm)** 着色：优于 -90 偏绿，劣于 -110 偏红，中间为黄—橙渐变。 |
| **三维视图** | pydeck `ColumnLayer`，柱高与 **Download_Mbps** 成正比，颜色仍反映 RSRP。 |
| **侧边栏筛选** | 多选 **Band**、**RSRP** 范围滑块；筛选后地图与下方图表同步更新。 |
| **统计图表** | 各频段 **唯一 CellID 数量**柱状图；**终端类型**样本数柱状图。 |
| **可测试逻辑** | `signal_utils.py` 封装加载、筛选、配色等，配套 `pytest` 单元测试。 |

---

## 目录结构（建议）

```
├── app.py                 # Streamlit 入口
├── signal_utils.py        # 数据处理与配色（便于单测）
├── requirements.txt       # Python 依赖
├── data/
│   └── signal_samples.csv # 赛题提供的路测样例数据
├── tests/
│   └── test_signal_utils.py
├── AI_PROMPTS.md          # AI Agent 交互日志（参赛时按主办方要求填写）
└── README.md              # 本文件
```

---

## 环境要求

- Python **3.10+**（推荐 **3.12**）
- 可访问公网以下载 pip 包（或使用国内镜像源）

---

## 安装与运行

```bash
# 进入项目根目录后
python -m pip install -r requirements.txt

# Windows 若安装了多个 Python，可用启动器指定版本，例如：
# py -3.12 -m pip install -r requirements.txt

streamlit run app.py
```

浏览器打开终端提示的地址（一般为 **http://localhost:8501**）。

---

## 运行单元测试

```bash
python -m pytest tests -q
```

---

## 数据字段说明

`signal_samples.csv` 主要列：

- `Latitude` / `Longitude`：采样点坐标  
- `CellID`：小区标识  
- `Band`：频段（如 n28、n41、n78）  
- `RSRP_dBm`：参考信号接收功率  
- `SINR_dB`：信噪比  
- `TerminalType`：终端类型（如 Smartphone、CPE、IoT）  
- `Download_Mbps`：下行速率（用于三维柱高）

---

## Git 提交与赛题打卡（可选）

若仓库为比赛用 Git 远程仓，完成度可按主办方要求打 Tag，例如：

```bash
git add .
git commit -m "完成基础/进阶功能说明"
git tag basic-done      # 基础关卡
# git tag advanced-done # 进阶关卡
git push origin main --tags
```

具体以当前届比赛 README 为准。

---

## 许可证与致谢

数据与赛题背景由活动主办方提供；本看板实现为示例工程，可按队伍需要修改署名与说明。
