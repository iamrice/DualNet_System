import streamlit as st

st.set_page_config(
    page_title="双网平衡低碳交通流智能调度系统",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── 全局样式 ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
.module-card {
    background: linear-gradient(135deg, #f8f9fa 0%, #e8f4fd 100%);
    border: 1px solid #1E88E5;
    border-radius: 12px;
    padding: 24px;
    height: 100%;
    transition: box-shadow 0.2s;
}
.module-card:hover { box-shadow: 0 4px 20px rgba(30,136,229,0.25); }
.module-title { color: #1E88E5; font-size: 1.1rem; font-weight: 700; margin-bottom: 8px; }
.module-badge { background: #1E88E5; color: white; border-radius: 20px;
                padding: 2px 10px; font-size: 0.75rem; display: inline-block; margin-bottom: 10px; }
.module-metric { color: #43A047; font-size: 0.85rem; margin-top: 10px; font-style: italic; }
.arrow-box { display: flex; align-items: center; justify-content: center; height: 100%; }
.arrow { font-size: 2.5rem; color: #1E88E5; }
.hero-title { font-size: 2rem; font-weight: 800; color: #1E88E5; text-align: center; margin-bottom: 4px; }
.hero-sub { text-align: center; color: #546E7A; margin-bottom: 32px; }
</style>
""", unsafe_allow_html=True)

# ── 侧边栏 ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚡ 双网智能调度系统")
    st.markdown("---")
    scenario = st.selectbox("选择仿真场景", ["平峰场景", "异常场景"], key="global_scenario")
    st.session_state["scenario"] = "平峰" if scenario == "平峰场景" else "异常"
    st.markdown("---")
    st.markdown("**系统架构**")
    st.markdown("- 电网 (Power Grid)")
    st.markdown("- 路网 (Road Network)")
    st.markdown("- 双网协同调度")
    st.markdown("---")
    st.caption("© 2024 双网平衡低碳交通流系统")

# ── 主页内容 ──────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">⚡ 双网平衡的低碳交通流系统智能调度系统</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">融合电网与路网，实现新能源公共交通的智能协同调度</div>', unsafe_allow_html=True)

# 流程图说明
st.markdown("#### 系统模块关联")
st.markdown("""
> **页面1** 提供数据驱动的双网能耗预测模型，为后续优化提供模型支撑 →
> **页面2** 基于预测结果进行鲁棒性充电站选址，为协同调度提供场景支撑 →
> **页面3** 综合前两页成果，实现动态价格调控与交通流协同调度
""")

st.markdown("---")

# 三模块卡片
col1, arrow1, col2, arrow2, col3 = st.columns([4, 0.6, 4, 0.6, 4])

with col1:
    st.markdown("""
<div class="module-card">
  <div class="module-badge">模块 1 · 预测层</div>
  <div class="module-title">📊 双网能耗模型与多尺度时空预测</div>
  <p style="color:#37474F;font-size:0.9rem;">
    构建数据驱动的双网（电网+路网）能耗模型，支持短期（小时级）与长期（日/周级）多尺度时空预测，
    为充电站规划和调度决策提供精准的能耗预测基础。
  </p>
  <div class="module-metric">✅ 预测误差较现有方法降低 5%+</div>
  <div class="module-metric">✅ 覆盖平峰与异常两种典型场景</div>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/1_双网能耗模型与时空预测.py", label="进入页面 1 →", icon="📊")

with arrow1:
    st.markdown('<div class="arrow-box"><div class="arrow">→</div></div>', unsafe_allow_html=True)

with col2:
    st.markdown("""
<div class="module-card">
  <div class="module-badge">模块 2 · 优化层</div>
  <div class="module-title">🗺️ 鲁棒性充电站选址与容量优化</div>
  <p style="color:#37474F;font-size:0.9rem;">
    在大时空尺度不确定场景下，利用鲁棒优化方法确定充电站最优选址与容量配置，
    有效应对需求波动与可再生能源不确定性，为协同调度提供基础设施支撑。
  </p>
  <div class="module-metric">✅ 鲁棒优化应对50+不确定性场景</div>
  <div class="module-metric">✅ 快充/慢充/缓冲容量精细化配置</div>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/2_充电站选址与容量优化.py", label="进入页面 2 →", icon="🗺️")

with arrow2:
    st.markdown('<div class="arrow-box"><div class="arrow">→</div></div>', unsafe_allow_html=True)

with col3:
    st.markdown("""
<div class="module-card">
  <div class="module-badge">模块 3 · 调度层</div>
  <div class="module-title">🔄 动态价格调控与公共交通流调度</div>
  <p style="color:#37474F;font-size:0.9rem;">
    基于协同与博弈理论，设计自适应动态价格策略与大规模新能源公共交通流调度算法，
    实现电网与路网的双网平衡，落脚于城市级交通与电力系统的协同优化。
  </p>
  <div class="module-metric">✅ 城市交通拥堵时间减少 8%+</div>
  <div class="module-metric">✅ 电网峰值负荷降低 8%+</div>
</div>
""", unsafe_allow_html=True)
    st.page_link("pages/3_动态价格调控与交通流调度.py", label="进入页面 3 →", icon="🔄")

st.markdown("---")

# 底部统计概览
st.markdown("#### 系统总览指标")
m1, m2, m3, m4 = st.columns(4)
m1.metric("预测误差改善", "5.6%↑", "较LSTM基线")
m2.metric("充电站优选", "8 / 30", "候选站点中优选")
m3.metric("交通拥堵减少", "8.3%", "城市级仿真验证")
m4.metric("电网峰值降低", "8.7%", "24h负荷优化")
