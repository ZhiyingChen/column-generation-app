import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import patches
import pandas as pd

# 设置页面标题和图标
st.set_page_config(page_title="纸卷切割优化问题背景", page_icon="📘")

# 自定义CSS样式
st.markdown("""
<style>
    .main {
        max-width: 1000px;
        padding: 2rem;
    }
    .stMarkdown h2 {
        color: #2e86ab;
        border-bottom: 2px solid #2e86ab;
        padding-bottom: 0.3rem;
    }
    .stMarkdown h3 {
        color: #3d5a80;
    }
    .stDataFrame {
        font-size: 0.9rem;
    }
    .stImage {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# 标题部分
st.title("📘 纸卷切割优化问题背景")
st.markdown("---")


# 1. 纸卷切割示意图
def draw_paper_roll_cutting():
    fig, ax = plt.subplots(figsize=(10, 2))

    # 原始纸卷
    original_roll = patches.Rectangle((0, 0), 5450, 100, facecolor='#a8dadc', edgecolor='#1d3557')
    ax.add_patch(original_roll)
    ax.text(5450 / 2, 50, 'Original (5450mm)', ha='center', va='center', fontsize=10, color='#1d3557')

    # 切割示例1
    cut_positions = [1500, 3300, 5450]  # 1500+1800=3300, 3300+2150=5450
    for pos in cut_positions[:-1]:
        ax.plot([pos, pos], [0, 100], 'r-', linewidth=2)

    # 标注切割段
    segments = [(0, 1500, '1500mm'), (1500, 3300, '1800mm'),
                (3300, 5450, '2150mm')]
    for start, end, label in segments:
        ax.text((start + end) / 2, 120, label, ha='center', fontsize=9)

    # 边损标注
    ax.text(5450 - 100, 70, 'left: 0mm', ha='right', fontsize=9, color='#e63946')

    ax.set_xlim(0, 5450)
    ax.set_ylim(0, 150)
    ax.axis('off')
    ax.set_title('Sample Display (2 cut 3 pieces)', pad=20, fontsize=12)

    return fig


# 2. 切割方案对比表格
def show_cutting_comparison():
    data = {
        "切割方案": ["方案A", "方案B", "方案C"],
        "切割方式": ["1500+1800+2150", "1800+2450", "2250+2150+1000"],
        "边损(mm)": [0, '-', 50],
        "余量(mm)": ['-', 1200, '-'],
        "原料使用效率": ["100%", "78%", "99%"],
        "适用场景": ["完全匹配需求", "存在余量供应后续需求", "存在少量边损"]
    }
    df = pd.DataFrame(data)
    st.dataframe(df.style.highlight_min(subset=["原料使用效率"], color='#a8dadc'),
                 use_container_width=True)


# 页面布局
st.subheader("📋 问题描述")
st.markdown("""
在纸卷制造业中，需要将统一长度的纸卷原料切割成不同长度，从而满足不同产品或者不同用户的需求。由于需求长度不同，切割方式有多种，而且每种切割方式所得到的子纸卷长度和数量不同，剩余的纸卷废料长度也不同。

- **决策**：在每天需求确定的情况下，如何进行纸卷的裁切
- **目标**：在满足当日需求的前提下，使得当日裁切后剩余的废弃纸卷长度最小
""")

st.subheader("📏 纸卷切割示意图")
st.pyplot(draw_paper_roll_cutting())

st.subheader("📊 切割方案对比")
show_cutting_comparison()

# 问题假设
st.subheader("📌 问题假设")
st.markdown("""
为简化并清晰描述模型，对生产场景做出如下假设：
- 每天的需求提前确定且已知
- 原始纸卷长度固定（以5450mm为例）
- 每天的产能足以保证完成当天所有需求
- 切割后的子纸卷长度必须精确匹配需求
- 边损和余量计算遵循预设规则

#### 名词解释

- 边损：对原纸卷而言，裁切过后，剩余下来无法供应给需求的边角料记做边损，边损可以设置上下限（如 (0, 50) ）
- 余量：对原纸卷而言，裁切过后，剩余下来可以供应给需求的边角料记做余量，余量可以设置下限（如 1500 ）
- 补库：每日裁切后多于需求部分的纸卷，都要进行补库的操作：在当日之后整个时间周期内的需求中去找，首先选择需求最高的补库，如果其需求长度超过了剩余边损，则再去选择需求第二高的，依次类推，直到剩余边损无法再补库为止

""")

# 切割限制说明
st.subheader("🔪 切割约束条件")
col3, col4 = st.columns(2)
with col3:
    st.markdown("""
    ### 技术限制
    - 最大切割次数：4刀（最多5段）
    - 边损范围：0-50mm
    - 余量下限：1000mm
    """)

with col4:
    st.markdown("""
    ### 业务规则
    - 补库机制：多余纸卷优先补充高需求
    - 需求优先级：按订单紧急程度排序
    - 特殊标记：非当天补库纸卷需标注
    """)

# 示例输出


st.markdown("""
 - 每天的计算结果，拟采用如下的表格格式 (注：需要特殊标注出哪些是非当天的补库纸卷)
 """
)
with st.expander("📁 示例输出格式", expanded=True):
    st.markdown("""
    | 总刀数 | 切割长度1 | 切割长度2 | 切割长度3 | 切割长度4 | 切割长度5 | 套数 | 原纸幅宽 | 余量 | 边损 |
    |--------|-----------|-----------|-----------|-----------|-----------|------|----------|------|------|
    | 3      | 1500      | 1800      | 2150      | -         | -         | 2    | 5450     | -    | 0    |
    | 2      | 1800      | 2450      | -         | -         | -         | 1    | 5450     | 1200 | -    |
    | 2      | 2250      | 2150      | -         | -         | -         | 38   | 5450     | 1000 | -    |
    """)
    st.caption("注：'-'表示该位置无切割长度，套数表示使用该切割方案的次数")

# 页脚
st.markdown("---")
