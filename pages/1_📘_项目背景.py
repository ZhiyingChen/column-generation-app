import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import patches
import pandas as pd
from web import function

# 渲染语言栏
function.render_language_selector()
lang, T = function.get_language_dict("doc")

# 页面标题
st.title(T["title"])
st.markdown("---")

# 纸卷切割示意图函数
def draw_paper_roll_cutting():
    fig, ax = plt.subplots(figsize=(10, 2))
    original_roll = patches.Rectangle((0, 0), 5450, 100, facecolor='#a8dadc', edgecolor='#1d3557')
    ax.add_patch(original_roll)
    ax.text(5450 / 2, 50, 'Original (5450mm)', ha='center', va='center', fontsize=10, color='#1d3557')
    cut_positions = [1500, 3300, 5450]
    for pos in cut_positions[:-1]:
        ax.plot([pos, pos], [0, 100], 'r-', linewidth=2)
    segments = [(0, 1500, '1500mm'), (1500, 3300, '1800mm'), (3300, 5450, '2150mm')]
    for start, end, label in segments:
        ax.text((start + end) / 2, 120, label, ha='center', fontsize=9)
    ax.text(5450 - 100, 70, 'left: 0mm', ha='right', fontsize=9, color='#e63946')
    ax.set_xlim(0, 5450)
    ax.set_ylim(0, 150)
    ax.axis('off')
    ax.set_title('Sample Display (2 cut 3 pieces)', pad=20, fontsize=12)
    return fig

# 切割方案对比表格函数
def show_cutting_comparison():
    data = {
        "Cutting Plan": ["Plan A", "Plan B", "Plan C"],
        "Cut Method": ["1500+1800+2150", "1800+2450", "2250+2150+1000"],
        "Edge Loss (mm)": ['0', '-', '50'],
        "Surplus (mm)": ['-', '1200', '-'],
        "Raw Material Efficiency": ["100%", "78%", "99%"],
        "Applicable Scenario": ["Exact Match Demand", "Excess Supply Future Demand", "Minor Edge Loss"]
    }
    df = pd.DataFrame(data)
    st.dataframe(df.style.highlight_min(subset=["Raw Material Efficiency"], color='#a8dadc'), use_container_width=True)

# 问题描述
st.subheader(T["problem_header"])
st.markdown(T["problem_text"])

# 示意图
st.markdown("#### " + T["diagram_header"])
st.pyplot(draw_paper_roll_cutting())

# 对比表格
st.markdown("#### " + T["comparison_header"])
show_cutting_comparison()

# 问题假设
st.subheader(T["assumption_header"])
st.markdown(T["assumption_text"])

# 约束条件
st.markdown(T["constraint_header"])
col1, col2 = st.columns(2)
with col1:
    st.markdown(T["tech_constraints"])
    st.markdown(T["tech_constraints_text"])
with col2:
    st.markdown(T["biz_constraints"])
    st.markdown(T["biz_constraints_text"])

# 输出格式示例
st.markdown(T["output_note"])
with st.expander(T["output_example"], expanded=True):
    st.markdown("""
    | Total Cuts | Cut Length 1 | Cut Length 2 | Cut Length 3 | Cut Length 4 | Cut Length 5 | Sets | Original Width | Surplus | Edge Loss |
    |------------|--------------|--------------|--------------|--------------|--------------|------|----------------|---------|-----------|
    | 3          | 1500         | 1800         | 2150         | -            | -            | 2    | 5450           | -       | 0         |
    | 2          | 1800         | 2450         | -            | -            | -            | 1    | 5450           | 1200    | -         |
    | 2          | 2250         | 2150         | -            | -            | -            | 38   | 5450           | 1000    | -         |
    """)
    st.caption(T["output_caption"])

# 页脚
function.render_footer()
