# QuantDinger Changelog

This document records version updates, new features, bug fixes, and database migration instructions.

---

## V3.0.2 (2026-04-11) — 多语言文件全量补齐(AI 自动翻译)

### 🌍 i18n

此前除 `zh-CN` / `en-US` 外,其余 7 个语言文件只有约 2000/4240 条(约 48% 覆盖),大量界面字段会回退到英文或 key 名。这次用 DeepSeek 把全部缺失 key 一次性批量翻译、写回源文件:

| 语言 | 修复前 | 修复后 | 新增条目 |
|---|---|---|---|
| `ar-SA` Arabic  | 2029 | **4573** | 2541 |
| `de-DE` German  | 2077 | **4573** | 2491 (+patch) |
| `en-US` English | 4424 | **4498** | 72 |
| `fr-FR` French  | 2029 | **4573** | 2539 (+patch) |
| `ja-JP` Japanese| 2033 | **4573** | 2537 (+patch) |
| `ko-KR` Korean  | 2034 | **4573** | 2537 (+patch) |
| `th-TH` Thai    | 2029 | **4573** | 2541 (+patch) |
| `vi-VN` Vietnamese | 1759 | **4495** | 2734 (+patch) |
| `zh-TW` Traditional | 3741 | **4499** | 758 |

全部 9 个语言文件相对 `zh-CN` 基准 **missing = 0** ✅

### 🛠️ Tooling (新增)

- **`scripts/i18n-diff.js`** — 扫描所有 locale 文件,以 `zh-CN` 为基准报告 missing / extra keys;支持 `--detail`、`--lang=xx-YY` 查看具体缺失。
- **`scripts/i18n-fill-ai.js`** — 增量 AI 翻译工具。支持 DeepSeek / Anthropic / OpenAI / OpenRouter 四家 provider,批量(默认 80/batch)+ 并发(默认 6)+ 本地缓存(`scripts/.i18n-cache/`)+ 自动备份(`*.js.bak`),字符串值按安全追加方式写回文件。失败批次 3 次重试 + 部分保留策略。保护占位符 `{foo}`、`<code>…</code>`、换行符 `\n`、HTML 标签、`BTC/ETH/USDT/AI/MT5` 等专有名词。
- **`scripts/i18n-patch-specials.js`** — 一次性补齐 AI 脚本无法覆盖的特殊 key:空字符串值、嵌套对象值(`trading-assistant.brokerNames`)、中文量词单字(`dashboard.unit.trades` / `.strategies` 等在西语/泰/越留空)。
- **`scripts/README.md`** — 工具链说明,含典型用法、API Key 配置、成本估算、质量提示。
- **`.gitignore`** — 忽略 `scripts/.i18n-cache/` 与 `QuantDinger-Vue-src/src/locales/lang/*.bak`。

### 翻译质量

专用术语已落地行业译法:网格(`neutral/long/short`)、Maker/Taker 指值/市价、加仓/平仓、止盈/止损、浮动盈亏、权益、仓位、挂单、成交等。占位符 / `<code>` 标签 / 代码示例全部保留。单次批量失败率 < 0.2%,失败 key 已由 specials 脚本兜底。

### ⚠️ 已知事项(后续改进)

- **`ja-JP` / `zh-TW` 等部分"已存在但值是英文"的 key 未被重译**:脚本只填「完全缺失」的 key,不覆写已有值。若要纠正这部分"占位英文",需要单独一次「识别非目标语言内容并重译」的增强扫描。

### 🗄️ Database Migration

无。

### 📦 Files Changed

- `QuantDinger-Vue-src/src/locales/lang/{ar-SA,de-DE,en-US,fr-FR,ja-JP,ko-KR,th-TH,vi-VN,zh-TW}.js`
- `scripts/i18n-diff.js`、`scripts/i18n-fill-ai.js`、`scripts/i18n-patch-specials.js`、`scripts/README.md`
- `.gitignore`

---

## V3.0.2 (2026-04-11) — 交易机器人全链路修复(Grid / Martingale / Trend / DCA)

### 🐛 Bug Fixes — 交易机器人

针对四类机器人(网格 / 马丁 / 趋势 / 定投)做了从前端配置、脚本模板、后端执行到列表/详情页数据的端到端审计与修复:

- **[P0-1] 编辑机器人会清空运行时状态**:`StrategyService.update_strategy` 此前直接用 payload 里的 `trading_config` 整体替换老记录,导致 `script_runtime_state`(马丁 `layer`/`total_cost`、网格 `bp/sp/prev_price`、DCA `total_qty` 等)被一把抹掉,改完参数重启就像换了台新机器人。改为 `{**existing, **incoming}` 浅合并,并保护 `script_runtime_state`、`last_signal_time`、`last_execution_time`、`bot_runtime_stats` 等后端维护的运行时字段。
- **[P0-2] 网格空头不受预算控制**:旧 `total_spent` 只在买入时累加,卖出开空(中性/做空模式)既不检查也不累加,合约下可以把空头无限放大直至爆仓。重写网格脚本改为 `long_exposure` / `short_exposure` 双路独立核算,BUY 先抵扣空头再开多(做多侧过预算就跳过),SELL 同理。
- **[P0-3] 马丁/趋势默认 `maker` 限价挂单导致漏触发和重复下单**:马丁每层加仓依赖上一单「已成交」才会更新 `last_entry_price`,挂单未成交时脚本在下一根 K 线用同一价格重新发单,出现一次开仓就下两笔甚至多笔的现象。向导 `buildPayload` 对 `bot_type` 为 `martingale` / `trend` 强制 `order_mode='market'`,网格/DCA 保留用户选择(默认 maker 更省费)。
- **[P0-4] 网格/DCA 在同一 tick 多笔减仓的本地持仓跟踪错误**:`_script_orders_to_execution_signals` 把脚本传来的 USDT 名义金额直接丢给 `ctx.position.reduce_position/add_position/open_position`(这些方法内部以 qty 单位计数),导致同一 tick 内若先后发 sell + sell,第二笔会被误判为「开空」而不是「继续平多」,发出错误的 `open_short` 信号。修复:把 USDT 金额按 `usdt * leverage / ref_price` 换算成近似 qty 再更新本地 ctx.position(真实下单数量依旧由 `_execute_signal` 按杠杆/市场类型重算,完全不变)。
- **[P0-5] DCA 频率被 K 线周期吞掉**:`intervalBars = round(freqMin / tfMin)` 当 `freq<tf`(比如 4h 线上选 hourly)会取整到 0,再 `max(1,0)=1`,结果变成「每根 K 线都买」(等于 4 小时 1 次)。把 DCA 脚本改成 **基于真实时间戳** 的 `INTERVAL_SEC = freqMin * 60`,用 `now - last_buy_ts >= INTERVAL_SEC` 判断,彻底与 K 线周期解耦。

### 🔧 Improvements

