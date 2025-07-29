APP_LANG = {
    "中文": {
        "title": "📦 卷纸切割算法平台",
        "welcome": "欢迎使用！请通过左侧导航栏选择功能页面：",
        "navigation": """
        ### 📘 页面导航说明：
        - **项目背景**：了解问题背景
        - **执行算法**：了解输入输出文件格式，编辑输入文件，运行算法并查看结果
        """
    },
    "English": {
        "title": "📦 Roll Paper Cutting Optimization Platform",
        "welcome": "Welcome! Please use the sidebar to navigate between pages:",
        "navigation": """
        ### 📘 Page Navigation Guide:
        - **Project Background**: Understand the problem context
        - **Run Algorithm**: Learn input/output formats, edit input files, run the algorithm and view results
        """
    }
}

ROLL_DOC_LANG = {
    "中文": {
        "title": "📘 纸卷切割优化问题背景",
        "problem_header": "📋 问题描述",
        "problem_text": """
在纸卷制造业中，需要将统一长度的纸卷原料切割成不同长度，从而满足不同产品或者不同用户的需求。由于需求长度不同，切割方式有多种，而且每种切割方式所得到的子纸卷长度和数量不同，剩余的纸卷废料长度也不同。

- **决策**：在每天需求确定的情况下，如何进行纸卷的裁切
- **目标**：在满足当日需求的前提下，使得当日裁切后剩余的废弃纸卷长度最小
""",
        "diagram_header": "📏 纸卷切割示意图",
        "comparison_header": "📊 切割方案对比",
        "assumption_header": "📌 问题假设",
        "assumption_text": """
为简化并清晰描述模型，对生产场景做出如下假设：
- 每天的需求提前确定且已知
- 原始纸卷长度固定（以5450mm为例）
- 每天的产能足以保证完成当天所有需求
- 切割后的子纸卷长度必须精确匹配需求
- 边损和余量计算遵循预设规则

#### 名词解释

- 边损：对原纸卷而言，裁切过后，剩余下来无法供应给需求的边角料记做边损，边损可以设置上下限（如 (0, 50) ）
- 余量：对原纸卷而言，裁切过后，剩余下来可以供应给需求的边角料记做余量，余量可以设置下限（如 1000 ）
- 补库：每日裁切后多于需求部分的纸卷，都要进行补库的操作：在当日之后整个时间周期内的需求中去找，首先选择需求最高的补库，如果其需求长度超过了剩余边损，则再去选择需求第二高的，依次类推，直到剩余边损无法再补库为止
""",
        "constraint_header": "### 约束条件",
        "tech_constraints": "#### 技术限制",
        "tech_constraints_text": """
    - 最大切割次数：4刀（最多5段）
    - 边损范围：0-50mm
    - 余量下限：1000mm
    """,
        "biz_constraints": "#### 业务规则",
        "biz_constraints_text": """
    - 补库机制：多余纸卷优先补充高需求
    - 需求优先级：按订单紧急程度排序
    - 特殊标记：非当天补库纸卷需标注
    """,
        "output_note": "每天的计算结果，拟采用如下的表格格式 (注：需要特殊标注出哪些是非当天的补库纸卷)",
        "output_example": "📁 示例输出格式",
        "output_caption": "注：'-'表示该位置无切割长度，套数表示使用该切割方案的次数"
    },
    "English": {
        "title": "📘 Roll Cutting Optimization Problem Background",
        "problem_header": "📋 Problem Description",
        "problem_text": """
In the paper roll manufacturing industry, standardized-length rolls must be cut into various lengths to meet different product or customer needs. Each cutting method yields different segment lengths and quantities, and results in varying leftover waste.

- **Decision**: How to cut rolls based on daily demand
- **Objective**: Minimize leftover waste while meeting daily demand
""",
        "diagram_header": "📏 Roll Cutting Diagram",
        "comparison_header": "📊 Cutting Plan Comparison",
        "assumption_header": "📌 Assumptions",
        "assumption_text": """
To simplify and clearly describe the model, we make the following assumptions:
- Daily demand is known in advance
- Raw roll length is fixed (e.g., 5450mm)
- Daily capacity is sufficient to meet all demand
- Cut segments must exactly match demand
- Waste and surplus are calculated based on preset rules

#### Terminology

- Waste: Unusable leftover after cutting, defined with bounds (e.g., 0–50mm)
- Surplus: Usable leftover that can fulfill future demand, with a lower bound (e.g., 1000mm)
- Replenishment: Surplus rolls are used to fulfill future demand, prioritizing highest demand first, then next highest, until surplus is exhausted
""",
        "constraint_header": "### Constraints",
        "tech_constraints": "#### Technical Constraints",
        "tech_constraints_text": """
    - Maximum number of cuts: 4 cuts (up to 5 segments)
    - Edge loss range: 0-50mm
    - Minimum surplus: 1000mm
    """,
        "biz_constraints": "#### Business Rules",
        "biz_constraints_text": """
    - Replenishment mechanism: Excess rolls prioritize high-demand orders
    - Order priority: Sorted by order urgency
    - Special marking: Non-daily replenishment rolls need to be marked
    """,
        "output_note": "Daily results are presented in the following table format (note: surplus rolls used for future demand must be specially marked)",
        "output_example": "📁 Sample Output Format",
        "output_caption": "Note: '-' means no cut length in that position; 'Sets' indicates how many times the cutting plan is used"
    }
}

