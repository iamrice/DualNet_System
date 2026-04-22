import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from utils.mock_data import (
    gen_grid_load, gen_electricity_price, gen_traffic_flow,
    gen_traffic_heatmap, gen_game_convergence, gen_kpi_comparison, gen_radar_comparison
)
from utils.chart_helpers import (
    make_load_chart, make_price_chart, make_traffic_map, make_traffic_heatmap,
    make_game_convergence, make_gauge, make_radar_chart, make_kpi_bar
)

st.set_page_config(page_title="动态电价调控与交通流调度", page_icon="🔄", layout="wide")

with st.sidebar:
    st.markdown("### 🔄 协同调度系统")
    st.markdown("---")
    scenario = st.selectbox("仿真场景", ["平峰场景", "异常场景"],
                            index=0 if st.session_state.get("scenario", "平峰") == "平峰" else 1)
    scenario_key = "平峰" if scenario == "平峰场景" else "异常"
    st.session_state["scenario"] = scenario_key
    st.markdown("---")
    st.markdown("**调度算法**")
    st.markdown("- 超启发式优化")
    st.markdown("- 迁移演化优化")
    st.markdown("- 协同演化博弈")
    st.markdown("---")
    st.page_link("app.py", label="← 返回首页")

st.title("🔄 动态电价调控与公共交通流调度")
st.caption("基于协同与博弈的双网平衡智能调度 · 电网 + 路网")

if scenario_key == "异常":
    st.warning("⚠️ 当前为异常场景：早晚高峰出现需求尖峰，部分路段严重拥堵")

# KPI 仪表盘
kpi = gen_kpi_comparison(scenario_key)
g1, g2, g3, g4 = st.columns(4)
with g1:
    st.plotly_chart(make_gauge(kpi["拥堵时间减少"], "交通拥堵时间减少", "%"),
                    use_container_width=True)
with g2:
    st.plotly_chart(make_gauge(kpi["峰值负荷降低"], "电网峰值负荷降低", "%"),
                    use_container_width=True)
with g3:
    st.plotly_chart(make_gauge(kpi["电价波动降低"], "电价波动降低", "%"),
                    use_container_width=True)
with g4:
    st.plotly_chart(make_gauge(kpi["调度效率提升"], "调度效率提升", "%"),
                    use_container_width=True)

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["⚡ 电价调控", "🚌 交通流调度", "🔗 双网协同效果"])

# ── Tab 1: 电价调控 ────────────────────────────────────────────────────────────
with tab1:
    col_a, col_b = st.columns(2)
    with col_a:
        df_price = gen_electricity_price(scenario_key)
        st.plotly_chart(make_price_chart(df_price), use_container_width=True)
    with col_b:
        df_load = gen_grid_load(scenario_key)
        st.plotly_chart(make_load_chart(df_load), use_container_width=True)

    st.markdown("---")
    col_c, col_d = st.columns([3, 2])
    with col_c:
        df_game = gen_game_convergence()
        st.plotly_chart(make_game_convergence(df_game), use_container_width=True)
    with col_d:
        st.markdown("**博弈调度说明**")
        st.markdown("""
        - **电网侧**：最小化峰值负荷，通过动态电价引导充电行为
        - **交通侧**：最小化拥堵时间，优化公交发车间隔与路线
        - **博弈均衡**：两侧效用函数在约 **40次迭代** 后收敛至纳什均衡
        - **纳什均衡差距** 收敛至 < 5，验证策略稳定性
        """)
        peak_reduction = round(
            (df_load["基准负荷 (MW)"].max() - df_load["优化后负荷 (MW)"].max()) /
            df_load["基准负荷 (MW)"].max() * 100, 1
        )
        price_reduction = round(
            (df_price["博弈前电价 (元/kWh)"].std() - df_price["博弈后电价 (元/kWh)"].std()) /
            df_price["博弈前电价 (元/kWh)"].std() * 100, 1
        )
        st.metric("峰值负荷削减", f"{peak_reduction}%", "优化前后对比")
        st.metric("电价波动降低", f"{price_reduction}%", "博弈前后对比")

# ── Tab 2: 交通流调度 ──────────────────────────────────────────────────────────
with tab2:
    df_traffic = gen_traffic_flow(scenario_key)
    st.plotly_chart(make_traffic_map(df_traffic), use_container_width=True)

    col_e, col_f = st.columns([3, 2])
    with col_e:
        df_heatmap = gen_traffic_heatmap()
        st.plotly_chart(make_traffic_heatmap(df_heatmap), use_container_width=True)
    with col_f:
        st.markdown("**路网流量统计**")
        st.dataframe(
            df_traffic[["路段ID", "流量 (辆/h)", "拥堵指数"]].sort_values("拥堵指数", ascending=False),
            use_container_width=True, hide_index=True,
        )
        if scenario_key == "异常":
            congested = df_traffic[df_traffic["拥堵指数"] > 0.75]
            st.error(f"⚠️ {len(congested)} 条路段拥堵指数 > 0.75，已触发应急调度预案")
        else:
            st.success("✅ 平峰场景：路网整体运行平稳，无严重拥堵路段")

# ── Tab 3: 双网协同效果 ────────────────────────────────────────────────────────
with tab3:
    col_g, col_h = st.columns(2)
    with col_g:
        df_radar = gen_radar_comparison()
        st.plotly_chart(make_radar_chart(df_radar), use_container_width=True)
    with col_h:
        st.plotly_chart(make_kpi_bar(kpi), use_container_width=True)

    st.markdown("---")
    st.markdown("**双网协同调度核心结论**")
    c1, c2, c3 = st.columns(3)
    c1.success(f"🚌 交通拥堵时间减少 **{kpi['拥堵时间减少']}%**\n\n超过8%目标基线")
    c2.success(f"⚡ 电网峰值负荷降低 **{kpi['峰值负荷降低']}%**\n\n超过8%目标基线")
    c3.info(f"🔗 双网协同效益\n\n电价波动降低 {kpi['电价波动降低']}%，调度效率提升 {kpi['调度效率提升']}%")