- **[P1] 机器人列表/详情返回运行时指标**:`list_strategies` / `get_strategy` 通过一次 GROUP BY 批量查 `qd_strategy_trades.profit-commission` 和 `qd_strategy_positions.unrealized_pnl`,在响应里附带 `realized_pnl` / `unrealized_pnl` / `total_pnl` / `current_equity`,前端 KPI 和卡片不再需要自己拼。
- **[P1] 趋势机器人仓位按实时权益计算**:`_hydrate_script_ctx_from_positions` 在 hydrate 持仓的同时把 `ctx.balance` / `ctx.equity` 刷新为 `initial_capital + 已实现 + 未实现` 的最新值,趋势脚本里 `amt = ctx.balance * POS_PCT` 终于能跟着账户净值走,而不是始终停在初始资金。
- **[P1] DCA 仓位被外部平掉后自动重置**:DCA 脚本每根 bar 检查 `buy_count>0 且 total_qty>0 但 ctx.position 为空` 的情况,判定为手动/止损平仓并清零累计状态,下一轮定投正常重新开始。
- **[P1] 网格/DCA 前端参数校验**:`GridConfig` 新增上下限大小校验、等比网格下限>0 校验、以及「每格金额 × 网格数 ≤ 初始资金」校验;`DCAConfig` 新增「单次金额 ≤ 总预算」校验。多语言已补齐 10 种。

### 🗄️ Database Migration

本次无新增列/表,仅代码层修复。已有部署**不需要**执行任何 SQL。

### 📦 Files Changed

- `backend_api_python/app/services/strategy.py` — `update_strategy` 合并逻辑、`_compute_runtime_metrics`、列表/详情附带运行时指标
- `backend_api_python/app/services/trading_executor.py` — `_script_orders_to_execution_signals` USDT→qty 换算、`_hydrate_script_ctx_from_positions` 刷新 balance/equity
- `QuantDinger-Vue-src/src/views/trading-bot/components/BotCreateWizard.vue` — 马丁/趋势强制市价
- `QuantDinger-Vue-src/src/views/trading-bot/components/botScriptTemplates.js` — 网格双路预算、DCA 时间制间隔与外部平仓重置
- `QuantDinger-Vue-src/src/views/trading-bot/components/configs/GridConfig.vue`、`DCAConfig.vue` — 参数校验
- `QuantDinger-Vue-src/src/locales/lang/*.js` — 4 条新校验文案 × 10 语言

---

## V3.0.2 (2026-04-17) — 指标社区「同步代码」+ Martingale / 回测稳定性

### 🚀 New Features

- **指标社区 · 同步代码**：指标详情弹窗为已购用户在「立即使用」旁新增「同步代码」按钮。发布者更新并重新上架后，已购用户可一键把最新代码拉到自己的本地副本；前端带 `Tooltip`、确认弹窗与「有更新」橙色标记，暗色主题单独适配。
  - 新接口：`POST /api/community/indicators/<id>/sync`
  - 详情接口 `GET /api/community/indicators/<id>` 新增字段：`has_update`、`local_copy_id`
  - 本地副本与原始指标通过新增的 `qd_indicator_codes.source_indicator_id` 建立持久关联；老数据按名称兜底匹配并在首次同步时回填该字段。
- **交易机器人 · 参数标准化**：Martingale / Grid / Trend / DCA 四类机器人参数统一语义，创建确认页、列表页、详情页展示完全对齐，后端 `bot_display` 统一结构，前端映射大幅简化。
- **Martingale 重复开仓修复**：策略启动瞬间会立即下两笔单的问题修复（信号去重 + 当次循环内的市值/持仓校验）。

### 🐛 Bug Fixes

- **回测日期范围失效**：调整回测起止日期但结果不变的严重问题修复。根因为 `_fetch_kline_data` 在上游数据覆盖不全时会退化为 `df.tail(N)`，忽略 `start_date` 约束。改为严格按「请求区间 ∩ 可用区间」过滤；无交集时直接报错；确需兜底时打印 `WARNING` 并标记 `fallback=True`。新增 `[BacktestRequest]`、`[Backtest] … requested/upstream/effective`、`[CryptoKline] …` 等诊断日志，便于排查数据源覆盖问题。
- **回测后 K 线 Buy/Sell 标记错位**：指标 IDE 运行回测后，K 线上的 B / S 标记可能整体往后偏移一根 K 线（多时间框架 MTF 模式下尤为明显）。根因有两点：
  1. 开启 MTF 后，后端执行时间框架（exec_tf）会自动切换到 `1m` 或 `5m`，`trade.time` 记录的是 exec_tf 级时间戳；但前端 K 线显示的是用户选择的信号 TF（如 `1h`）。
  2. 前端使用「就近」对齐（nearest-snap），当 SL / TP / Trailing 等触发发生在信号 TF 柱的后半段时，会被吸附到**下一根**柱，造成整根柱的错位。

  修复：
  - 后端 `_simulate_trading_mtf` 对每笔 trade 新增 `bar_time` 字段 —— 把 exec_tf 时间戳 floor 到信号 TF，得到 trade 实际所属的**图表柱**起点时间（UTC，`'%Y-%m-%d %H:%M'`）。
  - 前端 `renderBacktestSignals` 改为**优先使用 `trade.bar_time`**（已经是图表柱对齐），并把「就近」改为 **floor-snap**（定位到包含该时间的最后一根 K 线），彻底消除 ±1 根柱的偏移。
  - 非 MTF 路径无需改动：`trade.time` 本身就等于信号 TF 柱时间，前端回退到 `trade.time` 后依旧正确对齐。
  - 改动文件：`backend_api_python/app/services/backtest.py`、`QuantDinger-Vue-src/src/views/indicator-ide/index.vue`。

### 🗄️ Database Migration

本次新增一列 + 一个索引，用于指标社区「同步代码」定位买家本地副本：

```sql
-- 1. 新列：买家本地副本 -> 市场原始指标 的外键关联（软外键，NULL 兼容老数据）
ALTER TABLE qd_indicator_codes
    ADD COLUMN IF NOT EXISTS source_indicator_id INTEGER;

CREATE INDEX IF NOT EXISTS idx_indicator_codes_source
    ON qd_indicator_codes USING btree (source_indicator_id);

-- 2. 可选回填：给已有的已购副本按名称回写 source_indicator_id
--    安全条件：仅写 is_buy=1 且 source_indicator_id IS NULL 的行，按 (买家ID, 原指标名) 匹配
UPDATE qd_indicator_codes lc
SET    source_indicator_id = p.indicator_id
FROM   qd_indicator_purchases p
JOIN   qd_indicator_codes orig ON orig.id = p.indicator_id
WHERE  lc.user_id = p.buyer_id
  AND  lc.is_buy = 1
  AND  lc.source_indicator_id IS NULL
  AND  lc.name = orig.name;
```

**已在开发环境 Docker 中执行完毕**（`ALTER TABLE` + `CREATE INDEX` 均返回成功，回填 `UPDATE 4`）。新库使用当前仓库中的 `migrations/init.sql` 初始化已包含该列定义，无需重复执行。

**在已有库上手动执行（Docker 一行示例）：**

```bash
docker compose exec -T postgres psql -U quantdinger -d quantdinger <<'SQL'
ALTER TABLE qd_indicator_codes ADD COLUMN IF NOT EXISTS source_indicator_id INTEGER;
CREATE INDEX IF NOT EXISTS idx_indicator_codes_source ON qd_indicator_codes USING btree (source_indicator_id);
UPDATE qd_indicator_codes lc
SET source_indicator_id = p.indicator_id
FROM qd_indicator_purchases p
JOIN qd_indicator_codes orig ON orig.id = p.indicator_id
WHERE lc.user_id = p.buyer_id
  AND lc.is_buy = 1
  AND lc.source_indicator_id IS NULL
  AND lc.name = orig.name;
SQL
```

> 服务启动时 `CommunityService.__init__` 亦带 `ADD COLUMN IF NOT EXISTS`，作为冗余保障（向后兼容）。

