import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from source.context import Context
from web import function

# 渲染语言栏
function.render_language_selector()
lang, T = function.get_language_dict("algo")

# 页面标题
st.title(T["page_title"])
st.markdown("---")
st.markdown(T["description"])

# 文件说明
st.header(T["io_header"])

with st.expander(T["global_param_expander"]):
    st.markdown(T["global_param_table"])

with st.expander(T["demand_expander"]):
    st.markdown(T["demand_table"])

with st.expander(T["solution_out_expander"]):
    st.markdown(T["solution_out_table"])

with st.expander(T["kpi_out_expander"]):
    st.markdown(T["kpi_out_table"])

with st.expander(T["other_outputs_expander"]):
    st.markdown(T["other_outputs_text"])

# 示例数据展示
st.header(T["example_data_header"])

@st.cache_data
def load_csv(file):
    return pd.read_csv(file)

# 加载示例数据
global_df = load_csv("data/global_params.csv")
demand_df = load_csv("data/demand.csv")

# 可编辑的 DataFrame
with st.expander(T["edit_global_params"]):
    edited_global_df = st.data_editor(global_df, num_rows="dynamic")
    # 下载按钮
    st.download_button(
        label=T["download_global_params"],
        data=edited_global_df.to_csv(index=False).encode('utf-8'),
        file_name="global_params_modified.csv",
        mime="text/csv"
    )

with st.expander(T["edit_demand_data"]):
    edited_demand_df = st.data_editor(demand_df, num_rows="dynamic")
    # 下载按钮
    st.download_button(
        label=T["download_demand_data"],
        data=edited_demand_df.to_csv(index=False).encode('utf-8'),
        file_name="demand_modified.csv",
        mime="text/csv"
    )

# 显示运行按钮
if st.button(T["run_algorithm"]):
    with st.spinner(T["running_algorithm"]):
        try:
            context = Context(
                load_from_file=False,
                param_file_dict={
                    "global_params.csv": edited_global_df,
                    "demand.csv": edited_demand_df
                }
            )
            output_files = context.run()
            st.success(T["algorithm_success"])

        except Exception as e:
            st.error(T["algorithm_error"].format(e))

    st.markdown("---")
    st.header(T["output_results"])

    output_files_label = {
        "kpiOut.csv": T["kpi_metrics"],
        "solutionOut.csv": T["cutting_solutions"],
        "supplyOut.csv": T["supply_results"],
        "demandOut.csv": T["demand_fulfillment"],
        "fulfillmentOut.csv": T["matching_results"]
    }

    # 展示输出文件
    for filename, df in output_files.items():
        if filename == "kpiOut.csv":
            st.subheader(output_files_label[filename])
            st.dataframe(df)

            st.download_button(
                label=f"📥 Download {filename}",
                data=df.to_csv(index=False),
                file_name=filename,
                mime="text/csv"
            )
        else:
            with st.expander(f"📄 {output_files_label[filename]}"):
                st.dataframe(df)

                st.download_button(
                    label=f"📥 Download {filename}",
                    data=df.to_csv(index=False),
                    file_name=filename,
                    mime="text/csv"
                )

        if filename != "solutionOut.csv":
            continue

        sol_df = df.copy()

        if sol_df.empty:
            st.warning(T["empty_solution"])
        else:
            # 可视化前五套方案的切割段宽
            st.subheader(T["cutting_diagrams"])
            for i in range(min(5, len(sol_df))):
                sample_row = sol_df.iloc[i]
                segments = [v for k, v in sample_row.items() if "切割方案" in k and pd.notna(v)]
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
                ax.set_title(f"Solution {i} - Sample Display")  # 如果需要显示中文标题，请替换为英文标题
                st.pyplot(fig)

function.render_footer()