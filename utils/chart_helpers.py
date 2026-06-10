import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

COLORS = {
    "primary": "#1E88E5",
    "green": "#43A047",
    "orange": "#FB8C00",
    "red": "#E53935",
    "purple": "#8E24AA",
    "gray": "#90A4AE",
}

LAYOUT_BASE = dict(
    font=dict(family="SimHei, Microsoft YaHei, sans-serif", size=13),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    margin=dict(l=40, r=20, t=40, b=40),
)


def make_timeseries_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["时间"], y=df["实际值"], name="实际值",
                             line=dict(color=COLORS["gray"], width=1.5)))
    fig.add_trace(go.Scatter(x=df["时间"], y=df["本文模型"], name="本文模型",
                             line=dict(color=COLORS["primary"], width=2)))
    fig.add_trace(go.Scatter(x=df["时间"], y=df["LSTM"], name="LSTM",
                             line=dict(color=COLORS["orange"], width=1.5, dash="dash")))
    fig.add_trace(go.Scatter(x=df["时间"], y=df["ARIMA"], name="ARIMA",
                             line=dict(color=COLORS["red"], width=1.5, dash="dot")))
    fig.update_layout(**LAYOUT_BASE, title="能耗时序预测对比",
                      xaxis=dict(rangeslider=dict(visible=True), title="时间"),
                      yaxis=dict(title="能耗 (kWh)"), legend=dict(orientation="h", y=1.1))
    return fig


def make_error_boxplot(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    for col, color in [("本文模型", COLORS["primary"]), ("LSTM", COLORS["orange"]), ("ARIMA", COLORS["red"])]:
        errors = (df[col] - df["实际值"]).abs()
        fig.add_trace(go.Box(y=errors, name=col, marker_color=color))
    fig.update_layout(**LAYOUT_BASE, title="预测误差分布", yaxis_title="绝对误差 (kWh)")
    return fig


def make_bar_comparison(df: pd.DataFrame) -> go.Figure:
    metrics = ["MAE (kWh)", "RMSE (kWh)", "MAPE (%)"]
    colors = [COLORS["primary"], COLORS["orange"], COLORS["red"], COLORS["purple"], COLORS["green"]]
    fig = go.Figure()
    for i, row in df.iterrows():
        fig.add_trace(go.Bar(
            name=row["模型"],
            x=metrics,
            y=[row[m] for m in metrics],
            marker_color=colors[i % len(colors)],
        ))
    fig.update_layout(**LAYOUT_BASE, title="模型性能对比", barmode="group",
                      yaxis_title="误差值", legend=dict(orientation="h", y=1.1))
    return fig


def make_city_heatmap(df: pd.DataFrame) -> go.Figure:
    fig = px.density_mapbox(
        df, lat="lat", lon="lon", z="能耗密度",
        radius=18, center=dict(lat=31.25, lon=121.45), zoom=10,
        mapbox_style="carto-positron",
        color_continuous_scale="YlOrRd",
        title="城市能耗空间分布热力图",
    )
    fig.update_layout(**LAYOUT_BASE, coloraxis_colorbar=dict(title="能耗密度"))
    return fig


def make_convergence_chart(df: pd.DataFrame, title: str = "优化收敛曲线") -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["迭代次数"], y=df.iloc[:, 1], name=df.columns[1],
                             line=dict(color=COLORS["primary"], width=2)))
    fig.add_trace(go.Scatter(x=df["迭代次数"], y=df.iloc[:, 2], name=df.columns[2],
                             line=dict(color=COLORS["orange"], width=2, dash="dash")))
    fig.update_layout(**LAYOUT_BASE, title=title,
                      xaxis_title="迭代次数", yaxis_title="目标函数值")
    return fig


def make_stacked_bar(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(name="快充容量", x=df["站点"], y=df["快充容量 (kW)"],
                         marker_color=COLORS["primary"]))
    fig.add_trace(go.Bar(name="慢充容量", x=df["站点"], y=df["慢充容量 (kW)"],
                         marker_color=COLORS["green"]))
    fig.add_trace(go.Bar(name="缓冲容量", x=df["站点"], y=df["缓冲容量 (kW)"],
                         marker_color=COLORS["orange"]))
    fig.update_layout(**LAYOUT_BASE, title="充电站容量分配", barmode="stack",
                      yaxis_title="容量 (kW)", legend=dict(orientation="h", y=1.1))
    return fig


def make_scatter_scenarios(df: pd.DataFrame) -> go.Figure:
    fig = px.scatter(df, x="需求因子", y="可再生能源因子", color="总成本 (万元)",
                     color_continuous_scale="RdYlGn_r", title="不确定性场景分布",
                     labels={"需求因子": "需求因子", "可再生能源因子": "可再生能源因子"})
    fig.update_layout(**LAYOUT_BASE)
    return fig


