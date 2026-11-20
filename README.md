---
title: Column Generation App
emoji: 🧩
colorFrom: indigo
colorTo: blue
sdk: docker
sdk_version: "1.33.0"
app_file: app.py
pinned: false
---


# 📦 切割优化与列生成算法（Column Generation for Multi-Day Cutting Plan）

## Column Studio 现代化工作台

新增独立响应式前端与 FastAPI，source/ 核心列生成、余料补库与 GLPK 模型保持原样。旧 Streamlit 可按原依赖运行，但不作为生产主要界面。

### 本地运行（Python 3.11 / 3.12）

安装 GLPK，确保 glpsol 在 PATH 中，然后创建虚拟环境并安装独立 Web 依赖：

```sh
python -m venv .venv
# Windows 使用 .venv/Scripts/python；Linux 使用 .venv/bin/python
.venv/Scripts/python -m pip install -r requirements-web.txt
.venv/Scripts/python -m uvicorn api.main:app --host 127.0.0.1 --port 8091
```

访问 http://127.0.0.1:8091/，自动进入 /studio/，API 文档 /docs。生产隔离部署见 deploy/README.md。新运行时不需要 Streamlit、Matplotlib 或商业求解器。

### 接口和数据

- GET /api/health：服务与 GLPK 可用状态。
- GET /api/example：原始 CSV 示例，返回 demand 和 parameters 数组。
- POST /api/jobs：提交上述结构，HTTP 202 返回 id。demand 每行包含 幅宽、订单件数、移库日期；parameters 每行包含 参数名、参数值。最少提供 原始卷纸长度 和 最大切割次数，可选原项目全部参数，包括 切割方案使用下限。
- GET /api/jobs/{id}：queued / running / succeeded / failed 状态、逐日期进度或最终 result。
- result 包含 success、runtime、summary、results。results 完整保留 kpiOut.csv、solutionOut.csv、supplyOut.csv、demandOut.csv、fulfillmentOut.csv 五张原生结果表，DataFrame/NumPy 通过 pandas JSON 编码，NaT/NaN 均为 null。
- CSV 可编辑、上传和预览，结果支持各表 CSV 和完整 JSON 导出。输入变化后需重新运行。
- 利用率为所有产出幅宽 / 总投入幅宽，包含超产；负边损可能使其超过 100%。初始模式与最终整数解保留原项目逻辑，不提供额外全局约束保证或最优性证明。

ALLOWED_ORIGINS 可用逗号分隔设置明确跨域来源，默认仅允许本地 8091；同源部署不需要手动配置 API 地址。生产 APP_BASE_PATH=/column-generation；Caddy 剥离此路径后转发。仅启动单 worker，内存任务队列不跨进程共享。每个任务在独立进程和临时目录执行，不覆盖算法输出文件。

---

## 🧩 项目背景

在制造、包装、物流等行业中，常面临将大块材料（如钢卷、纸卷）裁剪为不同规格以满足每日订单需求的问题。如何优化切割模式，使原材料利用率最大化，并减少浪费与加工时间，是生产调度中的重要课题。

本项目针对该类**多天、多规格订单切割优化问题**，设计了一个基于列生成（Column Generation）的求解框架，并引入 Pyomo + Gurobi 实现多目标建模与迭代式模式生成。

---

## 📋 问题描述

- 每天有一组切割需求（不同宽度与数量）；
- 每个原料的宽度固定，切割数量有限（最多切 K 刀）；
- 残料超过最小剩余值可入库，否则当作废料；
- 每种切割模式决定一组规格的组合；
- 目标是：**在满足每日需求的前提下，最小化使用原料数量**，同时控制废料量。

---



## 🧠 模型结构

项目采用**列生成（Column Generation）框架**，分三层：

### 🔹 原始问题（Original Problem）

- 输入最终模式集；
- 建立 MILP 问题，决定每个模式的使用次数；
- 满足所有规格需求、最小化使用原材料总数。

### 🔹 主问题（Master Problem）

- 给定一组当前可用模式；
- 建立 LP 问题，变量为每种模式使用数量；
- 得到对偶值（每种规格的“影子价格”）；

### 🔹 子问题（Sub Problem）

- 利用对偶值，求解能否生成新的有“负 reduced cost”的模式；
- 其本质是一个背包问题或整数优化问题；
- 包括是否残料入库的逻辑建模。

---

## 🔁 求解流程（Context 类）

1. 对每个日期读取需求；
2. 初始化切割模式；
3. 重复执行：
   - 求解主问题 → 得到对偶值；
   - 构造子问题 → 生成新模式；
   - 若找到新模式则更新模式集；
   - 直至子问题无改进；
4. 最后求解原始问题，输出结果；
5. 可顺序或并行处理多天任务。

---


## 📌 应用场景

- 钢材、纸板、织物等大规格材料切割排程；
- 包装/物流行业按需裁剪策略优化；
- 库存管理中“残料-废料”二元分类问题；
- 箱型优化、模板切割、板材利用等相关问题。

---
**Environment Deployment**

 Install Python Executor (version >= 3.7.0), Anaconda IDE is recommended


The required packages are listed in requirements.txt. you can install them using:

    pip install -r requirements.txt
 
 **Run**

To run project:

    1. put your input data in data folder, you can adjust parameters.
    2. execute python main.py, and result.csv will be generated in data folder.
