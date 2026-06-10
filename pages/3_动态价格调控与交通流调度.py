import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pandas as pd
import streamlit as st
from utils.excel_data import (
    get_kpi_comparison, get_peak_area_load_series, get_price_guidance_series,
    get_synergy_radar_data, get_traffic_dynamic_records, load_training_curve_series
)
from utils.chart_helpers import (
    make_excel_traffic_map, make_gauge, make_peak_load_chart,
    make_price_guidance_chart, make_traffic_congestion_heatmap,
    make_synergy_radar_chart, make_training_curve_chart
)

st.set_page_config(page_title="动态价格调控与交通流调度", page_icon="🔄", layout="wide")

with st.sidebar:
    st.markdown("### 🔄 协同调度系统")
    st.markdown("---")
    scenario = st.selectbox("仿真场景", ["平峰场景", "异常场景"],
                            index=0 if st.session_state.get("scenario", "平峰") == "平峰" else 1)
    scenario_key = "平峰" if scenario == "平峰场景" else "异常"
    st.session_state["scenario"] = scenario_key
    st.markdown("---")
    st.markdown("**调度算法**")
    st.markdown("- GEP")
    st.markdown("- CCRP")
    st.markdown("---")
    st.page_link("app.py", label="← 返回首页")

st.title("🔄 动态价格调控与公共交通流调度")
st.caption("基于协同与博弈的双网平衡智能调度 · 电网 + 路网")

if scenario_key == "异常":
    st.warning("⚠️ 当前为异常场景：早晚高峰出现需求尖峰，部分路段严重拥堵")

# KPI 仪表盘
kpi = get_kpi_comparison(scenario_key)
g1, g2, g3, g4 = st.columns(4)
with g1:
    st.plotly_chart(make_gauge(kpi["拥堵时间减少"], "交通拥堵时间减少", "%"),
                    use_container_width=True)
with g2:
    st.plotly_chart(make_gauge(kpi["峰值负荷降低"], "电网峰值负荷降低", "%"),
                    use_container_width=True)
with g3:
    st.plotly_chart(make_gauge(kpi["电网局部压力降低"], "电网局部压力降低", "%"),
                    use_container_width=True)
with g4:
    st.plotly_chart(make_gauge(kpi["调度效率提升"], "调度效率提升", "%"),
                    use_container_width=True)

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["⚡ 双网调控", "🚌 交通流调度", "🔗 双网协同效果"])

# ── Tab 1: 双网调控 ────────────────────────────────────────────────────────────
with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        gep_series = get_price_guidance_series(scenario_key, "gep")
        st.plotly_chart(
            make_price_guidance_chart(gep_series, "GEP动态价格引导指数曲线"),
            use_container_width=True,
        )
    with col_b:
        ccrp_series = get_price_guidance_series(scenario_key, "ccrp")
        st.plotly_chart(
            make_price_guidance_chart(ccrp_series, "CCRP动态价格引导指数曲线"),
            use_container_width=True,
        )

    st.markdown("---")
    col_load_a, col_load_b = st.columns(2)
    with col_load_a:
        gep_load_series = get_peak_area_load_series(scenario_key, "gep")
        st.plotly_chart(
            make_peak_load_chart(gep_load_series, "GEP电网峰值片区负荷曲线"),
            use_container_width=True,
        )
    with col_load_b:
        ccrp_load_series = get_peak_area_load_series(scenario_key, "ccrp")
        st.plotly_chart(
            make_peak_load_chart(ccrp_load_series, "CCRP电网峰值片区负荷曲线"),
            use_container_width=True,
        )

    st.markdown("---")
    col_c, col_d = st.columns([3, 2])
    with col_c:
        training_series = load_training_curve_series()
        st.plotly_chart(make_training_curve_chart(training_series), use_container_width=True)
    with col_d:
        st.markdown("**协同博弈调度说明**")
        st.markdown("""
        - **电网侧**：最小化峰值负荷，降低电网局部压力，动态价格引导充电行为
        - **交通侧**：最小化拥堵时间，提升调度效率，优化汽车行驶路线
        """)
        st.metric("峰值负荷削减", f"{kpi['峰值负荷降低']}%", "优化前后对比")
        st.metric("拥堵时间减少", f"{kpi['拥堵时间减少']}%", "优化前后对比")

# ── Tab 2: 交通流调度 ──────────────────────────────────────────────────────────
with tab2:
    control_a, control_b = st.columns([1, 1])
    with control_a:
        selected_rule_label = st.selectbox("调度算法", ["GEP", "CCRP"], index=0)
    with control_b:
        selected_block = st.selectbox("时间块", list(range(25)), index=0)

    selected_rule = selected_rule_label.lower()
    traffic_records = get_traffic_dynamic_records(scenario_key, selected_rule, selected_block)
    st.plotly_chart(
        make_excel_traffic_map(
            traffic_records,
            f"{scenario_key}场景 {selected_rule_label} 时间块{selected_block} 城市路网交通流量图(颜色=拥堵度，线宽=流量)",
        ),
        use_container_width=True,
    )

    congested_count = sum(1 for record in traffic_records if record["congestion_index"] > 0.75)
    total_flow = sum(record["flow_count"] for record in traffic_records)
    avg_congestion = sum(record["congestion_index"] for record in traffic_records) / len(traffic_records)
    metric_a, metric_b, metric_c, metric_d = st.columns(4)
    metric_a.metric("路段数量", f"{len(traffic_records)}")
    metric_b.metric("总流量", f"{total_flow:.0f}")
    metric_c.metric("平均拥堵指数", f"{avg_congestion:.3f}")
    metric_d.metric("高拥堵路段", f"{congested_count}")

    st.markdown("---")
    heatmap_records = []
    for block_id in range(25):
        heatmap_records.extend(get_traffic_dynamic_records(scenario_key, selected_rule, block_id))
    top_records = sorted(traffic_records, key=lambda item: item["congestion_index"], reverse=True)[:10]
    heat_col, table_col = st.columns([3, 2])
    with heat_col:
        st.plotly_chart(
            make_traffic_congestion_heatmap(heatmap_records),
            use_container_width=True,
        )
    with table_col:
        st.markdown("**高拥堵路段 Top 10**")
        top_df = pd.DataFrame([
            {
                "边ID": record["edge_id"],
                "流量（辆）": int(record["flow_count"]),
                "拥堵指数": round(record["congestion_index"], 3),
            }
            for record in top_records
        ])
        st.dataframe(
            top_df.style.set_properties(**{"text-align": "center"}).set_table_styles([
                {"selector": "th", "props": [("text-align", "center")]},
            ]),
            use_container_width=True,
            hide_index=True,
        )

# ── Tab 3: 双网协同效果 ────────────────────────────────────────────────────────
with tab3:
    radar_data = get_synergy_radar_data(scenario_key)
    st.plotly_chart(make_synergy_radar_chart(radar_data), use_container_width=True)

    st.markdown("---")
    st.markdown("**双网协同调度核心结论**")
    c1, c2, c3 = st.columns(3)
    c1.success(f"🚌 交通拥堵时间减少 **{kpi['拥堵时间减少']}%**\n\n超过8%目标基线")
    c2.success(f"⚡ 电网峰值负荷降低 **{kpi['峰值负荷降低']}%**\n\n超过8%目标基线")
    c3.info(f"🔗 双网协同效益\n\n电网局部压力降低 {kpi['电网局部压力降低']}%，调度效率提升 {kpi['调度效率提升']}%")