def make_load_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["小时"], y=df["基准负荷 (MW)"], name="基准负荷",
                             line=dict(color=COLORS["red"], width=2), fill="tozeroy",
                             fillcolor="rgba(229,57,53,0.1)"))
    fig.add_trace(go.Scatter(x=df["小时"], y=df["优化后负荷 (MW)"], name="优化后负荷",
                             line=dict(color=COLORS["green"], width=2), fill="tozeroy",
                             fillcolor="rgba(67,160,71,0.1)"))
    fig.update_layout(**LAYOUT_BASE, title="24小时电网负荷曲线",
                      xaxis=dict(title="小时", tickvals=list(range(0, 24, 2))),
                      yaxis_title="负荷 (MW)")
    return fig


def make_price_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["小时"], y=df["博弈前价格 (元/kWh)"], name="博弈前",
                             line=dict(color=COLORS["orange"], width=2, dash="dash")))
    fig.add_trace(go.Scatter(x=df["小时"], y=df["博弈后价格 (元/kWh)"], name="博弈后",
                             line=dict(color=COLORS["primary"], width=2)))
    fig.update_layout(**LAYOUT_BASE, title="24小时动态价格曲线",
                      xaxis=dict(title="小时", tickvals=list(range(0, 24, 2))),
                      yaxis_title="价格 (元/kWh)")
    return fig


def make_price_guidance_chart(series: dict[str, list[float]], title: str) -> go.Figure:
    fig = go.Figure()
    for name, values, color in [
        ("非自适应", series["非自适应"], COLORS["orange"]),
        ("自适应", series["自适应"], COLORS["primary"]),
    ]:
        fig.add_trace(go.Scatter(
            x=list(range(len(values))),
            y=values,
            name=name,
            mode="lines",
            line=dict(color=color, width=2),
        ))
    layout_args = LAYOUT_BASE.copy()
    layout_args.update({
        "title": title,
        "title_x": 0.02,
        "title_y": 0.97,
        "xaxis_title": "仿真步数",
        "yaxis_title": "价格引导指数",
        "xaxis": dict(range=[0, 769]),
        "legend": dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=1.03,
            yanchor="bottom",
        ),
        "margin": dict(l=60, r=24, t=88, b=56),
    })
    fig.update_layout(**layout_args)
    return fig


def make_peak_load_chart(series: dict[str, list[float]], title: str) -> go.Figure:
    fig = go.Figure()
    for name, values, color in [
        ("优化前", series["优化前"], "#7E57C2"),
        ("优化后", series["优化后"], "#2E7D32"),
    ]:
        fig.add_trace(go.Scatter(
            x=list(range(1, 60)),
            y=values,
            name=name,
            mode="lines",
            line=dict(color=color, width=2),
        ))

    layout_args = LAYOUT_BASE.copy()
    layout_args.update({
        "title": title,
        "title_x": 0.02,
        "title_y": 0.97,
        "xaxis_title": "潮流计算步数",
        "yaxis_title": "负荷（MW）",
        "xaxis": dict(range=[1, 59], tickvals=list(range(1, 60, 8))),
        "legend": dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=1.03,
            yanchor="bottom",
        ),
        "margin": dict(l=60, r=24, t=88, b=56),
    })
    fig.update_layout(**layout_args)
    return fig


def make_training_curve_chart(series: dict[str, list[float]]) -> go.Figure:
    fig = go.Figure()
    for name, values, color in [
        ("avg", series["avg"], "#C62828"),
        ("std", series["std"], "#00897B"),
        ("max", series["max"], "#6D4C41"),
    ]:
        fig.add_trace(go.Scatter(
            x=list(range(100)),
            y=values,
            name=name,
            mode="lines",
            line=dict(color=color, width=2),
        ))

    layout_args = LAYOUT_BASE.copy()
    layout_args.update({
        "title": "训练收敛过程",
        "title_x": 0.02,
        "title_y": 0.97,
        "xaxis_title": "迭代轮数",
        "yaxis_title": "适应度",
        "xaxis": dict(range=[0, 99]),
        "legend": dict(
            orientation="h",
            x=0.5,
            xanchor="center",
            y=1.03,
            yanchor="bottom",
        ),
        "margin": dict(l=60, r=24, t=88, b=56),
    })
    fig.update_layout(**layout_args)
    return fig