# 中英字典
ALGO_DOC_LANG = {
    "中文": {
        "page_title": "⚙️ 执行卷纸切割算法",
        "description": """
请在“执行算法”页面将示例输入文件改成你需要的数据。
""",
        "io_header": "📂 输入输出文件说明",
        "global_param_expander": "📥 输入文件说明：global_param.csv",
        "global_param_table": """
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
""",
        "demand_expander": "📥 输入文件说明：demand.csv",
        "demand_table": """
| 字段名     | 描述               | 类型   | 是否必填 | 备注             |
|------------|--------------------|--------|-----------|------------------|
| 幅宽       | 客户所需纸卷宽度   | double | ✅        | 单位 mm          |
| 订单件数   | 每种幅宽的需求数量 | double | ✅        | 每天若干行       |
| 移库日期   | 该需求所属日期     | string | ✅        | 支持多天数据     |
""",
        "solution_out_expander": "📤 输出文件说明：solutionOut.csv（切割方案明细）",
        "solution_out_table": """
| 字段名             | 描述                           | 类型   |
|--------------------|----------------------------------|--------|
| 日期               | 哪天用的该方案                  | string |
| 切割方案_第1~N段   | 每段的宽度，最多 N+1 段         | double |
| 套数               | 使用该方案多少卷                | int    |
| 原始幅宽           | 原纸宽度，应与输入一致          | double |
| 边损               | 剩余长度 <= 边损下限时记为边损  | double |
| 余量               | 剩余长度 >= 余量下限时记为余量  | double |
| 切割方案编码       | 用于后续匹配、追踪              | int    |
""",
        "kpi_out_expander": "📊 输出文件说明：kpiOut.csv（关键指标）",
        "kpi_out_table": """
| 字段名           | 描述                     | 类型   |
|------------------|--------------------------|--------|
| 日期             | 哪天的结果               | string |
| 原始纸卷使用个数 | 共用了多少根母卷         | int    |
| 切割方案数量     | 该日使用了多少种方案     | int    |
| 运行时间（秒）   | 算法运行耗时             | double |
""",
        "other_outputs_expander": "📦 输出文件说明：supplyOut.csv / demandOut.csv / fulfillmentOut.csv",
        "other_outputs_text": """
- `supplyOut.csv`：每种方案每种宽度的供给数量
- `demandOut.csv`：每天每种宽度的实际需求与未满足数
- `fulfillmentOut.csv`：哪个方案在什么日期供给了哪个需求

这些用于分析方案对需求的满足匹配情况，可用于生成追踪表、KPI 和图示。
""",
        "example_data_header": "📄 示例输入数据（可编辑）",
        "edit_global_params": "📝 编辑全局参数",
        "download_global_params": "📥 下载编辑后的 global_params.csv",
        "edit_demand_data": "📝 编辑需求数据",
        "download_demand_data": "📥 下载编辑后的 demand.csv",
        "run_algorithm": "🚀 运行算法",
        "running_algorithm": "算法运行中，请稍候...",
        "algorithm_success": "✅ 算法运行完成！",
        "algorithm_error": "❌ 算法运行出错：{}",
        "output_results": "📊 输出结果",
        "kpi_metrics": "🎯 关键指标",
        "cutting_solutions": "切割方案 (solutionOut.csv)",
        "supply_results": "供给结果 (supplyOut.csv)",
        "demand_fulfillment": "需求满足情况 (demandOut.csv)",
        "matching_results": "供需匹配 (fulfillmentOut.csv)",
        "empty_solution": "切割方案为空，请检查输出文件。",
        "cutting_diagrams": "📏 切割方案图示"
    },
    "English": {
        "page_title": "⚙️ Execute Paper Roll Cutting Algorithm",
        "description": """
Please modify the example input files on the "Execute Algorithm" page to your required data.
""",
        "io_header": "📂 Input and Output File Descriptions",
        "global_param_expander": "📥 Input File Description: global_param.csv",
        "global_param_table": """
| Parameter Name   | Description                        | Type   | Default Value | Notes                      |
|------------------|-------------------------------------|--------|---------------|---------------------------|
| Raw Roll Length  | Width of raw paper                 | double | None          | For example, 5450         |
| Max Cuts         | Maximum number of cuts per roll    | int    | None          | E.g., 4 means up to 5 segments |
| Enable Replenishment | Allow excess parts for replenishment | string | Yes/No      | No means excess is wasted |
| Consider Edge Loss | Set edge loss limits               | string | Yes/No      | Yes means need to fill edge loss limits |
| Edge Loss Lower Bound | Less than this value is considered waste | double | 0       | Smaller values can be considered waste |
| Edge Loss Upper Bound | Greater than this value is considered surplus | double | None    | Need to consider surplus lower bound |
| Surplus Lower Bound | Remaining length not considered waste | double | None    | Threshold for replenishment judgment |
| Minimum Usage of Cutting Plan | Minimum usage times of a cutting plan | int    | 0       | Prevent extreme solutions |
""",
        "demand_expander": "📥 Input File Description: demand.csv",
        "demand_table": """
| Field Name       | Description                   | Type   | Required | Notes              |
|------------------|--------------------------------|--------|----------|-------------------|
| Width            | Customer-required paper width | double | ✅       | Unit: mm          |
| Order Quantity   | Number of requirements per width | double | ✅       | Several lines per day |
| Storage Date     | The date of this requirement  | string | ✅       | Supports multiple days of data |
""",
        "solution_out_expander": "📤 Output File Description: solutionOut.csv (Cutting Plan Details)",
        "solution_out_table": """
| Field Name           | Description                          | Type   |
|----------------------|---------------------------------------|--------|
| Date                 | Which day used this plan              | string |
| Cutting Plan_Segment 1-N | Width of each segment, max N+1 segments | double |
| Sets                 | How many rolls use this plan          | int    |
| Original Width       | Original paper width, should match input | double |
| Edge Loss            | Remaining length <= edge loss threshold is considered edge loss | double |
| Surplus              | Remaining length >= surplus threshold is considered surplus | double |
| Cutting Plan Code    | Used for subsequent matching and tracking | int    |
""",
        "kpi_out_expander": "📊 Output File Description: kpiOut.csv (Key Performance Indicators)",
        "kpi_out_table": """
| Field Name           | Description                     | Type   |
|----------------------|----------------------------------|--------|
| Date                 | Result of which day               | string |
| Raw Rolls Used       | Total number of mother rolls used | int    |
| Cutting Plans Used   | Number of plans used that day     | int    |
| Run Time (seconds)   | Algorithm runtime                | double |
""",
        "other_outputs_expander": "📦 Output File Description: supplyOut.csv / demandOut.csv / fulfillmentOut.csv",
        "other_outputs_text": """
- `supplyOut.csv`: Supply quantity of each plan for each width
- `demandOut.csv`: Actual demand and unmet numbers per day for each width
- `fulfillmentOut.csv`: Which plan supplied which demand on which date

These are used to analyze how well the plans meet the demands,可用于 generating traceability tables, KPIs, and charts.
""",
        "example_data_header": "📄 Example Input Data (Editable)",
        "edit_global_params": "📝 Edit Global Parameters",
        "download_global_params": "📥 Download Edited global_params.csv",
        "edit_demand_data": "📝 Edit Demand Data",
        "download_demand_data": "📥 Download Edited demand.csv",
        "run_algorithm": "🚀 Run Algorithm",
        "running_algorithm": "Algorithm running, please wait...",
        "algorithm_success": "✅ Algorithm run successfully!",
        "algorithm_error": "❌ Algorithm error: {}",
        "output_results": "📊 Output Results",
        "kpi_metrics": "🎯 Key Performance Metrics",
        "cutting_solutions": "Cutting Solutions (solutionOut.csv)",
        "supply_results": "Supply Results (supplyOut.csv)",
        "demand_fulfillment": "Demand Fulfillment (demandOut.csv)",
        "matching_results": "Supply-Demand Matching (fulfillmentOut.csv)",
        "empty_solution": "Cutting solutions are empty, please check the output files.",
        "cutting_diagrams": "📏 Cutting Solution Diagrams"
    }
}