### 🎨 Frontend / i18n

- `QuantDinger-Vue-src/package.json`、`src/config/defaultSettings.js`、`src/layouts/BasicLayout.vue` 版本号 `3.0.1 → 3.0.2`；`README.md` 与 `docs/README_CN.md` 版本徽章同步。
- `zh-CN / zh-TW / en-US` 新增 12 条 `community.sync*` / `community.hasUpdate` / `community.already_latest` 等 i18n key；其他语言沿用英文 fallback。
- 重新执行 `npm run build` 并同步 `dist/` 至 `frontend/dist/`，`docker compose build frontend` 已重打镜像。
- **补丁**：回测 Buy/Sell 标记错位修复后再次 `npm run build` + 同步 `frontend/dist/` + `docker compose build backend frontend && up -d backend frontend`，无需额外数据库变更。

---

## 2026-04-07 — 数据库：`qd_market_symbols` 补充 A股 / H股热门标的

已在 **Docker** 内对运行中的 PostgreSQL 执行完毕（`INSERT 0 20`）。**新库**若使用当前仓库中的 `migrations/init.sql` 初始化，已包含同批种子数据，无需重复执行。

**在已有库上手动执行（等价 SQL，可重复执行，`ON CONFLICT DO NOTHING`）：**

```sql
INSERT INTO qd_market_symbols (market, symbol, name, exchange, currency, is_active, is_hot, sort_order) VALUES
('CNStock', '600519', '贵州茅台', 'SSE', 'CNY', 1, 1, 100),
('CNStock', '600036', '招商银行', 'SSE', 'CNY', 1, 1, 99),
('CNStock', '601318', '中国平安', 'SSE', 'CNY', 1, 1, 98),
('CNStock', '600900', '长江电力', 'SSE', 'CNY', 1, 1, 97),
('CNStock', '601899', '紫金矿业', 'SSE', 'CNY', 1, 1, 96),
('CNStock', '000858', '五粮液', 'SZSE', 'CNY', 1, 1, 95),
('CNStock', '000333', '美的集团', 'SZSE', 'CNY', 1, 1, 94),
('CNStock', '002594', '比亚迪', 'SZSE', 'CNY', 1, 1, 93),
('CNStock', '300750', '宁德时代', 'SZSE', 'CNY', 1, 1, 92),
('CNStock', '000001', '平安银行', 'SZSE', 'CNY', 1, 1, 91),
('HKStock', '00700', '腾讯控股', 'HKEX', 'HKD', 1, 1, 100),
('HKStock', '09988', '阿里巴巴-W', 'HKEX', 'HKD', 1, 1, 99),
('HKStock', '03690', '美团-W', 'HKEX', 'HKD', 1, 1, 98),
('HKStock', '01810', '小米集团-W', 'HKEX', 'HKD', 1, 1, 97),
('HKStock', '00939', '建设银行', 'HKEX', 'HKD', 1, 1, 96),
('HKStock', '01299', '友邦保险', 'HKEX', 'HKD', 1, 1, 95),
('HKStock', '02318', '中国平安', 'HKEX', 'HKD', 1, 1, 94),
('HKStock', '00388', '香港交易所', 'HKEX', 'HKD', 1, 1, 93),
('HKStock', '00883', '中国海洋石油', 'HKEX', 'HKD', 1, 1, 92),
('HKStock', '01398', '工商银行', 'HKEX', 'HKD', 1, 1, 91)
ON CONFLICT (market, symbol) DO NOTHING;
```

**Docker 一行示例（文件需 UTF-8）：**

```bash
docker cp backend_api_python/migrations/<your>.sql quantdinger-db:/tmp/migrate.sql
docker compose exec -T postgres psql -U quantdinger -d quantdinger -f /tmp/migrate.sql
```

---

## V3.0.1 (2026-04-05) — Frontend / docs

- **前端版本**：私有 Vue 仓库 `package.json`、页脚展示与 `frontend/VERSION` 统一为 **3.0.1**。
- **文档**：根目录 `README.md` 与 `docs/README_CN.md` 补充 QuantDinger 专属交易所邀请注册链接表（与个人中心「开户」一致），版本徽章更新为 3.0.1。
- **回测中心**：暗黑主题下图标与「添加标的」等弹窗样式对齐（`a-icon`、图表标题区、Modal 挂载层）。

---

## V2.2.4 (2026-04-05)

### 🚀 New Features

- **真实策略回测主链路**: 新增基于 `strategyId` 的策略回测入口，支持已保存的 `IndicatorStrategy` 与 `ScriptStrategy`，不再只是“取指标再跑一次指标回测”。
- **策略快照解析层**: 后端新增统一策略快照解析逻辑，把 `indicator_config`、`trading_config`、`strategy_code` 解析为可回测的标准输入。
- **策略回测历史与详情**: 回测记录现在可区分 `indicator` / `strategy_indicator` / `strategy_script`，并支持策略回测历史、详情查看和 AI 修正建议链路。
- **交易助手联动回测中心**: 交易助手中的策略项新增回测跳转入口，可直接带 `strategy_id` 进入回测中心。

### 🐛 Bug Fixes

- Fixed the previous “策略回测” pseudo-flow that only reused `/api/indicator/backtest` and could not faithfully replay stored strategies.
- Fixed strategy backtest history semantics so records can be linked to concrete strategies instead of only relying on `indicator_id`.
- Fixed strategy backtest UI entry restoration in Backtest Center and wired the strategy selector/history drawer to real backend endpoints.

### 🎨 UI/UX Improvements

- Restored the `回测中心 -> 策略回测` tab with strategy summary cards and environment override controls.
- Unified strategy backtest history display with the existing run viewer and AI suggestion modal.

### 📋 Database Migration

**在已有 PostgreSQL 库上执行（新库若已通过更新后的 `migrations/init.sql` 初始化则无需再执行）：**

```sql
-- ============================================================
-- QuantDinger V2.2.4 Database Migration
-- Strategy Backtest Persistence Upgrade
-- ============================================================

ALTER TABLE qd_backtest_runs ADD COLUMN IF NOT EXISTS strategy_id INTEGER;
ALTER TABLE qd_backtest_runs ADD COLUMN IF NOT EXISTS strategy_name VARCHAR(255) DEFAULT '';
ALTER TABLE qd_backtest_runs ADD COLUMN IF NOT EXISTS run_type VARCHAR(50) DEFAULT 'indicator';
ALTER TABLE qd_backtest_runs ADD COLUMN IF NOT EXISTS config_snapshot TEXT DEFAULT '';
ALTER TABLE qd_backtest_runs ADD COLUMN IF NOT EXISTS engine_version VARCHAR(50) DEFAULT '';
ALTER TABLE qd_backtest_runs ADD COLUMN IF NOT EXISTS code_hash VARCHAR(128) DEFAULT '';

CREATE INDEX IF NOT EXISTS idx_backtest_runs_strategy_id ON qd_backtest_runs(strategy_id);
CREATE INDEX IF NOT EXISTS idx_backtest_runs_run_type ON qd_backtest_runs(run_type);

CREATE TABLE IF NOT EXISTS qd_backtest_trades (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL DEFAULT 1 REFERENCES qd_users(id) ON DELETE CASCADE,
    strategy_id INTEGER,
    trade_index INTEGER DEFAULT 0,
    trade_time VARCHAR(64) DEFAULT '',
    trade_type VARCHAR(64) DEFAULT '',
    side VARCHAR(32) DEFAULT '',
    price DOUBLE PRECISION DEFAULT 0,
    amount DOUBLE PRECISION DEFAULT 0,
    profit DOUBLE PRECISION DEFAULT 0,
    balance DOUBLE PRECISION DEFAULT 0,
    reason VARCHAR(64) DEFAULT '',
    payload_json TEXT DEFAULT '',
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_backtest_trades_run_id ON qd_backtest_trades(run_id);

CREATE TABLE IF NOT EXISTS qd_backtest_equity_points (
    id SERIAL PRIMARY KEY,
    run_id INTEGER NOT NULL,
    point_index INTEGER DEFAULT 0,
    point_time VARCHAR(64) DEFAULT '',
    point_value DOUBLE PRECISION DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_backtest_equity_points_run_id ON qd_backtest_equity_points(run_id);
```

