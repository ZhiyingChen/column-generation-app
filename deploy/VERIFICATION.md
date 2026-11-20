# 部署验证记录 · 2026-11-20

- 公网入口：http://43.163.3.74/column-generation/（跳转到 studio/）。
- API 文档：http://43.163.3.74/column-generation/docs，OpenAPI servers 为 /column-generation。
- 部署：/opt/column_generation_app，独立 .venv，无登录用户 column-generation。
- 服务：column-generation-app.service，127.0.0.1:8091，已启用开机启动和失败自动重启。
- Caddy 备份：/etc/caddy/Caddyfile.bak.column-generation-20261120-202458。
- Caddy 候选配置与最终配置均通过 validate，之后仅热加载，未重启。

## 验证结果

- node --check frontend/app.js 与 Python compileall api source 通过。
- 浏览器桌面 1440px、移动端 390px 检查通过，无 JavaScript 错误，移动页面 scrollWidth 与 viewport 均为 390。
- 加载原始 149 条示例，真实点击运行按钮完成算法，并展示 KPI、图表、切割条带和结果表；五张表切换以及 CSV/JSON 下载通过。
- 异常幅宽输入被 API 拒绝，返回 422。
- 公网 API 提交返回 HTTP 202，任务最终 succeeded，success=true。
- 线上 2 天结果：197 卷，46 种模式，利用率 89.88%，需求满足率 100%，未满足 0；记录的一次算法耗时 2.551 秒。
- 2024-02-13：38 卷、21 模式；2024-02-14：159 卷、25 模式。
- 返回行数：KPI 2，切割方案 46，供给 114，需求 52，履约关系 112。
- Windows GLPK 本地结果同为 197 卷、46 模式、需求满足率 100%，利用率 90.04%；不同平台的等价切割组合存在差异，不要求逐行相同。

## 原有应用

部署前后 warehouse-app PID 3968958、consult-demo PID 1379920、consult-demo-dev PID 1379897 均未改变；三个服务仍 active。Caddy PID 1794102 未改变。IP 根路径、既有 /warehouse/、咨询生产与开发接口根路径、https://wisdawn-consult.cn/ 均 HTTP 200。既有端口和反向代理保留。

未在代码、Git、配置或脚本中保存密码或私钥；连接使用本机已有 SSH 私钥，无新增临时凭据文件。
