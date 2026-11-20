"use strict";

const byId = (identifier) => document.getElementById(identifier);
const apiBase = new URL("../api/", window.location.href);
const state = { parameters: [], result: null, activeTable: "solutionOut.csv", running: false, timer: null };
const tables = { "solutionOut.csv": "切割方案", "kpiOut.csv": "每日 KPI", "demandOut.csv": "需求履约", "supplyOut.csv": "供给明细", "fulfillmentOut.csv": "履约关系" };
const colors = ["#527b5d", "#8baa72", "#b0c78b", "#688f88", "#b2a879", "#7e9e60"];
const escapeHtml = (value) => String(value ?? "—").replace(/[&<>"']/g, (character) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[character]);
const format = (value) => Number(value).toLocaleString("zh-CN", { maximumFractionDigits: 2 });

function notify(message, type = "") {
  byId("notice").textContent = message;
  byId("notice").className = "notice " + type;
}

async function request(path, options = {}) {
  const response = await fetch(new URL(path, apiBase), { ...options, signal: AbortSignal.timeout(20000) });
  const payload = await response.json();
  if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "输入格式不正确，请检查需求数据与参数。");
  return payload;
}

function parseCsv(text) {
  const records = [];
  let record = [];
  let field = "";
  let quoted = false;
  const content = text.replace(/^﻿/, "").replace(/\r\n/g, "\n");
  for (let index = 0; index < content.length; index += 1) {
    const character = content[index];
    if (character === '"') {
      if (quoted && content[index + 1] === '"') { field += '"'; index += 1; }
      else { quoted = !quoted; }
    } else if (character === "," && !quoted) { record.push(field.trim()); field = ""; }
    else if (character === "\n" && !quoted) {
      record.push(field.trim());
      if (record.some(Boolean)) records.push(record);
      record = []; field = "";
    } else { field += character; }
  }
  if (quoted) throw new Error("CSV 引号未闭合。");
  record.push(field.trim());
  if (record.some(Boolean)) records.push(record);
  const headers = records.shift() || [];
  for (const header of ["幅宽", "订单件数", "移库日期"]) {
    if (!headers.includes(header)) throw new Error("CSV 缺少列：" + header);
  }
  if (new Set(headers).size !== headers.length) throw new Error("CSV 表头不能重复。");
  if (!records.length) throw new Error("请至少输入一条订单需求。");
  return records.map((values, index) => {
    if (values.length !== headers.length) throw new Error("第 " + (index + 2) + " 行列数不正确。");
    return Object.fromEntries(headers.map((header, position) => [header, values[position]]));
  });
}

function csvText(rows) {
  const columns = Object.keys(rows[0] || {});
  const cell = (value) => {
    const text = String(value ?? "");
    const safe = /^[=+@\t\r]/.test(text) || (/^-/.test(text) && !Number.isFinite(Number(text))) ? "'" + text : text;
    return '"' + safe.replace(/"/g, '""') + '"';
  };
  return [columns.map(cell).join(","), ...rows.map((row) => columns.map((column) => cell(row[column])).join(","))].join("\n");
}

function tableMarkup(rows) {
  const columns = Object.keys(rows[0] || {});
  if (!rows.length) return '<p class="model-note">此结果表暂无记录。</p>';
  return '<table><thead><tr>' + columns.map((column) => '<th scope="col">' + escapeHtml(column) + '</th>').join("") + '</tr></thead><tbody>' + rows.map((row) => '<tr>' + columns.map((column) => '<td>' + escapeHtml(row[column]) + '</td>').join("") + '</tr>').join("") + '</tbody></table>';
}

function preview() {
  const rows = parseCsv(byId("demandEditor").value);
  const days = new Set(rows.map((row) => row["移库日期"])).size;
  byId("inputCount").textContent = format(rows.length);
  byId("dayCount").textContent = format(days);
  byId("editorStats").textContent = rows.length + " 条记录 · " + days + " 个日期 · 预览前 8 行";
  byId("inputPreview").innerHTML = tableMarkup(rows.slice(0, 8));
  return rows;
}

function renderParameters() {
  byId("parameterFields").innerHTML = state.parameters.map((row, index) => {
    const name = row["参数名"];
    const value = row["参数值"];
    const boolean = name.startsWith("是否");
    const input = boolean
      ? '<select id="param-' + index + '" data-parameter="' + index + '"><option' + (value === "否" ? " selected" : "") + '>否</option><option' + (value === "是" ? " selected" : "") + '>是</option></select>'
      : '<input id="param-' + index + '" data-parameter="' + index + '" type="number" step="' + (name.includes("次数") || name.includes("使用下限") ? "1" : "any") + '" value="' + escapeHtml(value) + '">';
    return '<div class="field"><label for="param-' + index + '">' + escapeHtml(name) + '</label>' + input + '</div>';
  }).join("");
}

async function loadExample() {
  try {
    byId("loadExample").disabled = true;
    const example = await request("example");
    state.parameters = example.parameters;
    if (!state.parameters.some((row) => row["参数名"] === "切割方案使用下限")) state.parameters.push({ "参数名": "切割方案使用下限", "参数值": "0" });
    byId("demandEditor").value = csvText(example.demand);
    renderParameters(); preview();
    notify("项目原始示例已加载。可直接运行，或编辑需求和模型参数。旧结果不会自动更新。");
  } catch (error) { notify("示例加载失败：" + error.message, "error"); }
  finally { byId("loadExample").disabled = state.running; }
}

function renderResults(result) {
  state.result = result;
  const summary = result.summary;
  byId("kpiRolls").textContent = format(summary.rolls);
  byId("kpiPatterns").textContent = format(summary.patterns);
  byId("kpiUtilization").textContent = format(summary.utilization) + "%";
  byId("kpiFulfillment").textContent = format(summary.fulfillment) + "%";
  byId("emptyResults").hidden = true;
  byId("resultContent").hidden = false;
  byId("exportJson").disabled = false;
  const kpis = result.results["kpiOut.csv"];
  const maximum = Math.max(...kpis.map((row) => row["原始纸卷使用个数"]), 1);
  byId("dailyChart").innerHTML = kpis.map((row) => '<div class="chart-column"><strong class="chart-value">' + format(row["原始纸卷使用个数"]) + '</strong><div class="bar" style="height:' + Math.max(4, row["原始纸卷使用个数"] / maximum * 120) + 'px"></div><span class="chart-label">' + escapeHtml(row["日期"]) + '</span><span class="chart-sub">' + format(row["切割方案数量"]) + ' 种模式</span></div>').join("");
  const facts = [["求解引擎", "Pyomo / GLPK"], ["算法耗时", format(result.runtime) + " 秒"], ["计划日期", summary.days + " 天"], ["未满足数量", format(summary.unfulfilled) + " 件"]];
  byId("resultFacts").innerHTML = facts.map(([label, value]) => '<div class="fact"><span>' + label + '</span><strong>' + escapeHtml(value) + '</strong></div>').join("");
  byId("patternDate").innerHTML = kpis.map((row) => '<option value="' + escapeHtml(row["日期"]) + '">' + escapeHtml(row["日期"]) + '</option>').join("");
  renderPatterns();
  byId("resultTabs").innerHTML = Object.entries(tables).map(([file, name]) => '<button role="tab" data-table="' + file + '">' + name + '</button>').join("");
  renderTable();
}

function renderPatterns() {
  const rows = state.result.results["solutionOut.csv"].filter((row) => row["日期"] === byId("patternDate").value);
  byId("patternBars").innerHTML = rows.map((row) => {
    const widths = Object.entries(row).filter(([key, value]) => key.startsWith("切割方案_第") && value !== null).map(([, value]) => Number(value));
    const original = Number(row["原始幅宽"]);
    const remaining = Math.max(0, original - widths.reduce((total, width) => total + width, 0));
    const segments = widths.map((width, index) => '<div class="segment" style="flex:' + width + ';background:' + colors[index % colors.length] + '" title="' + width + ' mm">' + format(width) + '</div>').join("");
    return '<div class="pattern-row"><span>P' + String(row["切割方案编码"]).padStart(2, "0") + '</span><div class="segments">' + segments + (remaining ? '<div class="segment remnant" style="flex:' + remaining + '" title="余量 ' + remaining + ' mm"></div>' : "") + '</div><strong>× ' + format(row["套数"]) + '</strong></div>';
  }).join("");
}

function renderTable() {
  const rows = state.result.results[state.activeTable];
  byId("resultTable").innerHTML = tableMarkup(rows);
  byId("resultRowCount").textContent = tables[state.activeTable] + " · " + rows.length + " 行 · 原始字段完整保留";
  byId("resultTabs").querySelectorAll("button").forEach((button) => {
    const active = button.dataset.table === state.activeTable;
    button.classList.toggle("active", active);
    button.setAttribute("aria-selected", String(active));
  });
}

function setBusy(busy) {
  state.running = busy;
  byId("runButton").disabled = busy;
  byId("runButton").textContent = busy ? "正在求解，请稍候…" : "▶ 运行列生成算法 ↗";
  byId("loadExample").disabled = busy;
  byId("demandEditor").disabled = busy;
  byId("csvUpload").disabled = busy;
  byId("parameterFields").querySelectorAll("input,select").forEach((field) => { field.disabled = busy; });
  byId("runBadge").classList.toggle("busy", busy);
}

async function runAlgorithm() {
  if (state.running) return;
  try {
    const demand = preview();
    const parameters = state.parameters.map((row, index) => ({ "参数名": row["参数名"], "参数值": byId("param-" + index).value }));
    setBusy(true);
    byId("runBadge").textContent = "提交中";
    byId("runTitle").textContent = "正在构建切割计划";
    byId("progressBar").style.width = "3%";
    const started = Date.now();
    state.timer = setInterval(() => { byId("elapsed").textContent = ((Date.now() - started) / 1000).toFixed(1) + "s"; }, 100);
    const job = await request("jobs", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ demand, parameters }) });
    notify("任务 " + job.id.slice(0, 8) + " 已提交。算法在独立进程运行，请保持页面开启。");
    let completed = false;
    let retries = 0;
    while (!completed) {
      await new Promise((resolve) => setTimeout(resolve, 1000));
      let current;
      try { current = await request("jobs/" + job.id); retries = 0; }
      catch (error) {
        if (retries >= 4) throw new Error("状态连接中断，可稍后查询任务 " + job.id + "；" + error.message);
        retries += 1; notify("连接暂时中断，正在重试（" + retries + "/4）…", "warning"); continue;
      }
      byId("runBadge").textContent = current.status === "queued" ? "排队中" : "求解中";
      if (current.progress) {
        byId("runDescription").textContent = "正在处理 " + current.progress.date + " · 已完成 " + current.progress.completed + "/" + current.progress.total + " 天";
        byId("progressBar").style.width = (10 + 80 * current.progress.completed / current.progress.total) + "%";
      }
      if (current.status === "failed") throw new Error(current.error);
      if (current.status === "succeeded") {
        completed = true;
        renderResults(current.result);
        byId("progressBar").style.width = "100%";
        byId("runBadge").textContent = "求解完成";
        byId("runTitle").textContent = "切割计划已就绪";
        byId("runDescription").textContent = "算法耗时 " + current.result.runtime + " 秒 · 五类结果已生成";
        notify("优化完成：" + format(current.result.summary.rolls) + " 卷原料，" + format(current.result.summary.patterns) + " 种模式，需求满足率 " + current.result.summary.fulfillment + "%。" + (current.result.summary.unfulfilled ? "存在未满足需求，请检查结果。" : "结果可在下方查看和导出。"), current.result.summary.unfulfilled ? "warning" : "");
      }
    }
  } catch (error) {
    byId("runBadge").textContent = "未完成";
    byId("runTitle").textContent = "请检查输入后重试";
    byId("runDescription").textContent = "已有结果保留，未被本次失败运行覆盖。";
    notify(error.message, "error");
  } finally { clearInterval(state.timer); setBusy(false); }
}