### 📝 Migration Notes

- All statements are idempotent and safe to run multiple times.
- Existing backtest data is preserved.
- Existing `indicator` backtest records remain compatible; new strategy backtests will write `run_type`, `strategy_id`, `strategy_name`, `config_snapshot`, `engine_version`, and `code_hash`.
- `qd_backtest_trades` and `qd_backtest_equity_points` are introduced for future strategy-level analytics and debugging.

---

## V2.2.3 (2026-03-24)

### 🚀 New Features

- **User profile IANA timezone (`qd_users.timezone`)**: 个人资料可保存时区（IANA 标识，如 `Asia/Shanghai`）；为空表示跟随浏览器。登录态 `/api/auth/info`、资料接口与前端 AI 分析页等时间展示会按该时区调用 `toLocaleString(..., { timeZone })`（非法或空则回退本机时区）。

### 📋 Database Migration

**在已有 PostgreSQL 库上执行（新库若已通过更新后的 `migrations/init.sql` 初始化则无需再执行）：**

```sql
-- ============================================================
-- QuantDinger V2.2.3 — qd_users.timezone（用户资料时区）
-- ============================================================

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public'
          AND table_name = 'qd_users'
          AND column_name = 'timezone'
    ) THEN
        ALTER TABLE qd_users ADD COLUMN timezone VARCHAR(64) DEFAULT '';
        RAISE NOTICE 'Added timezone column to qd_users table';
    END IF;
END $$;
```

**仅当列不存在时的一行式写法（自行确认无列后再执行）：**

```sql
ALTER TABLE qd_users ADD COLUMN IF NOT EXISTS timezone VARCHAR(64) DEFAULT '';
```

> 说明：`ALTER TABLE ... ADD COLUMN IF NOT EXISTS` 需 **PostgreSQL 11+**（本仓库 Docker 默认 `postgres:16` 可用）；与上面 `DO` 块二选一即可。

---

## V2.2.2 (2026-02-28)

### 🚀 New Features

#### Polymarket Prediction Markets Integration 🔮
- **Prediction Market Analysis**: Integrated Polymarket prediction markets as a new data source for AI analysis
- **AI-Driven Insights**: AI analyzes prediction market events and compares AI predictions with market consensus
- **Opportunity Discovery**: Identifies undervalued prediction opportunities with AI vs market divergence analysis
- **Asset Trading Recommendations**: Links prediction market events to related asset trading opportunities (e.g., BTC/USDT, ETH/USDT)
- **Data Analysis Only**: Focuses on data analysis and trading opportunity recommendations without live trading
- **Frontend Pages**: New `/polymarket` page with market listings, filtering, sorting, and search functionality
- **Market Detail View**: Comprehensive analysis view showing market info, AI analysis results, and related asset opportunities
- **AI Trading Radar Integration**: Prediction market opportunities appear in the AI Trading Radar alongside Crypto, US Stocks, and Forex

### 🐛 Bug Fixes
- Fixed duplicate `common.refresh` key in internationalization files (`zh-CN.js` and `en-US.js`)
- Fixed OKX position `entry_price` extraction (now correctly reads `avgPx`, `avgPxEp`, or `last` from position data)
- Improved symbol normalization across all exchanges to handle edge cases (e.g., PI, TRX without quote currency)
- Enhanced LLM provider fallback mechanism to handle 403/402/404/429 errors automatically

### 🎨 UI/UX Improvements
- Added Polymarket market cards with AI analysis summaries and opportunity scores
- Enhanced AI Trading Radar to display prediction market opportunities with distinct styling
- Improved symbol selector in Quick Trade panel with watchlist integration

### 📋 Database Migration

**Run the following SQL on your PostgreSQL database before deploying V2.2.2:**

```sql
-- ============================================================
-- QuantDinger V2.2.2 Database Migration
-- Polymarket Prediction Markets Integration
-- ============================================================

-- 预测市场表（缓存）
CREATE TABLE IF NOT EXISTS qd_polymarket_markets (
    id SERIAL PRIMARY KEY,
    market_id VARCHAR(255) UNIQUE NOT NULL,
    question TEXT,
    category VARCHAR(100),  -- crypto, politics, economics, sports
    current_probability DECIMAL(5,2),  -- YES概率（0-100）
    volume_24h DECIMAL(20,2),
    liquidity DECIMAL(20,2),
    end_date_iso TIMESTAMP,
    status VARCHAR(50),  -- active, closed, resolved
    outcome_tokens JSONB,  -- YES/NO价格和交易量
    slug VARCHAR(255),  -- Polymarket事件slug，用于构建URL
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 添加slug字段（如果表已存在但字段不存在）
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'qd_polymarket_markets' AND column_name = 'slug'
    ) THEN
        ALTER TABLE qd_polymarket_markets ADD COLUMN slug VARCHAR(255);
        RAISE NOTICE 'Added slug column to qd_polymarket_markets';
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_polymarket_category ON qd_polymarket_markets(category);
CREATE INDEX IF NOT EXISTS idx_polymarket_status ON qd_polymarket_markets(status);
CREATE INDEX IF NOT EXISTS idx_polymarket_updated ON qd_polymarket_markets(updated_at DESC);

-- AI分析记录表
CREATE TABLE IF NOT EXISTS qd_polymarket_ai_analysis (
    id SERIAL PRIMARY KEY,
    market_id VARCHAR(255) NOT NULL,
    user_id INTEGER,  -- 可选：用户特定的分析
    ai_predicted_probability DECIMAL(5,2),
    market_probability DECIMAL(5,2),
    divergence DECIMAL(5,2),  -- AI - 市场
    recommendation VARCHAR(20),  -- YES/NO/HOLD
    confidence_score DECIMAL(5,2),
    opportunity_score DECIMAL(5,2),
    reasoning TEXT,
    key_factors JSONB,
    related_assets TEXT[],  -- 相关资产列表
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_polymarket_analysis_market ON qd_polymarket_ai_analysis(market_id);
CREATE INDEX IF NOT EXISTS idx_polymarket_analysis_opportunity ON qd_polymarket_ai_analysis(opportunity_score DESC);
CREATE INDEX IF NOT EXISTS idx_polymarket_analysis_user ON qd_polymarket_ai_analysis(user_id);

-- 资产交易机会表（基于预测市场生成）
CREATE TABLE IF NOT EXISTS qd_polymarket_asset_opportunities (
    id SERIAL PRIMARY KEY,
    market_id VARCHAR(255) NOT NULL,
    asset_symbol VARCHAR(100),
    asset_market VARCHAR(50),
    signal VARCHAR(20),  -- BUY/SELL/HOLD
    confidence DECIMAL(5,2),
    reasoning TEXT,
    entry_suggestion JSONB,  -- 入场建议
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_polymarket_opp_market ON qd_polymarket_asset_opportunities(market_id);
CREATE INDEX IF NOT EXISTS idx_polymarket_opp_asset ON qd_polymarket_asset_opportunities(asset_symbol, asset_market);

-- Migration Complete
DO $$
BEGIN
    RAISE NOTICE '✅ QuantDinger V2.2.2 database migration completed!';
END $$;
```