def make_traffic_map(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    max_flow = df["流量 (辆/h)"].max()
    for _, row in df.iterrows():
        width = 2 + 6 * row["流量 (辆/h)"] / max_flow
        congestion = row["拥堵指数"]
        color = f"rgba({int(229*congestion)},{int(160*(1-congestion))},53,0.85)"
        fig.add_trace(go.Scattermapbox(
            lat=[row["起点纬度"], row["终点纬度"]],
            lon=[row["起点经度"], row["终点经度"]],
            mode="lines",
            line=dict(width=width, color=color),
            name=row["路段ID"],
            hovertemplate=f"{row['路段ID']}<br>流量: {row['流量 (辆/h)']} 辆/h<br>拥堵指数: {row['拥堵指数']}<extra></extra>",
            showlegend=False,
        ))
    fig.update_layout(
        **LAYOUT_BASE,
        title="城市路网交通流量图（颜色=拥堵度，线宽=流量）",
        mapbox=dict(style="carto-positron", center=dict(lat=31.25, lon=121.45), zoom=10),
        height=500,
    )
    return fig


def make_excel_traffic_map(records: list[dict], title: str) -> go.Figure:
    fig = go.Figure()
    if not records:
        fig.update_layout(**LAYOUT_BASE, title=title)
        return fig

    max_flow = max(record["flow_count"] for record in records) or 1
    center_lat = sum((r["edge_u_lat"] + r["edge_v_lat"]) / 2 for r in records) / len(records)
    center_lon = sum((r["edge_u_lng"] + r["edge_v_lng"]) / 2 for r in records) / len(records)

    congestion_bins = [
        (0.0, 0.2, "rgba(46,125,50,0.78)"),
        (0.2, 0.4, "rgba(124,179,66,0.78)"),
        (0.4, 0.6, "rgba(251,192,45,0.78)"),
        (0.6, 0.8, "rgba(239,108,0,0.82)"),
        (0.8, 1.01, "rgba(198,40,40,0.86)"),
    ]
    width_bins = [
        (0.0, 0.25, 1.0),
        (0.25, 0.5, 2.0),
        (0.5, 0.75, 3.4),
        (0.75, 1.01, 5.0),
    ]
    grouped = {}

    for record in records:
        congestion = record["congestion_index"]
        flow_ratio = record["flow_count"] / max_flow
        color = next(color for low, high, color in congestion_bins if low <= congestion < high)
        width = next(width for low, high, width in width_bins if low <= flow_ratio < high)
        grouped.setdefault((color, width), {"lat": [], "lon": [], "text": []})
        group = grouped[(color, width)]
        group["lat"].extend([record["edge_u_lat"], record["edge_v_lat"], None])
        group["lon"].extend([record["edge_u_lng"], record["edge_v_lng"], None])

    for (color, width), group in grouped.items():
        fig.add_trace(go.Scattermapbox(
            lat=group["lat"],
            lon=group["lon"],
            mode="lines",
            line=dict(width=width, color=color),
            hoverinfo="skip",
            showlegend=False,
        ))

    layout_args = LAYOUT_BASE.copy()
    layout_args.update({
        "title": title,
        "mapbox": dict(
            style="carto-positron",
            center=dict(lat=center_lat, lon=center_lon),
            zoom=11,
        ),
        "height": 620,
        "margin": dict(l=10, r=10, t=54, b=10),
    })
    fig.update_layout(**layout_args)
    return fig


def make_traffic_congestion_heatmap(records: list[dict], top_n: int = 25) -> go.Figure:
    edge_scores = {}
    for record in records:
        score = edge_scores.setdefault(record["edge_id"], {"total": 0.0, "count": 0})
        score["total"] += record["congestion_index"]
        score["count"] += 1

    top_edges = sorted(
        edge_scores,
        key=lambda edge_id: edge_scores[edge_id]["total"] / edge_scores[edge_id]["count"],
        reverse=True,
    )[:top_n]
    edge_rank = {edge_id: index for index, edge_id in enumerate(top_edges)}
    matrix = [[0.0 for _ in range(25)] for _ in top_edges]

    for record in records:
        edge_index = edge_rank.get(record["edge_id"])
        if edge_index is not None:
            matrix[edge_index][record["block_id"]] = record["congestion_index"]

    fig = go.Figure(go.Heatmap(
        z=matrix,
        x=list(range(25)),
        y=top_edges,
        colorscale="YlOrRd",
        colorbar=dict(title="拥堵指数"),
        hovertemplate="时间块: %{x}<br>边ID: %{y}<br>拥堵指数: %{z:.3f}<extra></extra>",
    ))
    layout_args = LAYOUT_BASE.copy()
    layout_args.update({
        "title": "高拥堵路段时间块热力图",
        "xaxis_title": "时间块",
        "yaxis_title": "边ID",
        "height": 520,
        "margin": dict(l=90, r=20, t=54, b=48),
    })
    fig.update_layout(**layout_args)
    return fig


def make_traffic_heatmap(df: pd.DataFrame) -> go.Figure:
    pivot = df.pivot(index="路段", columns="小时", values="流量")
    fig = go.Figure(go.Heatmap(
        z=pivot.values, x=pivot.columns.tolist(), y=pivot.index.tolist(),
        colorscale="YlOrRd", colorbar=dict(title="流量 (辆/h)"),
    ))
    fig.update_layout(**LAYOUT_BASE, title="各路段24小时流量热力图",
                      xaxis_title="小时", yaxis_title="路段")
    return fig


def make_game_convergence(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["迭代次数"], y=df["电网效用"], name="电网效用",
                             line=dict(color=COLORS["primary"], width=2)))
    fig.add_trace(go.Scatter(x=df["迭代次数"], y=df["交通效用"], name="交通效用",
                             line=dict(color=COLORS["green"], width=2)))
    fig.add_trace(go.Scatter(x=df["迭代次数"], y=df["纳什均衡差距"], name="纳什均衡差距",
                             line=dict(color=COLORS["red"], width=2, dash="dot"),
                             yaxis="y2"))
    fig.update_layout(
        **LAYOUT_BASE, title="博弈收敛过程",
        xaxis_title="迭代次数",
        yaxis=dict(title="效用值"),
        yaxis2=dict(title="纳什均衡差距", overlaying="y", side="right", showgrid=False),
        legend=dict(orientation="h", y=1.1),
    )
    return fig