function download(filename, content, type) {
  const url = URL.createObjectURL(new Blob([content], { type }));
  const link = document.createElement("a");
  link.href = url; link.download = filename; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}

byId("docsLink").href = new URL("../docs", window.location.href).href;
byId("loadExample").addEventListener("click", loadExample);
byId("runButton").addEventListener("click", runAlgorithm);
byId("previewButton").addEventListener("click", () => { try { preview(); notify("预览已刷新。请运行算法以更新结果。"); } catch (error) { notify(error.message, "error"); } });
byId("demandEditor").addEventListener("input", () => notify("需求数据已修改。刷新预览并重新运行算法后，结果才会更新。", "warning"));
byId("parameterFields").addEventListener("change", () => notify("模型参数已修改。请重新运行算法更新结果。", "warning"));
byId("csvUpload").addEventListener("change", async (event) => {
  const file = event.target.files[0];
  if (!file) return;
  try {
    if (file.size > 2 * 1024 * 1024) throw new Error("CSV 文件不能超过 2 MB。");
    const text = await file.text(); parseCsv(text);
    byId("demandEditor").value = text; preview(); notify("CSV 已导入，请检查参数后运行算法。");
  } catch (error) { notify(error.message, "error"); }
  event.target.value = "";
});
byId("patternDate").addEventListener("change", renderPatterns);
byId("resultTabs").addEventListener("click", (event) => {
  const button = event.target.closest("[data-table]");
  if (button) { state.activeTable = button.dataset.table; renderTable(); }
});
byId("exportCsv").addEventListener("click", () => { if (state.result) download(state.activeTable, "﻿" + csvText(state.result.results[state.activeTable]), "text/csv;charset=utf-8"); });
byId("exportJson").addEventListener("click", () => { if (state.result) download("column-generation-results.json", JSON.stringify(state.result, null, 2), "application/json"); });
document.querySelectorAll(".nav-link").forEach((link) => link.addEventListener("click", () => {
  document.querySelectorAll(".nav-link").forEach((item) => item.classList.toggle("active", item === link));
}));
request("health").then((health) => {
  byId("healthDot").classList.toggle("online", health.solver_available);
  byId("healthLabel").textContent = health.solver_available ? "求解器在线" : "GLPK 尚未安装";
}).catch(() => { byId("healthLabel").textContent = "API 连接失败"; });
loadExample();