**Migration Notes:**
- All statements use `IF NOT EXISTS` — safe to run multiple times
- No existing data is modified or deleted
- New tables are created for Polymarket data caching and AI analysis
- Polymarket integration is read-only (data analysis only, no live trading)

### 📝 Configuration Notes
- No new environment variables required for basic Polymarket integration
- Polymarket data source uses placeholder/dummy data by default (can be extended with actual API integration)
- AI analysis leverages existing LLM configuration from System Settings

---

## V2.2.1 (2026-02-27)

### 🚀 New Features

#### Membership & Billing System
- **Subscription Plans**: Monthly / Yearly / Lifetime tiers with configurable pricing and credit bundles
- **Credit System**: Each plan includes credits; lifetime members receive recurring monthly credit bonuses
- **Plan Management**: All plan prices, credits, and bonus amounts configurable via System Settings → Billing Configuration
- **Membership Orders**: Order tracking with status management (paid / pending / failed / refunded)

#### USDT On-Chain Payment (TRC20)
- **HD Wallet Integration**: Per-order unique receiving address derived from xpub (BIP-32/44) — no private key on server
- **Automatic Reconciliation**: Background polling via TronGrid API detects incoming payments and confirms orders
- **Depth-Flexible xpub**: Supports both account-level (depth=3) and change-level (depth=4) xpub keys
- **Configurable Expiry**: Order expiration time and confirmation delay configurable in System Settings
- **Scan-to-Pay Modal**: Professional checkout UI with QR code, step indicator, real-time status, copy-to-clipboard, dark theme support

#### VIP Free Indicators
- **VIP Free Tag**: Admins can mark community indicators as "VIP Free" when publishing
- **Zero-Credit Access**: VIP members can use VIP-free indicators without spending credits
- **Visual Badge**: VIP Free indicators display a distinct badge in the Indicator Market

#### AI Trading Opportunities Radar
- **Multi-Market Scanning**: Auto-scans Crypto, US Stocks, and Forex markets every hour
- **Rolling Carousel**: Opportunities displayed in a rotating carousel with market-specific styling
- **Signal Classification**: BUY / SELL signals with percentage change and reason text
- **Multi-Language**: All radar card content fully internationalized

#### Simplified Strategy Creation
- **Simple / Advanced Mode Toggle**: New users start with simplified mode, power users can switch to advanced
- **Smart Defaults**: 15-minute K-line period, 5x leverage, market order, sensible TP/SL percentages
- **Live Trading Disclaimer**: Mandatory risk acknowledgment checkbox before enabling live trading

#### System Settings Simplification
- **Streamlined Configuration**: Removed redundant config groups (server, strategy); consolidated into essential categories
- **Market Order Default**: Changed default order mode to market order for reliable execution
- **Billing Config i18n**: All billing configuration items fully multi-language supported

#### Quick Trade Panel (闪电交易) 🆕
- **Side-Sliding Drawer**: Professional trading panel slides in from the right, allowing instant order placement without leaving the analysis page
- **Multi-Exchange Support**: Select from saved exchange credentials (Binance, OKX, Bitget, Bybit, etc.) with real-time balance display
- **Long/Short Toggle**: Color-coded direction buttons with one-click switching
- **Market / Limit Orders**: Toggle between market and limit order types; limit orders accept a specific price
- **Leverage Slider**: Interactive 1x–125x leverage control for futures trading
- **TP/SL Price Setting**: Optional take-profit and stop-loss by **absolute price** (not percentage)
- **Current Position Display**: Shows open position with side, size, entry price, unrealized PnL, and one-click close button
- **Recent Trade History**: Displays last 5 quick trades with status tags
- **AI Radar Integration**: "Trade Now" button on each AI Trading Opportunities card pre-fills symbol, direction, and price
- **Indicator Analysis Integration**: Quick Trade button in chart header and floating ⚡ button pre-fills current symbol and price
- **Auto-Polling**: Balance and position data refresh every 10 seconds
- **Full Dark Theme**: Complete dark mode support for all panel elements
- **Multi-Language**: All labels and messages fully internationalized (zh-CN / en-US)

#### Indicator Market Performance Tracking
- **Live Performance Data**: Fixed aggregation to correctly parse backtest `result_json` and include live trade data
- **Combined Metrics**: Backtest return, live PnL, and win rate now properly displayed on indicator cards

### 🐛 Bug Fixes
- Fixed `quick_trade.py` importing from non-existent `auth_utils` module (corrected to `auth`)
- Fixed "Live Performance" data showing all zeros in Indicator Market (incorrect SQL query referencing non-existent columns)
- Fixed incorrect entry price display in Position Records (was falling back to current price)
- Fixed inaccurate System Overview statistics for running strategies, total capital, and total PnL
- Fixed multiple duplicate i18n key issues in `zh-CN.js` and `en-US.js` causing ESLint build failures
- Fixed exposed i18n keys (`common.loading`, `common.noData`, `systemOverview.*`) not configured
- Fixed HTML nesting issues in trading assistant strategy creation form
- Fixed `ed25519-blake2b` build failure in Docker by adding temporary build dependencies
- Fixed "Current depth (3) is not suitable for deriving address" error for xpub — now compatible with both depth 3 and depth 4

### 🎨 UI/UX Improvements
- Removed "Total Analyses" / "Accuracy Rate" row from homepage AI Analysis section
- Removed "Search" and "Portfolio Checkup" features from AI Asset Analysis page
- Professional USDT checkout modal with custom header, step indicator, dual-column layout
- Dark theme and mobile responsive support for payment modal
- Trading Opportunities Radar carousel with smooth scrolling animation

### 📋 Database Migration

**Run the following SQL on your PostgreSQL database before deploying V2.2.1:**