def make_gauge(value: float, title: str, suffix: str = "%") -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        delta={"reference": 8.0, "valueformat": ".1f"},
        number={"suffix": suffix, "font": {"size": 28}},
        title={"text": title, "font": {"size": 14}},
        gauge={
            "axis": {"range": [0, 25]},
            "bar": {"color": COLORS["primary"]},
            "steps": [
                {"range": [0, 8], "color": "rgba(229,57,53,0.2)"},
                {"range": [8, 15], "color": "rgba(67,160,71,0.2)"},
                {"range": [15, 25], "color": "rgba(30,136,229,0.2)"},
            ],
            "threshold": {"line": {"color": COLORS["red"], "width": 3}, "value": 8},
        },
    ))

    # ── 修复位置：避免参数解包冲突 ──
    # 1. 拷贝一份基础布局参数字典
    layout_args = LAYOUT_BASE.copy()
    
    # 2. 用自定义的值安全地覆盖/新增键值对
    layout_args.update({
        "height": 200,
        "margin": dict(l=20, r=20, t=40, b=10)
    })
    
    # 3. 将最终的参数字典一次性解包传给 update_layout
    fig.update_layout(**layout_args)
    
    return fig
    # fig.update_layout(**LAYOUT_BASE, height=200, margin=dict(l=20, r=20, t=40, b=10))
    # return fig


def make_radar_chart(df: pd.DataFrame) -> go.Figure:
    metrics = df["指标"].tolist()
    fig = go.Figure()
    for col, color in [("优化前", COLORS["gray"]), ("平峰场景优化后", COLORS["green"]),
                       ("异常场景优化后", COLORS["primary"])]:
        vals = df[col].tolist() + [df[col].iloc[0]]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=metrics + [metrics[0]],
            fill="toself", name=col,
            line=dict(color=color),
            fillcolor=color.replace(")", ",0.15)").replace("rgb", "rgba") if "rgb" in color else color,
        ))
    fig.update_layout(**LAYOUT_BASE, title="双网协同优化效果雷达图",
                      polar=dict(radialaxis=dict(visible=True, range=[0, 25])),
                      legend=dict(orientation="h", y=-0.1))
    return fig


def make_synergy_radar_chart(data: dict[str, list[float]]) -> go.Figure:
    metrics = data["指标"]
    fig = go.Figure()
    for name, color in [("GEP", COLORS["primary"]), ("CCRP", COLORS["orange"])]:
        values = data[name] + [data[name][0]]
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=metrics + [metrics[0]],
            fill="toself",
            name=name,
            line=dict(color=color),
            hovertemplate="%{theta}<br>%{fullData.name}: %{r:.4f}<extra></extra>",
        ))
    fig.update_layout(
        **LAYOUT_BASE,
        title="双网协同效果雷达图",
        polar=dict(radialaxis=dict(visible=True)),
        legend=dict(orientation="h", y=-0.1),
    )
    return fig


def make_kpi_bar(kpi: dict) -> go.Figure:
    labels = list(kpi.keys())
    values = list(kpi.values())
    colors = [COLORS["primary"] if v >= 8 else COLORS["orange"] for v in values]
    fig = go.Figure(go.Bar(x=labels, y=values, marker_color=colors,
                           text=[f"{v}%" for v in values], textposition="outside"))
    fig.add_hline(y=8, line_dash="dash", line_color=COLORS["red"],
                  annotation_text="目标基线 8%", annotation_position="right")
    fig.update_layout(**LAYOUT_BASE, title="关键指标达成情况",
                      yaxis=dict(title="改善幅度 (%)", range=[0, 30]))
    return fig
