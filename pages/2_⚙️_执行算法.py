import streamlit as st
import pandas as pd
import os
import subprocess
import matplotlib.pyplot as plt
import matplotlib
import pylab
import shutil
import sys

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
    请在“执行算法”页面上传符合格式的输入文件。
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

st.header("📥 上传文件")
col1, col2 = st.columns(2)

with col1:
    global_params_file = st.file_uploader("📄 上传全局参数文件（global_params.csv）", type="csv", key="global")
with col2:
    demand_file = st.file_uploader("📄 上传需求文件（demand.csv）", type="csv", key="demand")

# 示例数据展示
with st.expander("📄 示例数据：global_params.csv"):
    try:
        example_global_params = pd.read_csv("data/global_params.csv")
        st.dataframe(example_global_params)
        st.download_button(
            label="📥 下载全局参数示例",
            data=example_global_params.to_csv(index=False).encode('utf-8'),
            file_name="global_params.csv",
            mime="text/csv"
        )
    except FileNotFoundError:
        st.warning("未找到 data/global_params.csv 示例文件")

with st.expander("📄 示例数据：demand.csv"):
    try:
        example_demand = pd.read_csv("data/demand.csv")
        st.dataframe(example_demand)
        st.download_button(
            label="📥 下载需求示例",
            data=example_demand.to_csv(index=False).encode('utf-8'),
            file_name="demand.csv",
            mime="text/csv"
        )
    except FileNotFoundError:
        st.warning("未找到 data/demand.csv 示例文件")

# 1. 上传路径
if 'win' in sys.platform:
    upload_dir = "./tmp"
    if not os.path.exists(upload_dir):
        os.mkdir(upload_dir)
else:
    upload_dir = "/tmp"


def clean_upload_dir(upload_dir: str = "/tmp"):
    import os, glob, shutil
    # 删除 main.py
    main_path = os.path.join(upload_dir, "main.py")
    if os.path.exists(main_path):
        os.remove(main_path)
    # 删除 source 文件夹
    source_path = os.path.join(upload_dir, "source")
    if os.path.exists(source_path) and os.path.isdir(source_path):
        shutil.rmtree(source_path)
    # 删除所有 .csv 文件
    for f in glob.glob(os.path.join(upload_dir, "*.csv")):
        try:
            os.remove(f)
        except Exception as e:
            print(f"⚠️ 删除失败：{f}, 错误：{e}")


clean_upload_dir(
    upload_dir=upload_dir
)
# 2. 把 main.py 和其它必要文件复制进去
# 找到 pages 的上一级目录
project_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# 先清空 upload_dir

shutil.copy(os.path.join(project_dir, "main.py"), os.path.join(upload_dir, "main.py"))
# main.py 有依赖的 source/ 等子目录，也一并复制过去（可用 shutil.copytree）
shutil.copytree(os.path.join(project_dir, "source"), os.path.join(upload_dir, "source"))

# 3. 再复制上传的文件
if global_params_file:
    if global_params_file:
        try:
            save_path = os.path.join(upload_dir, "global_params.csv")
            with open(save_path, "wb") as f:
                f.write(global_params_file.read())
            st.success(f"✅ 上传成功：{save_path}")
        except Exception as e:
            st.error(f"❌ 文件保存失败：{e}")

if demand_file:
    with open(os.path.join(upload_dir, "demand.csv"), "wb") as f:
        f.write(demand_file.read())

# 判断是否禁用运行按钮
run_disabled = not (global_params_file and demand_file)

# 显示运行按钮
if st.button("🚀 运行算法", disabled=run_disabled,
             help="请先上传所需的两个输入文件" if run_disabled else "点击运行算法"):
    with st.spinner("算法运行中，请稍候..."):
        try:
            # 运行 main.py
            result = subprocess.run(
                ["python", "main.py"],
                cwd=upload_dir,
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                st.success("✅ 算法运行完成！")
            else:
                st.error("❌ 算法运行失败")
                st.text(result.stderr)
        except Exception as e:
            st.error(f"运行出错：{e}")

    st.markdown("---")
    st.header("📊 输出结果")

    # 展示输出文件
    output_dir = os.path.join(upload_dir, "output")
    output_files = {
        "切割方案 (solutionOut.csv)": "solutionOut.csv",
        "KPI指标 (kpiOut.csv)": "kpiOut.csv",
        "供给结果 (supplyOut.csv)": "supplyOut.csv",
        "需求满足情况 (demandOut.csv)": "demandOut.csv",
        "供需匹配 (fulfillmentOut.csv)": "fulfillmentOut.csv"
    }

    sol_df = pd.DataFrame()
    for label, filename in output_files.items():
        path = os.path.join(output_dir, filename)
        if os.path.exists(path):
            with st.expander(f"📄 {label}"):
                df = pd.read_csv(path)
                st.dataframe(df)
                with open(path, "rb") as f:
                    st.download_button(
                        label=f"📥 下载 {filename}",
                        data=f,
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
                    segments = [v for k, v in sample_row.items() if "切割方案" in k and pd.notna(v)]
                    labels = [f"段{i} ({width})" for i, width in enumerate(segments)]

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
                    ax.set_title(f"方案 {i} - 母卷切割段宽示意图")
                    st.pyplot(fig)