```sql
-- ============================================================
-- QuantDinger V2.2.1 Database Migration
-- Membership, USDT Payment, VIP Free Indicators
-- ============================================================

-- 1. User Table: Add membership columns
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'qd_users' AND column_name = 'vip_plan'
    ) THEN
        ALTER TABLE qd_users ADD COLUMN vip_plan VARCHAR(20) DEFAULT '';
        RAISE NOTICE 'Added vip_plan column to qd_users';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'qd_users' AND column_name = 'vip_is_lifetime'
    ) THEN
        ALTER TABLE qd_users ADD COLUMN vip_is_lifetime BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added vip_is_lifetime column to qd_users';
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'qd_users' AND column_name = 'vip_monthly_credits_last_grant'
    ) THEN
        ALTER TABLE qd_users ADD COLUMN vip_monthly_credits_last_grant TIMESTAMP;
        RAISE NOTICE 'Added vip_monthly_credits_last_grant column to qd_users';
    END IF;
END $$;

-- 2. Indicator Codes: Add VIP Free flag
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'qd_indicator_codes' AND column_name = 'vip_free'
    ) THEN
        ALTER TABLE qd_indicator_codes ADD COLUMN vip_free BOOLEAN DEFAULT FALSE;
        RAISE NOTICE 'Added vip_free column to qd_indicator_codes';
    END IF;
END $$;

-- 3. Membership Orders table
CREATE TABLE IF NOT EXISTS qd_membership_orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES qd_users(id) ON DELETE CASCADE,
    plan VARCHAR(20) NOT NULL,
    price_usd DECIMAL(10,2) DEFAULT 0,
    status VARCHAR(20) DEFAULT 'paid',
    created_at TIMESTAMP DEFAULT NOW(),
    paid_at TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_membership_orders_user_id ON qd_membership_orders(user_id);

-- 4. USDT Orders table (on-chain payment tracking)
CREATE TABLE IF NOT EXISTS qd_usdt_orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES qd_users(id) ON DELETE CASCADE,
    plan VARCHAR(20) NOT NULL,
    chain VARCHAR(20) NOT NULL DEFAULT 'TRC20',
    amount_usdt DECIMAL(20,6) NOT NULL DEFAULT 0,
    address_index INTEGER NOT NULL DEFAULT 0,
    address VARCHAR(80) NOT NULL DEFAULT '',
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    tx_hash VARCHAR(120) DEFAULT '',
    paid_at TIMESTAMP,
    confirmed_at TIMESTAMP,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_usdt_orders_address_unique ON qd_usdt_orders(chain, address);
CREATE INDEX IF NOT EXISTS idx_usdt_orders_user_id ON qd_usdt_orders(user_id);
CREATE INDEX IF NOT EXISTS idx_usdt_orders_status ON qd_usdt_orders(status);

-- 5. Quick Trades table (manual / discretionary orders from Quick Trade Panel)
CREATE TABLE IF NOT EXISTS qd_quick_trades (
    id              SERIAL PRIMARY KEY,
    user_id         INTEGER NOT NULL REFERENCES qd_users(id) ON DELETE CASCADE,
    credential_id   INTEGER DEFAULT 0,
    exchange_id     VARCHAR(40) NOT NULL DEFAULT '',
    symbol          VARCHAR(60) NOT NULL DEFAULT '',
    side            VARCHAR(10) NOT NULL DEFAULT '',       -- buy / sell
    order_type      VARCHAR(20) NOT NULL DEFAULT 'market', -- market / limit
    amount          DECIMAL(24, 8) DEFAULT 0,
    price           DECIMAL(24, 8) DEFAULT 0,
    leverage        INTEGER DEFAULT 1,
    market_type     VARCHAR(20) DEFAULT 'swap',            -- swap / spot
    tp_price        DECIMAL(24, 8) DEFAULT 0,
    sl_price        DECIMAL(24, 8) DEFAULT 0,
    status          VARCHAR(20) DEFAULT 'submitted',       -- submitted / filled / failed / cancelled
    exchange_order_id VARCHAR(120) DEFAULT '',
    filled_amount   DECIMAL(24, 8) DEFAULT 0,
    avg_fill_price  DECIMAL(24, 8) DEFAULT 0,
    error_msg       TEXT DEFAULT '',
    source          VARCHAR(40) DEFAULT 'manual',          -- ai_radar / ai_analysis / indicator / manual
    raw_result      JSONB,
    created_at      TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_quick_trades_user    ON qd_quick_trades(user_id);
CREATE INDEX IF NOT EXISTS idx_quick_trades_created ON qd_quick_trades(created_at DESC);

-- Migration Complete
DO $$
BEGIN
    RAISE NOTICE '✅ QuantDinger V2.2.1 database migration completed!';
END $$;
```

**Migration Notes:**
- All statements use `IF NOT EXISTS` — safe to run multiple times
- No existing data is modified or deleted
- New `.env` variables required for USDT payment: `USDT_PAY_ENABLED`, `USDT_TRC20_XPUB`, `TRONGRID_API_KEY`
- New `.env` variables for membership pricing: `MEMBERSHIP_MONTHLY_PRICE_USD`, `MEMBERSHIP_MONTHLY_CREDITS`, etc.
- See `backend_api_python/env.example` for all new configuration options

### 📝 Configuration Notes

New environment variables (all optional, with defaults):

| Variable | Default | Description |
|----------|---------|-------------|
| `MEMBERSHIP_MONTHLY_PRICE_USD` | `19.9` | Monthly plan price |
| `MEMBERSHIP_MONTHLY_CREDITS` | `500` | Credits included in monthly plan |
| `MEMBERSHIP_YEARLY_PRICE_USD` | `169` | Yearly plan price |
| `MEMBERSHIP_YEARLY_CREDITS` | `8000` | Credits included in yearly plan |
| `MEMBERSHIP_LIFETIME_PRICE_USD` | `499` | Lifetime plan price |
| `MEMBERSHIP_LIFETIME_CREDITS` | `30000` | Initial credits for lifetime plan |
| `MEMBERSHIP_LIFETIME_MONTHLY_BONUS` | `500` | Monthly bonus credits for lifetime members |
| `USDT_PAY_ENABLED` | `false` | Enable USDT TRC20 payment |
| `USDT_TRC20_XPUB` | _(empty)_ | TRC20 HD wallet xpub for address derivation |
| `TRONGRID_API_KEY` | _(empty)_ | TronGrid API key for on-chain monitoring |
| `USDT_ORDER_EXPIRE_MINUTES` | `30` | USDT order expiration time |

---

## V2.1.3 (2026-02-XX)

### 🚀 New Features

#### Cross-Sectional Strategy Support
- **Multi-Symbol Portfolio Management** - Added support for cross-sectional strategies that manage a portfolio of multiple symbols simultaneously
  - Strategy type selection: Single Symbol vs Cross-Sectional
  - Symbol list configuration: Select multiple symbols for portfolio management
  - Portfolio size: Configure the number of symbols to hold simultaneously
  - Long/Short ratio: Set the proportion of long vs short positions (0-1)
  - Rebalance frequency: Daily, Weekly, or Monthly portfolio rebalancing
  - Indicator execution: Indicators receive a `data` dictionary (symbol -> DataFrame) for cross-symbol analysis
  - Signal generation: Automatic buy/sell/close signals based on indicator rankings
  - Parallel execution: Multiple orders executed concurrently for efficiency
- **Backend Implementation**
  - Cross-sectional configurations stored in `trading_config` JSON field
  - New `_run_cross_sectional_strategy_loop` method in TradingExecutor
  - Automatic rebalancing based on configured frequency
  - Support for both long and short positions in the same portfolio
- **Frontend UI**
  - Strategy type selector in strategy creation/editing form
  - Conditional display of single-symbol vs cross-sectional configuration fields
  - Multi-select symbol picker for cross-sectional strategies
  - Full i18n support (Chinese and English)

See `docs/CROSS_SECTIONAL_STRATEGY_GUIDE_CN.md` or `docs/CROSS_SECTIONAL_STRATEGY_GUIDE_EN.md` for detailed usage instructions.

### 🐛 Bug Fixes
- Fixed decimal precision issues in exchange order quantities (Binance Spot LOT_SIZE filter errors)
- Improved `_dec_str` method across all exchange clients for accurate quantity formatting
- Enhanced quantity normalization to respect exchange precision requirements
- Fixed validation logic for cross-sectional strategies (now validates correct symbol list field)
- Fixed success message to show correct strategy count for cross-sectional strategies

