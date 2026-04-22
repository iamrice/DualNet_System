import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import streamlit as st
from utils.mock_data import gen_energy_timeseries, gen_model_comparison, gen_spatial_grid
from utils.chart_helpers import (
    make_timeseries_chart, make_error_boxplot, make_bar_comparison, make_city_heatmap
)

st.set_page_config(page_title="双网能耗模型与时空预测", page_icon="📊", layout="wide")

with st.sidebar:
    st.markdown("### 📊 双网能耗模型")
    st.markdown("---")
    scenario = st.selectbox("仿真场景", ["平峰场景", "异常场景"],
                            index=0 if st.session_state.get("scenario", "平峰") == "平峰" else 1)
    scenario_key = "平峰" if scenario == "平峰场景" else "异常"
    st.session_state["scenario"] = scenario_key
    st.markdown("---")
    st.page_link("app.py", label="← 返回首页")

st.title("📊 双网能耗模型与多尺度时空预测")
st.caption("数据驱动的双网能耗建模 · 短期/长期多尺度时空预测")

# KPI 卡片
df_cmp = gen_model_comparison()
our = df_cmp[df_cmp["模型"] == "本文模型"].iloc[0]
best_baseline = df_cmp[df_cmp["模型"] != "本文模型"]["MAPE (%)"].min()
improvement = round((best_baseline - our["MAPE (%)"]) / best_baseline * 100, 1)

k1, k2, k3, k4 = st.columns(4)
k1.metric("MAE", f"{our['MAE (kWh)']} kWh", "本文模型")
k2.metric("RMSE", f"{our['RMSE (kWh)']} kWh", "本文模型")
k3.metric("MAPE", f"{our['MAPE (%)']}%", "本文模型")
k4.metric("较最优基线改进", f"{improvement}%↑", f"基线最优 {best_baseline}%")

st.markdown("---")

tab1, tab2, tab3 = st.tabs(["📈 时序预测", "🗺️ 空间热力图", "📊 模型对比"])

with tab1:
    df_ts = gen_energy_timeseries(scenario_key)
    st.plotly_chart(make_timeseries_chart(df_ts), use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.plotly_chart(make_error_boxplot(df_ts), use_container_width=True)
    with col_b:
        st.markdown("**预测误差统计**")
        for model in ["本文模型", "LSTM", "ARIMA"]:
            err = (df_ts[model] - df_ts["实际值"]).abs()
            st.markdown(f"- **{model}**: MAE={err.mean():.1f} kWh, Max={err.max():.1f} kWh")

        if scenario_key == "异常":
            st.warning("⚠️ 异常场景：第20-22天出现能耗尖峰，本文模型仍保持较低误差")
        else:
            st.success("✅ 平峰场景：各模型预测稳定，本文模型误差最小")

with tab2:
    df_grid = gen_spatial_grid()
    st.plotly_chart(make_city_heatmap(df_grid), use_container_width=True)
    st.caption("城市20×20网格能耗密度分布，市中心区域能耗密度显著高于郊区")

with tab3:
    col_left, col_right = st.columns([3, 2])
    with col_left:
        st.plotly_chart(make_bar_comparison(df_cmp), use_container_width=True)
    with col_right:
        st.markdown("**模型性能对比表**")
        st.dataframe(
            df_cmp.style.highlight_min(subset=["MAE (kWh)", "RMSE (kWh)", "MAPE (%)"],
                                       color="#c8e6c9"),
            use_container_width=True, hide_index=True,
        )
        st.success(f"本文模型 MAPE 仅 {our['MAPE (%)']}%，较最优基线（Transformer {best_baseline}%）改进 **{improvement}%**，超过5%目标")
