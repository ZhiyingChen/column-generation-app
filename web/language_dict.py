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