### 📋 Database Migration

**Run the following SQL on your PostgreSQL database before deploying V2.1.3:**

```sql
-- ============================================================
-- QuantDinger V2.1.3 Database Migration
-- Cross-Sectional Strategy Support
-- ============================================================

-- Add last_rebalance_at column to track rebalancing time for cross-sectional strategies
-- Note: Cross-sectional strategy configurations (symbol_list, portfolio_size, long_ratio, rebalance_frequency)
-- are stored in the trading_config JSON field, not as separate database columns.
-- This migration only adds the last_rebalance_at timestamp field which is needed for rebalancing logic.

DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'qd_strategies_trading' 
        AND column_name = 'last_rebalance_at'
    ) THEN
        ALTER TABLE qd_strategies_trading 
        ADD COLUMN last_rebalance_at TIMESTAMP;
        RAISE NOTICE 'Added last_rebalance_at column to qd_strategies_trading';
    ELSE
        RAISE NOTICE 'Column last_rebalance_at already exists';
    END IF;
END $$;
```

**Migration Notes:**
- This migration is safe to run multiple times (uses IF NOT EXISTS check)
- Cross-sectional strategy configurations are stored in the `trading_config` JSON field, so no additional columns are needed
- The `last_rebalance_at` field is used to track when the last rebalancing occurred for cross-sectional strategies
- If you don't run this migration, cross-sectional strategies will still work, but rebalancing frequency checks may not function correctly

---

## V2.1.2 (2026-02-01)

### 🚀 New Features

#### Indicator Parameter Support
- **External Parameter Passing** - Indicators can now declare parameters using `# @param` syntax that can be configured per-strategy
  - Supported types: `int`, `float`, `bool`, `str`
  - Parameters are displayed in the strategy creation form after selecting an indicator
  - Different strategies using the same indicator can have different parameter values
- **Cross-Indicator Calling** - Indicators can now call other indicators using `call_indicator(id_or_name, df)` function
  - Supports calling by indicator ID (number) or name (string)
  - Maximum call depth of 5 to prevent circular dependencies
  - Only allows calling own indicators or published community indicators

#### Parameter Declaration Syntax
```
# @param <name> <type> <default> <description>
```

| Field | Description | Example |
|-------|-------------|---------|
| name | Parameter name (variable name) | `ma_fast` |
| type | Data type: `int`, `float`, `bool`, `str` | `int` |
| default | Default value | `5` |
| description | Description (shown in UI tooltip) | `Short-term MA period` |

#### Example: Dual Moving Average with Parameters
```python
# @param sma_short int 14 Short-term MA period
# @param sma_long int 28 Long-term MA period

# Get parameters
sma_short_period = params.get('sma_short', 14)
sma_long_period = params.get('sma_long', 28)

my_indicator_name = "Dual MA Strategy"
my_indicator_description = f"SMA{sma_short_period}/{sma_long_period} crossover"

df = df.copy()
sma_short = df["close"].rolling(sma_short_period).mean()
sma_long = df["close"].rolling(sma_long_period).mean()

# Golden cross / Death cross
buy = (sma_short > sma_long) & (sma_short.shift(1) <= sma_long.shift(1))
sell = (sma_short < sma_long) & (sma_short.shift(1) >= sma_long.shift(1))

df["buy"] = buy.fillna(False).astype(bool)
df["sell"] = sell.fillna(False).astype(bool)

# Chart markers
buy_marks = [df["low"].iloc[i] * 0.995 if df["buy"].iloc[i] else None for i in range(len(df))]
sell_marks = [df["high"].iloc[i] * 1.005 if df["sell"].iloc[i] else None for i in range(len(df))]

output = {
    "name": my_indicator_name,
    "plots": [
        {"name": f"SMA{sma_short_period}", "data": sma_short.tolist(), "color": "#FF9800", "overlay": True},
        {"name": f"SMA{sma_long_period}", "data": sma_long.tolist(), "color": "#3F51B5", "overlay": True}
    ],
    "signals": [
        {"type": "buy", "text": "B", "data": buy_marks, "color": "#00E676"},
        {"type": "sell", "text": "S", "data": sell_marks, "color": "#FF5252"}
    ]
}
```

#### Example: Using call_indicator()
```python
# Call another indicator by name or ID
# rsi_df = call_indicator('RSI', df)           # By name
# rsi_df = call_indicator(5, df)               # By ID
# rsi_df = call_indicator('RSI', df, {'period': 14})  # With params

# Note: The called indicator must be created first
# and accessible (own indicator or published community indicator)
```

### 🐛 Bug Fixes

#### Dashboard Fixes
- **Fixed current positions showing records from other users** - Position synchronization now correctly associates positions with the strategy owner's user_id
- **Fixed strategy distribution pie chart always showing "No Data"** - Chart now uses `strategy_stats` data which includes all strategies with trading activity
- **Removed AI strategy count from running strategies card** - Dashboard now only shows indicator strategy count since AI strategies category has been removed

---

## V2.1.1 (2026-01-31)

### 🚀 New Features

#### AI Analysis System Overhaul
- **Fast Analysis Mode**: Replaced the complex multi-agent system with a streamlined single LLM call architecture for faster and more accurate analysis
- **Progressive Loading**: Market data now loads independently - each section (sentiment, indices, heatmap, calendar) displays as soon as it's ready
- **Professional Loading Animation**: New progress bar with step indicators during AI analysis
- **Analysis Memory**: Store analysis results for history review and user feedback
- **Stop Loss/Take Profit Calculation**: Now based on ATR (Average True Range) and Support/Resistance levels with clear methodology hints

#### Global Market Integration
- Integrated Global Market data directly into AI Analysis page
- Real-time scrolling display of major global indices with flags, prices, and percentage changes
- Interactive heatmaps for Crypto, Commodities, Sectors, and Forex
- Economic calendar with bullish/bearish/neutral impact indicators
- Commodities heatmap added (Gold, Silver, Crude Oil, etc.)

#### Indicator Community Enhancements
- **Admin Review System**: Administrators can now review, approve, reject, unpublish, and delete community indicators
- **Purchase & Rating System**: Users can buy indicators, leave ratings and comments
- **Statistics Tracking**: Purchase count, average rating, rating count, view count for each indicator

#### Trading Assistant Improvements
- Improved IBKR/MT5 connection test feedback
- Added local deployment warning for external trading platforms
- Virtual profit/loss calculation for signal-only strategies

### 🐛 Bug Fixes
- Fixed progress bar and timer not animating during AI analysis
- Fixed missing i18n translations for various components
- Fixed Tiingo API rate limit issues with caching
- Fixed data fetching with multiple fallback sources
- Fixed watchlist price batch fetch timeout handling
- Fixed heatmap multi-language support for commodities and forex
- **Fixed AI analysis history not filtered by user** - All users were seeing the same history records; now each user only sees their own analysis history
- **Fixed "Missing Turnstile token" error when changing password** - Logged-in users no longer need Turnstile verification to request password change verification code

### 🎨 UI/UX Improvements
- Reorganized left menu: Indicator Market moved below Indicator Analysis, Settings moved to bottom
- Skeleton loading animations for progressive data display
- Dark theme support for all new components
- Compact market overview bar design

### 📋 Database Migration

**Run the following SQL on your PostgreSQL database before deploying V2.1.1:**

