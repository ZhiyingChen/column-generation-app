# 独立部署

专属目录 /opt/column_generation_app，虚拟环境 .venv，系统用户 column-generation，systemd 服务 column-generation-app.service，仅监听 127.0.0.1:8091。禁止复用其他项目环境或服务。

1. 只读检查 /opt、监听端口、相关服务和 /etc/caddy/Caddyfile，确认目标目录和 8091 空闲。
2. 将审核后的源码放入全新目录，执行 python3 -m venv .venv 和 .venv/bin/pip install -r requirements-web.txt。确保系统 GLPK 的 glpsol 在 PATH 中，不升级无关软件。
3. 创建无登录系统用户 column-generation，代码由 root 持有，该用户只读。任务仅写隔离临时目录。
4. 安装本目录 service 文件到 /etc/systemd/system/，执行 systemctl daemon-reload 和 systemctl enable --now column-generation-app.service。不重启其他服务。
5. 检查内部 /api/health，再配置公网入口。

## Caddy

修改前备份 /etc/caddy/Caddyfile 为 Caddyfile.bak.column-generation-<timestamp>。仅将 caddy-route.txt 插入已有 http://43.163.3.74 块内，位于原 reverse_proxy 前；原根路径代理与域名块不变。

先运行 caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile，通过后才 systemctl reload caddy。失败则恢复本次备份并验证。入口 /column-generation/ 跳转到 /column-generation/studio/。前端资源相对寻址，API 为 ../api/。APP_BASE_PATH=/column-generation 与 Uvicorn --root-path /column-generation 必须同时设置，保证静态挂载、路由及文档前缀正确。

部署前后比对已有服务 PID 与 active 时间，并检查根路径及原域名代理。回滚仅停止本服务并撤回新增路由，验证后热加载，不改其他应用目录。

## 运维边界

- journalctl -u column-generation-app 查看日志。
- 单 Uvicorn worker、单求解进程、最多三个未完成任务、最近 20 个任务保留内存，重启即清空。
- 输入最多 2000 条、14 天、100 规格，单任务最长 300 秒；最终每日 MILP 沿用原算法 30 秒限制，不承诺全局最优。
- 公网演示无账户认证，不上传敏感业务数据；正式多用户生产需额外配置 TLS、认证、请求限流与任务持久化。
- 凭据不得保存至源码、文档、服务配置或运维脚本。
