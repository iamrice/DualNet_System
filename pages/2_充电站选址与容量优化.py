import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
import folium
from streamlit_folium import st_folium
from utils.mock_data import (
    gen_charging_stations, gen_optimization_convergence,
    gen_capacity_allocation, gen_uncertainty_scenarios
)
from utils.chart_helpers import make_convergence_chart, make_stacked_bar, make_scatter_scenarios

st.set_page_config(page_title="充电站选址与容量优化", page_icon="🗺️", layout="wide")

with st.sidebar:
    st.markdown("### 🗺️ 充电站选址优化")
    st.markdown("---")
    st.markdown("**优化方法**：鲁棒优化")
    st.markdown("**不确定性场景**：50个")
    st.markdown("**候选站点**：30个")
    st.markdown("**优选站点**：8个")
    st.markdown("---")
    st.page_link("app.py", label="← 返回首页")

st.title("🗺️ 鲁棒性充电站选址与容量优化")
st.caption("大时空尺度不确定场景下的充电基础设施规划")

candidates, selected = gen_charging_stations()

# KPI
k1, k2, k3, k4 = st.columns(4)
k1.metric("候选站点", "30 个", "全市覆盖")
k2.metric("优选站点", "8 个", "鲁棒优化结果")
k3.metric("总装机容量", f"{selected['容量 (kW)'].sum():.0f} kW", "快+慢+缓冲")
k4.metric("需求覆盖率", "94.2%", "鲁棒场景下")

st.markdown("---")

col_map, col_charts = st.columns([6, 4])

with col_map:
    st.markdown("**城市充电站选址地图**")
    m = folium.Map(location=[31.25, 121.45], zoom_start=11, tiles="CartoDB positron")

    # 候选站点（灰色圆圈）
    for _, row in candidates.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=5,
            color="#90A4AE",
            fill=True,
            fill_color="#90A4AE",
            fill_opacity=0.5,
            tooltip=f"候选站点 {row['站点ID']} | 需求: {row['需求量 (kW)']:.0f} kW",
        ).add_to(m)

    # 优选站点（蓝色图标）
    for _, row in selected.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            tooltip=f"✅ {row['站点ID']} | 容量: {row['容量 (kW)']} kW | 快充: {row['快充桩数']}桩",
            icon=folium.Icon(color="blue", icon="bolt", prefix="fa"),
        ).add_to(m)

    # 图例说明
    legend_html = """
    <div style="position:fixed;bottom:30px;left:30px;z-index:1000;background:white;
                padding:10px;border-radius:8px;border:1px solid #ccc;font-size:12px;">
        <b>图例</b><br>
        <span style="color:#90A4AE">●</span> 候选站点 (30个)<br>
        <span style="color:#1E88E5">📍</span> 优选站点 (8个)
    </div>
    """
    m.get_root().html.add_child(folium.Element(legend_html))
    st_folium(m, width=None, height=480, returned_objects=[])

with col_charts:
    df_conv = gen_optimization_convergence()
    st.plotly_chart(make_convergence_chart(df_conv, "鲁棒优化 vs 确定性优化收敛曲线"),
                    use_container_width=True)

    df_unc = gen_uncertainty_scenarios()
    st.plotly_chart(make_scatter_scenarios(df_unc), use_container_width=True)

st.markdown("---")
st.markdown("**充电站容量分配详情**")
col_bar, col_table = st.columns([3, 2])
df_cap = gen_capacity_allocation()
with col_bar:
    st.plotly_chart(make_stacked_bar(df_cap), use_container_width=True)
with col_table:
    st.dataframe(df_cap, use_container_width=True, hide_index=True)
    st.info("鲁棒优化在最坏场景下仍保证充电需求满足率 ≥ 90%，较确定性优化提升约 15%")