```sql
-- ============================================================
-- QuantDinger V2.1.1 Database Migration
-- ============================================================

-- 1. AI Analysis Memory Table
CREATE TABLE IF NOT EXISTS qd_analysis_memory (
    id SERIAL PRIMARY KEY,
    market VARCHAR(50) NOT NULL,
    symbol VARCHAR(50) NOT NULL,
    decision VARCHAR(10) NOT NULL,
    confidence INT DEFAULT 50,
    price_at_analysis DECIMAL(24, 8),
    entry_price DECIMAL(24, 8),
    stop_loss DECIMAL(24, 8),
    take_profit DECIMAL(24, 8),
    summary TEXT,
    reasons JSONB,
    risks JSONB,
    scores JSONB,
    indicators_snapshot JSONB,
    raw_result JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    validated_at TIMESTAMP,
    actual_outcome VARCHAR(20),
    actual_return_pct DECIMAL(10, 4),
    was_correct BOOLEAN,
    user_feedback VARCHAR(20),
    feedback_at TIMESTAMP
);

-- Add raw_result column if table exists but column doesn't
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'qd_analysis_memory' AND column_name = 'raw_result'
    ) THEN
        ALTER TABLE qd_analysis_memory ADD COLUMN raw_result JSONB;
    END IF;
END $$;

-- Add user_id column for user-specific history filtering
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'qd_analysis_memory' AND column_name = 'user_id'
    ) THEN
        ALTER TABLE qd_analysis_memory ADD COLUMN user_id INT;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_analysis_memory_symbol ON qd_analysis_memory(market, symbol);
CREATE INDEX IF NOT EXISTS idx_analysis_memory_created ON qd_analysis_memory(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_memory_validated ON qd_analysis_memory(validated_at) WHERE validated_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_analysis_memory_user ON qd_analysis_memory(user_id);

-- 2. Indicator Purchase Records
CREATE TABLE IF NOT EXISTS qd_indicator_purchases (
    id SERIAL PRIMARY KEY,
    indicator_id INTEGER NOT NULL REFERENCES qd_indicator_codes(id) ON DELETE CASCADE,
    buyer_id INTEGER NOT NULL REFERENCES qd_users(id) ON DELETE CASCADE,
    seller_id INTEGER NOT NULL REFERENCES qd_users(id),
    price DECIMAL(10,2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(indicator_id, buyer_id)
);

CREATE INDEX IF NOT EXISTS idx_purchases_indicator ON qd_indicator_purchases(indicator_id);
CREATE INDEX IF NOT EXISTS idx_purchases_buyer ON qd_indicator_purchases(buyer_id);
CREATE INDEX IF NOT EXISTS idx_purchases_seller ON qd_indicator_purchases(seller_id);

-- 3. Indicator Comments
CREATE TABLE IF NOT EXISTS qd_indicator_comments (
    id SERIAL PRIMARY KEY,
    indicator_id INTEGER NOT NULL REFERENCES qd_indicator_codes(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES qd_users(id) ON DELETE CASCADE,
    rating INTEGER DEFAULT 5 CHECK (rating >= 1 AND rating <= 5),
    content TEXT DEFAULT '',
    parent_id INTEGER REFERENCES qd_indicator_comments(id) ON DELETE CASCADE,
    is_deleted INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_comments_indicator ON qd_indicator_comments(indicator_id);
CREATE INDEX IF NOT EXISTS idx_comments_user ON qd_indicator_comments(user_id);

-- 4. Indicator Codes Extensions
DO $$
BEGIN
    -- Purchase count
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'qd_indicator_codes' AND column_name = 'purchase_count'
    ) THEN
        ALTER TABLE qd_indicator_codes ADD COLUMN purchase_count INTEGER DEFAULT 0;
    END IF;
    
    -- Average rating
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'qd_indicator_codes' AND column_name = 'avg_rating'
    ) THEN
        ALTER TABLE qd_indicator_codes ADD COLUMN avg_rating DECIMAL(3,2) DEFAULT 0;
    END IF;
    
    -- Rating count
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'qd_indicator_codes' AND column_name = 'rating_count'
    ) THEN
        ALTER TABLE qd_indicator_codes ADD COLUMN rating_count INTEGER DEFAULT 0;
    END IF;
    
    -- View count
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'qd_indicator_codes' AND column_name = 'view_count'
    ) THEN
        ALTER TABLE qd_indicator_codes ADD COLUMN view_count INTEGER DEFAULT 0;
    END IF;
    
    -- Review status
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'qd_indicator_codes' AND column_name = 'review_status'
    ) THEN
        ALTER TABLE qd_indicator_codes ADD COLUMN review_status VARCHAR(20) DEFAULT 'approved';
        UPDATE qd_indicator_codes SET review_status = 'approved' WHERE publish_to_community = 1;
    END IF;
    
    -- Review note
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'qd_indicator_codes' AND column_name = 'review_note'
    ) THEN
        ALTER TABLE qd_indicator_codes ADD COLUMN review_note TEXT DEFAULT '';
    END IF;
    
    -- Reviewed at
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'qd_indicator_codes' AND column_name = 'reviewed_at'
    ) THEN
        ALTER TABLE qd_indicator_codes ADD COLUMN reviewed_at TIMESTAMP;
    END IF;
    
    -- Reviewed by
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'qd_indicator_codes' AND column_name = 'reviewed_by'
    ) THEN
        ALTER TABLE qd_indicator_codes ADD COLUMN reviewed_by INTEGER;
    END IF;
END $$;

CREATE INDEX IF NOT EXISTS idx_indicator_review_status ON qd_indicator_codes(review_status);

-- 5. User Table Extensions
DO $$
BEGIN
    -- Token version (for single-client login)
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'qd_users' AND column_name = 'token_version'
    ) THEN
        ALTER TABLE qd_users ADD COLUMN token_version INTEGER DEFAULT 1;
    END IF;
    
    -- Notification settings
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns 
        WHERE table_name = 'qd_users' AND column_name = 'notification_settings'
    ) THEN
        ALTER TABLE qd_users ADD COLUMN notification_settings TEXT DEFAULT '{}';
    END IF;
END $$;

-- Migration Complete
DO $$
BEGIN
    RAISE NOTICE '✅ QuantDinger V2.1.1 database migration completed!';
END $$;
```

### 🗑️ Removed
- Old multi-agent AI analysis system (`backend_api_python/app/services/agents/` directory)
- Old analysis routes and services
- Standalone Global Market page (merged into AI Analysis)
- Reflection worker background process

### ⚠️ Breaking Changes
- AI Analysis API endpoints changed from `/api/analysis/*` to `/api/fast-analysis/*`
- Old analysis history data is not compatible with new format

### 📝 Configuration Notes
- No new environment variables required
- Existing LLM configuration in System Settings will be used for AI Analysis

---

## Version History

| Version | Date | Highlights |
|---------|------|------------|
| V2.2.2 | 2026-02-28 | Polymarket prediction markets integration, AI-driven prediction analysis, asset trading recommendations |
| V2.2.1 | 2026-02-27 | Membership & Billing, USDT TRC20 payment, VIP free indicators, AI Trading Radar, simplified strategy creation |
| V2.1.3 | 2026-02-XX | Cross-sectional strategy support |
| V2.1.2 | 2026-02-01 | Indicator parameters, cross-indicator calling |
| V2.1.1 | 2026-01-31 | AI Analysis overhaul, Global Market integration, Indicator Community enhancements |

---

*For questions or issues, please open a GitHub issue or contact the maintainers.*
