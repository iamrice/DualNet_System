import numpy as np
import pandas as pd


# ─────────────────────────────────────────────
# Page 1: 双网能耗模型与多尺度时空预测
# ─────────────────────────────────────────────

def gen_energy_timeseries(scenario: str = "平峰") -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n = 30 * 24
    t = np.arange(n)
    base = 500 + 200 * np.sin(2 * np.pi * t / 24) + 80 * np.sin(2 * np.pi * t / (24 * 7))
    noise = rng.normal(0, 15, n)
    actual = base + noise

    if scenario == "异常":
        spike_start, spike_end = 20 * 24, 22 * 24
        actual[spike_start:spike_end] += rng.uniform(150, 300, spike_end - spike_start)

    pred_ours = actual + rng.normal(0, actual * 0.042, n)
    pred_lstm = actual + rng.normal(0, actual * 0.098, n)
    pred_arima = actual + rng.normal(0, actual * 0.121, n)

    timestamps = pd.date_range("2024-01-01", periods=n, freq="h")
    return pd.DataFrame({
        "时间": timestamps,
        "实际值": actual,
        "本文模型": pred_ours,
        "LSTM": pred_lstm,
        "ARIMA": pred_arima,
    })


def gen_model_comparison() -> pd.DataFrame:
    return pd.DataFrame({
        "模型": ["本文模型", "LSTM", "Transformer", "ARIMA", "SVR"],
        "MAE (kWh)": [18.3, 39.2, 35.7, 52.1, 48.6],
        "RMSE (kWh)": [24.1, 51.8, 47.3, 68.4, 63.2],
        "MAPE (%)": [4.2, 9.8, 8.9, 12.1, 11.3],
        "较最优基线改进": ["-", "57.1%↑", "52.4%↑", "65.3%↑", "62.9%↑"],
    })


def gen_spatial_grid() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    lats = np.linspace(31.1, 31.4, 20)
    lons = np.linspace(121.3, 121.6, 20)
    records = []
    for lat in lats:
        for lon in lons:
            dist = np.sqrt((lat - 31.25) ** 2 + (lon - 121.45) ** 2)
            density = max(0, 800 - 1500 * dist + rng.normal(0, 50))
            records.append({"lat": lat, "lon": lon, "能耗密度": density})
    return pd.DataFrame(records)


# ─────────────────────────────────────────────
# Page 2: 充电站选址与容量优化
# ─────────────────────────────────────────────

def gen_charging_stations():
    rng = np.random.default_rng(42)
    n_cand = 30
    lats = rng.uniform(31.1, 31.4, n_cand)
    lons = rng.uniform(121.3, 121.6, n_cand)
    demands = rng.uniform(50, 300, n_cand)
    candidates = pd.DataFrame({
        "站点ID": [f"C{i+1:02d}" for i in range(n_cand)],
        "lat": lats, "lon": lons,
        "需求量 (kW)": demands.round(1),
    })
    selected_idx = [2, 5, 8, 11, 15, 19, 23, 27]
    selected = candidates.iloc[selected_idx].copy().reset_index(drop=True)
    selected["容量 (kW)"] = rng.uniform(200, 600, len(selected_idx)).round(1)
    selected["快充桩数"] = rng.integers(4, 12, len(selected_idx))
    selected["慢充桩数"] = rng.integers(8, 20, len(selected_idx))
    return candidates, selected


def gen_optimization_convergence() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    iters = np.arange(1, 201)
    robust = 1000 * np.exp(-iters / 60) + 320 + rng.normal(0, 8, 200)
    deterministic = 1000 * np.exp(-iters / 40) + 380 + rng.normal(0, 6, 200)
    return pd.DataFrame({
        "迭代次数": iters,
        "鲁棒优化": robust.round(2),
        "确定性优化": deterministic.round(2),
    })


def gen_capacity_allocation() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    stations = [f"站点{i+1}" for i in range(8)]
    fast = rng.uniform(100, 300, 8).round(1)
    slow = rng.uniform(80, 200, 8).round(1)
    buffer = rng.uniform(20, 80, 8).round(1)
    return pd.DataFrame({
        "站点": stations,
        "快充容量 (kW)": fast,
        "慢充容量 (kW)": slow,
        "缓冲容量 (kW)": buffer,
    })


def gen_uncertainty_scenarios() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    n = 50
    demand_factor = rng.uniform(0.7, 1.4, n)
    renewable_factor = rng.uniform(0.5, 1.2, n)
    cost = 500 + 200 * demand_factor - 100 * renewable_factor + rng.normal(0, 30, n)
    return pd.DataFrame({
        "需求因子": demand_factor.round(3),
        "可再生能源因子": renewable_factor.round(3),
        "总成本 (万元)": cost.round(1),
    })


# ─────────────────────────────────────────────
# Page 3: 动态电价调控与交通流调度
# ─────────────────────────────────────────────

