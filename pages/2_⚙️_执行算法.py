import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import pylab
from source.context import Context
from web import function

# 设置使用的字体（需要显示中文的时候使用）
font = {'family': 'SimHei'}
# 设置显示中文,与字体配合使用
matplotlib.rc('font', **font)
matplotlib.rcParams['axes.unicode_minus'] = False
params = {'legend.fontsize': 'x-large',
          'axes.labelsize': 'x-large',
          'axes.titlesize': 'x-large',
          'xtick.labelsize': 'x-large',
          'ytick.labelsize': 'x-large'}
pylab.rcParams.update(params)

st.title("⚙️ 执行卷纸切割算法")

st.markdown(
    """
     请在“执行算法”页面将示例输入文件改成你需要的数据。
    """
)

st.header("📂 输入输出文件说明")

with st.expander("📥 输入文件说明：global_param.csv"):
    st.markdown("""
| 参数名称     | 描述                         | 类型   | 默认值 | 备注                       |
|--------------|------------------------------|--------|--------|----------------------------|
| 原始卷纸长度 | 原纸宽度                     | double | 无     | 例如 5450                  |
| 最大切割次数 | 每卷最多裁剪几次（最多几段） | int    | 无     | 例如 4 表示最多5段        |
| 是否进行补库 | 是否允许将多余部分用于补库   | string | 是/否 | 否表示多余直接浪费        |
| 是否考虑边损 | 是否设置边损上下限           | string | 是/否 | 是表示需填写边损上下限    |
| 边损下限     | 小于该值视为边损             | double | 0      | 较小时可视为浪费          |
| 边损上限     | 大于该值视为余量             | double | 无     | 需考虑余量下限            |
| 余量下限     | 非边损可补库的剩余长度       | double | 无     | 补库判断阈值              |
| 切割方案使用下限 | 某种切割方案至少用几次     | int    | 0      | 防止极端解                |
""")

with st.expander("📥 输入文件说明：demand.csv"):
    st.markdown("""
| 字段名     | 描述               | 类型   | 是否必填 | 备注             |
|------------|--------------------|--------|-----------|------------------|
| 幅宽       | 客户所需纸卷宽度   | double | ✅        | 单位 mm          |
| 订单件数   | 每种幅宽的需求数量 | double | ✅        | 每天若干行       |
| 移库日期   | 该需求所属日期     | string | ✅        | 支持多天数据     |
""")

st.markdown("---")

with st.expander("📤 输出文件说明：solutionOut.csv（切割方案明细）"):
    st.markdown("""
| 字段名             | 描述                           | 类型   |
|--------------------|----------------------------------|--------|
| 日期               | 哪天用的该方案                  | string |
| 切割方案_第1~N段   | 每段的宽度，最多 N+1 段         | double |
| 套数               | 使用该方案多少卷                | int    |
| 原始幅宽           | 原纸宽度，应与输入一致          | double |
| 边损               | 剩余长度 <= 边损下限时记为边损  | double |
| 余量               | 剩余长度 >= 余量下限时记为余量  | double |
| 切割方案编码       | 用于后续匹配、追踪              | int    |
""")

with st.expander("📊 输出文件说明：kpiOut.csv（关键指标）"):
    st.markdown("""
| 字段名           | 描述                     | 类型   |
|------------------|--------------------------|--------|
| 日期             | 哪天的结果               | string |
| 原始纸卷使用个数 | 共用了多少根母卷         | int    |
| 切割方案数量     | 该日使用了多少种方案     | int    |
| 运行时间（秒）   | 算法运行耗时             | double |
""")

with st.expander("📦 输出文件说明：supplyOut.csv / demandOut.csv / fulfillmentOut.csv"):
    st.markdown("""
- `supplyOut.csv`：每种方案每种宽度的供给数量
- `demandOut.csv`：每天每种宽度的实际需求与未满足数
- `fulfillmentOut.csv`：哪个方案在什么日期供给了哪个需求

这些用于分析方案对需求的满足匹配情况，可用于生成追踪表、KPI 和图示。
""")

# 示例数据展示
st.header("📄 示例输入数据（可编辑）")

@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

# 加载示例数据
global_df = load_csv("data/global_params.csv")
demand_df = load_csv("data/demand.csv")

# 可编辑的 DataFrame
with st.expander("📝 编辑全局参数"):
    edited_global_df = st.data_editor(global_df, num_rows="dynamic")
    # 下载按钮
    st.download_button(
        label="📥 下载编辑后的 global_params.csv",
        data=edited_global_df.to_csv(index=False).encode('utf-8'),
        file_name="global_params_modified.csv",
        mime="text/csv"
    )

with st.expander("📝 编辑需求数据"):
    edited_demand_df = st.data_editor(demand_df, num_rows="dynamic")
    # 下载按钮
    st.download_button(
        label="📥 下载编辑后的 demand.csv",
        data=edited_demand_df.to_csv(index=False).encode('utf-8'),
        file_name="demand_modified.csv",
        mime="text/csv"
    )


# 显示运行按钮
if st.button("🚀 运行算法"):
    with st.spinner("算法运行中，请稍候..."):
        try:
            context = Context(
                load_from_file=False,
                param_file_dict={
                    "global_params.csv": edited_global_df,
                    "demand.csv": edited_demand_df
                }
            )
            output_files = context.run(
            )
            st.success("✅ 算法运行完成！")

        except Exception as e:
            st.error(f"❌ 算法运行出错：{e}")

    st.markdown("---")
    st.header("📊 输出结果")

    output_files_label = {
        "kpiOut.csv": "KPI指标 (kpiOut.csv)",
        "solutionOut.csv": "切割方案 (solutionOut.csv)",
        "supplyOut.csv": "供给结果 (supplyOut.csv)",
        "demandOut.csv": "需求满足情况 (demandOut.csv)",
        "fulfillmentOut.csv": "供需匹配 (fulfillmentOut.csv)"
    }

    # 展示输出文件
    for filename, df in output_files.items():
        if filename == "kpiOut.csv":
            st.subheader("🎯 关键指标")
            st.dataframe(df)

            st.download_button(
                label=f"📥 下载 {filename}",
                data=df.to_csv(index=False),
                file_name=filename,
                mime="text/csv"
            )
        else:
            with st.expander("📄 {}".format(output_files_label[filename])):
                st.dataframe(df)

                st.download_button(
                    label=f"📥 下载 {filename}",
                    data=df.to_csv(index=False),
                    file_name=filename,
                    mime="text/csv"
                )

        if filename != "solutionOut.csv":
            continue

        sol_df = df.copy()

        if sol_df.empty:
            st.warning("切割方案为空，请检查输出文件。")
        else:
            # 可视化前五套方案的切割段宽
            st.subheader("📏 切割方案图示")
            for i in range(min(5, len(sol_df))):
                sample_row = sol_df.iloc[i]
                segments = [v for k, v in sample_row.items()
                            if "切割方案" in k and pd.notna(v)]
                labels = [f"Segment {i} ({width})" for i, width in enumerate(segments)]

                fig, ax = plt.subplots(figsize=(10, 1))
                left = 0
                colors = plt.cm.Paired(range(len(segments)))
                for j, width in enumerate(segments):
                    ax.barh(0, width, left=left, height=0.3, color=colors[j], label=labels[j])
                    ax.text(left + width / 2, 0, str(int(width)), ha='center', va='center', color='black',
                            fontsize=8)
                    left += width
                ax.set_xlim(0, left)
                ax.axis('off')
                ax.set_title(f"Solution {i} -Sample Display")  # 如果需要显示中文标题，请替换为英文标题
                st.pyplot(fig)


function.render_footer()