def gen_grid_load(scenario: str = "平峰") -> pd.DataFrame:
    rng = np.random.default_rng(42)
    hours = np.arange(24)
    base = 800 + 300 * np.sin(np.pi * (hours - 6) / 12)
    if scenario == "异常":
        base = base.copy().astype(float)
        base[8:11] += rng.uniform(200, 400, 3)
        base[17:20] += rng.uniform(150, 300, 3)
    optimized = base * rng.uniform(0.88, 0.95, 24)
    return pd.DataFrame({
        "小时": hours,
        "基准负荷 (MW)": base.round(1),
        "优化后负荷 (MW)": optimized.round(1),
    })


def gen_electricity_price(scenario: str = "平峰") -> pd.DataFrame:
    rng = np.random.default_rng(42)
    hours = np.arange(24)
    price_before = 0.5 + 0.3 * np.sin(np.pi * (hours - 6) / 12) + rng.normal(0, 0.02, 24)
    price_before = price_before.astype(float)
    if scenario == "异常":
        price_before[8:11] += rng.uniform(0.2, 0.4, 3)
        price_before[17:20] += rng.uniform(0.15, 0.3, 3)
    price_after = price_before * rng.uniform(0.85, 0.98, 24)
    return pd.DataFrame({
        "小时": hours,
        "博弈前电价 (元/kWh)": price_before.round(3),
        "博弈后电价 (元/kWh)": price_after.round(3),
    })


def gen_traffic_flow(scenario: str = "平峰") -> pd.DataFrame:
    rng = np.random.default_rng(42)
    roads = [
        ("R01", 31.22, 121.38, 31.25, 121.45),
        ("R02", 31.25, 121.45, 31.28, 121.52),
        ("R03", 31.18, 121.42, 31.22, 121.38),
        ("R04", 31.28, 121.35, 31.25, 121.45),
        ("R05", 31.30, 121.48, 31.28, 121.52),
        ("R06", 31.15, 121.50, 31.18, 121.42),
        ("R07", 31.22, 121.55, 31.25, 121.45),
        ("R08", 31.32, 121.40, 31.30, 121.48),
        ("R09", 31.20, 121.32, 31.22, 121.38),
        ("R10", 31.35, 121.45, 31.32, 121.40),
        ("R11", 31.25, 121.45, 31.22, 121.55),
        ("R12", 31.28, 121.52, 31.30, 121.48),
    ]
    flows = rng.uniform(200, 1200, len(roads))
    congestion = rng.uniform(0.2, 0.8, len(roads))
    if scenario == "异常":
        # 部分路段严重拥堵
        flows[:4] *= rng.uniform(1.3, 1.8, 4)
        congestion[:4] = rng.uniform(0.75, 0.98, 4)
    df = pd.DataFrame(roads, columns=["路段ID", "起点纬度", "起点经度", "终点纬度", "终点经度"])
    df["流量 (辆/h)"] = flows.round(0).astype(int)
    df["拥堵指数"] = congestion.round(3)
    return df


def gen_traffic_heatmap() -> pd.DataFrame:
    """各路段24h流量热力图数据。"""
    rng = np.random.default_rng(42)
    roads = [f"R{i+1:02d}" for i in range(12)]
    hours = list(range(24))
    data = []
    for road in roads:
        for h in hours:
            base_flow = 400 + 300 * np.sin(np.pi * (h - 7) / 12)
            flow = max(0, base_flow + rng.normal(0, 50))
            data.append({"路段": road, "小时": h, "流量": round(flow)})
    return pd.DataFrame(data)


def gen_game_convergence() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    iters = np.arange(1, 101)
    utility_grid = -500 * np.exp(-iters / 30) + 800 + rng.normal(0, 10, 100)
    utility_traffic = -400 * np.exp(-iters / 25) + 650 + rng.normal(0, 8, 100)
    nash_gap = 200 * np.exp(-iters / 20) + rng.normal(0, 5, 100)
    return pd.DataFrame({
        "迭代次数": iters,
        "电网效用": utility_grid.round(2),
        "交通效用": utility_traffic.round(2),
        "纳什均衡差距": np.abs(nash_gap).round(2),
    })


def gen_kpi_comparison(scenario: str = "平峰") -> dict:
    if scenario == "平峰":
        return {
            "拥堵时间减少": 8.3,
            "峰值负荷降低": 8.7,
            "电价波动降低": 12.4,
            "调度效率提升": 15.2,
        }
    else:
        return {
            "拥堵时间减少": 9.1,
            "峰值负荷降低": 10.2,
            "电价波动降低": 18.6,
            "调度效率提升": 21.3,
        }


def gen_radar_comparison() -> pd.DataFrame:
    metrics = ["拥堵减少", "负荷降低", "电价优化", "调度效率", "能耗节约", "碳排放减少"]
    before = [0, 0, 0, 0, 0, 0]
    after_normal = [8.3, 8.7, 12.4, 15.2, 9.6, 11.2]
    after_anomaly = [9.1, 10.2, 18.6, 21.3, 13.4, 15.8]
    return pd.DataFrame({
        "指标": metrics,
        "优化前": before,
        "平峰场景优化后": after_normal,
        "异常场景优化后": after_anomaly,
    })
