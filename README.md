<div align="center">
  <a href="https://github.com/brokermr810/QuantDinger">
    <img src="https://ai.quantdinger.com/img/logo.e0f510a8.png" alt="QuantDinger Logo" width="160" height="160">
  </a>

  <h1>QuantDinger</h1>

  <h3>AI-Native Quantitative Trading Platform</h3>
  <p><strong>Vibe Coding Meets Algo Trading</strong></p>
  <p> 
  <a href="docs/README_CN.md"><strong>🇨🇳 中文</strong></a> &nbsp;·&nbsp;
  <a href="README.md"><strong>🇺🇸 English</strong></a> 
  </p>
  <p>
 
  <a href="https://ai.quantdinger.com"><strong>🌐 Live Demo</strong></a> &nbsp;·&nbsp;
  <a href="https://youtu.be/HPTVpqL7knM"><strong>📺 Video</strong></a> &nbsp;·&nbsp;
  <a href="https://www.quantdinger.com"><strong>💬 Community</strong></a> &nbsp;·&nbsp;
  <a href="#-quick-start-2-minutes"><strong>🚀 Quick Start</strong></a>
  </p>

  <p>
    <strong>7 AI Agents · Python Strategies · 10+ Exchanges · Prediction Markets · Your Server, Your Keys</strong>
  </p>
  <p>
    <i>Describe your trading idea in natural language → AI writes the Python strategy → Backtest → Live trade.<br/>
    Zero coding required. Self-hosted — your API keys and strategies never leave your machine.</i>
  </p>

  <p>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=flat-square&logo=apache" alt="License"></a>
    <img src="https://img.shields.io/badge/Version-2.2.3-orange?style=flat-square" alt="Version">
    <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Docker-One%20Click-2496ED?style=flat-square&logo=docker&logoColor=white" alt="Docker">
    <img src="https://img.shields.io/badge/Vibe%20Coding-Ready-FF6B6B?style=flat-square&logo=sparkles&logoColor=white" alt="Vibe Coding">
    <img src="https://img.shields.io/github/stars/brokermr810/QuantDinger?style=flat-square&logo=github" alt="Stars">
  </p>

  <p>
    <a href="https://t.me/quantdinger"><img src="https://img.shields.io/badge/Telegram-Group-26A5E4?style=for-the-badge&logo=telegram" alt="Telegram"></a>
    <a href="https://discord.gg/tyx5B6TChr"><img src="https://img.shields.io/badge/Discord-Server-5865F2?style=for-the-badge&logo=discord" alt="Discord"></a>
    <a href="https://x.com/HenryCryption"><img src="https://img.shields.io/badge/X-Follow-000000?style=for-the-badge&logo=x" alt="X"></a>
  </p>

  <sub>🇺🇸 <a href="README.md">English</a> · 🇨🇳 <a href="docs/README_CN.md">简体中文</a> · 🇹🇼 繁體中文 · 🇯🇵 日本語 · 🇰🇷 한국어 · 🇩🇪 Deutsch · 🇫🇷 Français · 🇹🇭 ไทย · 🇻🇳 Tiếng Việt · 🇸🇦 العربية</sub>
</div>

---

## 📑 Table of Contents

- [🚀 Quick Start (2 Minutes)](#-quick-start-2-minutes)
- [🎯 Why QuantDinger?](#-why-quantdinger)
- [📸 Visual Tour](#-visual-tour--watch-video-demo)
- [✨ Key Features](#-key-features)
- [🔌 Supported Exchanges & Brokers](#-supported-exchanges--brokers)
- [🏗️ Architecture & Configuration](#️-architecture--configuration)
- [📚 Documentation Index](#-documentation-index)
- [💼 License & Commercial](#-license--commercial)
- [🤝 Community & Support](#-community--support)

---

## 🚀 Quick Start (2 Minutes)

> **Only need**: [Docker](https://docs.docker.com/get-docker/) installed. Nothing else.

```bash
# 1. Clone
git clone https://github.com/brokermr810/QuantDinger.git
cd QuantDinger

# 2. Configure (edit admin password & AI API key)
cp backend_api_python/env.example backend_api_python/.env

# 3. Launch!
docker-compose up -d --build
```

> **Windows PowerShell**: use `Copy-Item backend_api_python\env.example -Destination backend_api_python\.env`

🎉 **Done!** Open **http://localhost:8888** | Login: `quantdinger` / `123456`

<details>
<summary><b>📝 Key settings in backend_api_python/.env</b></summary>

```ini
# Required — Change for production!
ADMIN_USER=quantdinger
ADMIN_PASSWORD=your_secure_password
SECRET_KEY=your_random_secret_key

# Optional — Enable AI features (pick one)
OPENROUTER_API_KEY=your_key        # Recommended: 100+ models
OPENAI_API_KEY=your_key            # GPT-4o
DEEPSEEK_API_KEY=your_key          # Cost-effective
GOOGLE_GEMINI_API_KEY=your_key     # Gemini
```

</details>

<details>
<summary><b>🔧 Common Docker Commands</b></summary>

```bash
docker-compose ps                  # View service status
docker-compose logs -f backend     # View backend logs (real-time)
docker-compose restart backend     # Restart backend only
docker-compose up -d --build       # Rebuild & restart all
docker-compose down                # Stop all services
```

**Update to latest version:**
```bash
git pull && docker-compose up -d --build
```

**Backup & Restore database:**
```bash
docker exec quantdinger-db pg_dump -U quantdinger quantdinger > backup.sql
cat backup.sql | docker exec -i quantdinger-db psql -U quantdinger quantdinger
```

**Custom port** — create `.env` in project root:
```ini
FRONTEND_PORT=3000          # Default: 8888
BACKEND_PORT=127.0.0.1:5001 # Default: 5000
```

</details>

---

## 🎯 Why QuantDinger?

> **Vibe Coding for Trading** — Describe your trading idea in plain English (or any language). AI writes the Python strategy, backtests it, and deploys it to live markets. No manual coding. No SaaS lock-in. Everything runs on your own server.

| | |
|---|---|
| 🎵 **Vibe Coding** | Describe ideas in natural language → AI generates production-ready Python strategies |
| 🔒 **100% Self-Hosted** | API keys & strategies never leave your server — privacy by design |
| 🤖 **7 AI Agents** | Multi-agent research team: parallel analysis → debate → trade decision |
| 🐍 **Python-Native** | Full ecosystem (Pandas, NumPy, TA-Lib, scikit-learn) — no proprietary language limits |
| 📊 **Professional Charts** | K-line charts with Python indicators, real-time visualization |
| 🌍 **Crypto + Stocks + Forex** | 10+ exchanges, IBKR, MT5 — all in one platform |
| 📊 **Prediction Markets** | On-demand AI analysis for Polymarket — probability divergence, opportunity scoring |
| 💰 **Monetization-Ready** | Membership, credits, USDT on-chain payment — built-in |
| ⚡ **2-Minute Deploy** | `docker-compose up -d` — production-ready, zero build |

---

## 📸 Visual Tour &nbsp;|&nbsp; [📺 Watch Video Demo](https://youtu.be/HPTVpqL7knM)

<table align="center" width="100%">
  <tr>
    <td colspan="2" align="center">
      <a href="https://youtu.be/HPTVpqL7knM"><img src="docs/screenshots/video_demo.png" alt="Video Demo" width="80%" style="border-radius: 8px;"></a>
    </td>
  </tr>
  <tr>
    <td colspan="2" align="center">
      <img src="docs/screenshots/dashboard.png" alt="Dashboard" width="90%" style="border-radius: 8px;">
      <br/><sub>📊 Professional Quant Dashboard</sub>
    </td>
  </tr>
  <tr>
    <td width="50%" align="center"><img src="docs/screenshots/ai_analysis1.png" alt="AI Analysis" style="border-radius: 6px;"><br/><sub>🤖 AI Deep Research</sub></td>
    <td width="50%" align="center"><img src="docs/screenshots/trading_assistant.png" alt="Trading Assistant" style="border-radius: 6px;"><br/><sub>💬 Smart Trading Assistant</sub></td>
  </tr>
  <tr>
    <td align="center"><img src="docs/screenshots/indicator_analysis.png" alt="Indicator Analysis" style="border-radius: 6px;"><br/><sub>📈 Indicator Analysis</sub></td>
    <td align="center"><img src="docs/screenshots/indicator_creat_python_code.png" alt="Code Generation" style="border-radius: 6px;"><br/><sub>🐍 AI Strategy Coding</sub></td>
  </tr>
  <tr>
    <td colspan="2" align="center"><img src="docs/screenshots/portfolio.jpg" alt="Portfolio Monitor" style="border-radius: 6px; max-width: 80%;"><br/><sub>📊 Portfolio Monitor</sub></td>
  </tr>
</table>

---

## ✨ Key Features

### 🎵 Vibe Coding Strategy Workbench

> **No coding required.** Tell AI what you want in natural language — it generates production-ready Python strategies. Or write your own with the full Python ecosystem (Pandas, NumPy, TA-Lib, scikit-learn). Visualize everything on professional K-line charts.

```
💬 "I want a MACD crossover strategy with RSI filter on BTC 15min"
    ↓ AI generates Python code
    ↓ 📈 Visualize on K-line charts
    ↓ 🔄 Backtest with rich metrics
    ↓ 🤖 AI suggests optimizations
    ↓ 🚀 One-click deploy to live trading
```

### 🤖 7-Agent AI Analysis Engine

> Not just one AI call. QuantDinger deploys **7 specialized agents** that collaborate like a research team — analyze, debate, and reach consensus:

```
Phase 1 (Parallel):  📊 Technical · 📑 Fundamental · 📰 News · 💭 Sentiment · ⚠️ Risk
Phase 2 (Debate):    🐂 Bull vs 🐻 Bear — structured argumentation
Phase 3 (Decision):  🎯 TraderAgent → BUY / SELL / HOLD (with confidence %)
```

- **🎵 Natural Language Analysis** — Ask "Analyze BTC trend for next week" → 7 agents deliver a full report
- **📡 AI Trading Radar** — Auto-scans Crypto/Stocks/Forex hourly, surfaces opportunities
- **⚡ Quick Trade Panel** — See a signal? One-click to execute. No page switching.
- **🧠 Memory-Augmented** — Agents learn from past analyses (local RAG, not cloud)
- **🔌 5+ LLM Providers**: OpenRouter (100+ models), OpenAI, Gemini, DeepSeek, Grok
- **📊 Polymarket Prediction Markets** — On-demand AI analysis for prediction markets. Input a market link or title → AI analyzes probability divergence, opportunity score, and trading recommendations. Full history tracking and billing integration.

### 📈 Full Trading Lifecycle

| Step | What Happens |
|------|-------------|
| **1. 💬 Describe** | Tell AI your trading idea in natural language — or write Python directly |
| **2. 🤖 Generate** | AI creates the indicator & strategy code for you |
| **3. 📊 Visualize** | See signals on professional K-line charts instantly |
| **4. 🔄 Backtest** | Rich metrics + **AI analyzes results & suggests improvements** |
| **5. 🚀 Execute** | Live trade on 10+ crypto exchanges, IBKR (stocks), MT5 (forex) |
| **6. 📡 Monitor** | Portfolio tracker, alerts via Telegram/Discord/Email/SMS/Webhook |

### 📊 Polymarket Prediction Market Analysis

> **On-demand AI analysis for prediction markets.** Input a Polymarket link or market title → AI analyzes probability divergence, opportunity score, and provides trading recommendations.

**Features:**
- **🔍 Smart Search** — Supports market links, slugs, or natural language titles
- **🤖 AI Probability Prediction** — Compares AI-predicted probability vs market probability
- **📈 Opportunity Scoring** — Calculates opportunity score based on divergence and confidence
- **💡 Trading Recommendations** — YES/NO/HOLD with detailed reasoning and key factors
- **📚 History Tracking** — View all your past analyses with full details in a dedicated history tab
- **💰 Billing Integration** — Configurable credit consumption per analysis (set via `BILLING_COST_POLYMARKET_DEEP_ANALYSIS`)
- **🌍 Multi-Language** — AI responses match your frontend language (English/Chinese)
- **📊 Admin Statistics** — All analyses tracked in user management dashboard

**Usage:**
```
1. Navigate to AI Asset Analysis → Prediction Markets tab
2. Input Polymarket link or market title
3. AI analyzes and returns:
   - Market probability vs AI-predicted probability
   - Divergence analysis
   - Opportunity score (0-100)
   - Trading recommendation (YES/NO/HOLD)
   - Detailed reasoning and key factors
4. View analysis history anytime
```

### 💰 Built-in Monetization

> Most open-source projects need months of custom billing work. QuantDinger ships with a **complete monetization system** out of the box:

- **💳 Membership Plans** — Monthly / Yearly / Lifetime tiers with configurable pricing & credits
- **₿ USDT On-Chain Payment** — TRC20 scan-to-pay, HD Wallet (xpub) per-order addresses, auto-reconciliation via TronGrid
- **🏪 Indicator Marketplace** — Users publish & sell Python indicators, you take commission
- **⚙️ Admin Dashboard** — Order management, AI usage stats, user analytics

### 🔐 Enterprise-Grade Security

- **Multi-User** — PostgreSQL-backed accounts with role-based permissions
- **OAuth** — Google & GitHub one-click login
- **Protection** — Cloudflare Turnstile, IP/account rate limiting, email verification
- **Demo Mode** — Read-only mode for public showcases

<details>
<summary><b>🧠 AI Agent Architecture Diagram (Click to expand)</b></summary>

```mermaid
flowchart TB
    subgraph Entry["🌐 API Entry"]
        A["📡 POST /api/analysis/multi"]
        A2["🔄 POST /api/analysis/reflect"]
    end
    subgraph Service["⚙️ Service Orchestration"]
        B[AnalysisService]
        C[AgentCoordinator]
        D["📊 Build Context<br/>price · kline · news · indicators"]
    end
    subgraph Agents["🤖 7-Agent Workflow"]
        subgraph P1["📈 Phase 1 · Parallel Analysis"]
            E1["🔍 MarketAnalyst"]
            E2["📑 FundamentalAnalyst"]
            E3["📰 NewsAnalyst"]
            E4["💭 SentimentAnalyst"]
            E5["⚠️ RiskAnalyst"]
        end
        subgraph P2["🎯 Phase 2 · Bull vs Bear Debate"]
            F1["🐂 BullResearcher"]
            F2["🐻 BearResearcher"]
        end
        subgraph P3["💹 Phase 3 · Final Decision"]
            G["🎰 TraderAgent → BUY / SELL / HOLD"]
        end
    end
    subgraph Memory["🧠 Local Memory Store"]
        M1[("Agent Memories (PostgreSQL)")]
    end
    subgraph Reflect["🔄 Reflection Loop"]
        R[ReflectionService]
        W["⏰ ReflectionWorker → verify + learn"]
    end
    A --> B --> C --> D
    D --> P1 --> P2 --> P3
    Agents <-.->|"RAG retrieval"| M1
    C --> R
    W -.->|"update memories"| M1
```

</details>

---

## 🔌 Supported Exchanges & Brokers

### Cryptocurrency (Direct API Trading)

| Exchange | Markets |
|:--------:|:---------|
| Binance | Spot, Futures, Margin |
| OKX | Spot, Perpetual, Options |
| Bitget | Spot, Futures, Copy Trading |
| Bybit | Spot, Linear Futures |
| Coinbase | Spot |
| Kraken | Spot, Futures |
| KuCoin | Spot, Futures |
| Gate.io | Spot, Futures |
| Bitfinex | Spot, Derivatives |

### Traditional Brokers & Markets

| Market | Broker/Source | Trading |
|--------|--------------|---------|
| **US Stocks** | Interactive Brokers (IBKR), Yahoo Finance, Finnhub | ✅ Via IBKR |
| **Forex** | MetaTrader 5 (MT5), OANDA | ✅ Via MT5 |
| **Futures** | Exchange APIs | ⚡ Data + Notify |

---

## 🏗️ Architecture & Configuration

### Tech Stack

| Layer | Technology |
|-------|-----------|
| **AI Engine** | 7-Agent Multi-Agent System · RAG Memory · 5+ LLM Providers · Vibe Coding (NL→Python) |
| **Backend** | Python 3.10+ · Flask · PostgreSQL 16 · Redis (optional) |
| **Frontend** | Vue.js · Ant Design · KlineCharts · ECharts |
| **Payment** | USDT TRC20 On-Chain · HD Wallet (BIP-32/44) · TronGrid API |
| **Mobile** | Vue 3 + Capacitor (Android / iOS) |
| **Deploy** | Docker Compose · Nginx · Zero-build one-click |

```text
┌─────────────────────────────────────┐
│         Docker Compose              │
│                                     │
│  ┌───────────────────────────────┐  │
│  │  frontend (Nginx)  → :8888   │  │
│  └──────────────┬────────────────┘  │
│                 │ /api/* proxy       │
│  ┌──────────────▼────────────────┐  │
│  │  backend (Flask)   → :5000   │  │
│  └──────────────┬────────────────┘  │
│  ┌──────────────▼────────────────┐  │
│  │  postgres (PG 16)  → :5432   │  │
│  └───────────────────────────────┘  │
│                                     │
│  External: LLM APIs · Exchanges ·   │
│  TronGrid · Data providers          │
└─────────────────────────────────────┘
```

### Repository Layout

```text
QuantDinger/
├── backend_api_python/          # 🐍 Backend (Open Source, Apache 2.0)
│   ├── app/routes/              #   API endpoints
│   ├── app/services/            #   Business logic (AI, trading, payment)
│   ├── migrations/init.sql      #   Database schema
│   ├── env.example              #   ⚙️ Config template → copy to .env
│   └── Dockerfile
├── frontend/                    # 🎨 Frontend (Pre-built)
│   ├── dist/                    #   Static files (HTML/JS/CSS)
│   ├── Dockerfile               #   Nginx image
│   └── nginx.conf               #   SPA routing + API proxy
├── docs/                        # 📚 Guides & tutorials
├── docker-compose.yml           # 🐳 One-click deployment
└── LICENSE                      # Apache 2.0
```

<details>
<summary><b>⚙️ Configuration Reference (.env)</b></summary>

Use `backend_api_python/env.example` as template:

| Category | Key Variables |
|----------|-----------|
| **Auth** | `SECRET_KEY`, `ADMIN_USER`, `ADMIN_PASSWORD` |
| **Database** | `DATABASE_URL` (PostgreSQL connection string) |
| **AI / LLM** | `LLM_PROVIDER`, `OPENROUTER_API_KEY`, `OPENAI_API_KEY` |
| **OAuth** | `GOOGLE_CLIENT_ID`, `GITHUB_CLIENT_ID` |
| **Security** | `TURNSTILE_SITE_KEY`, `ENABLE_REGISTRATION` |
| **Membership** | `MEMBERSHIP_MONTHLY_PRICE_USD`, `MEMBERSHIP_MONTHLY_CREDITS` |
| **USDT Payment** | `USDT_PAY_ENABLED`, `USDT_TRC20_XPUB`, `TRONGRID_API_KEY` |
| **Proxy** | `PROXY_PORT` or `PROXY_URL` |
| **Workers** | `ENABLE_PENDING_ORDER_WORKER`, `ENABLE_PORTFOLIO_MONITOR` |

</details>

<details>
<summary><b>🔌 API Endpoints</b></summary>

| Endpoint | Description |
|----------|-------------|
| `GET /api/health` | Health check |
| `POST /api/user/login` | User authentication |
| `GET /api/user/info` | Current user info |
| `GET /api/billing/plans` | Membership plans |
| `POST /api/billing/usdt/create-order` | Create USDT payment order |

For the full route list, see `backend_api_python/app/routes/`.

</details>

---

## 📚 Documentation Index

All detailed guides are in the [`docs/`](docs/) folder:

### Getting Started

| Document | Description |
|----------|-------------|
| [Changelog](docs/CHANGELOG.md) | Version history & migration notes |
| [Multi-User Setup](docs/multi-user-setup.md) | PostgreSQL multi-user deployment |

### Strategy Development

| Guide | 🇺🇸 EN | 🇨🇳 CN | 🇹🇼 TW | 🇯🇵 JA | 🇰🇷 KO |
|-------|--------|--------|--------|--------|--------|
| **Strategy Dev** | [EN](docs/STRATEGY_DEV_GUIDE.md) | [CN](docs/STRATEGY_DEV_GUIDE_CN.md) | [TW](docs/STRATEGY_DEV_GUIDE_TW.md) | [JA](docs/STRATEGY_DEV_GUIDE_JA.md) | [KO](docs/STRATEGY_DEV_GUIDE_KO.md) |
| **Cross-Sectional** | [EN](docs/CROSS_SECTIONAL_STRATEGY_GUIDE_EN.md) | [CN](docs/CROSS_SECTIONAL_STRATEGY_GUIDE_CN.md) | | | |
| **Code Examples** | [examples/](docs/examples/) | | | | |

### Broker & Integration

| Guide | English | 中文 |
|-------|---------|------|
| **IBKR (US Stocks)** | [Guide](docs/IBKR_TRADING_GUIDE_EN.md) | — |
| **MT5 (Forex)** | [Guide](docs/MT5_TRADING_GUIDE_EN.md) | [指南](docs/MT5_TRADING_GUIDE_CN.md) |
| **OAuth (Google/GitHub)** | [Guide](docs/OAUTH_CONFIG_EN.md) | [指南](docs/OAUTH_CONFIG_CN.md) |

### Notifications

| Channel | English | 中文 |
|---------|---------|------|
| **Telegram** | [Setup](docs/NOTIFICATION_TELEGRAM_CONFIG_EN.md) | [配置](docs/NOTIFICATION_TELEGRAM_CONFIG_CH.md) |
| **Email (SMTP)** | [Setup](docs/NOTIFICATION_EMAIL_CONFIG_EN.md) | [配置](docs/NOTIFICATION_EMAIL_CONFIG_CH.md) |
| **SMS (Twilio)** | [Setup](docs/NOTIFICATION_SMS_CONFIG_EN.md) | [配置](docs/NOTIFICATION_SMS_CONFIG_CH.md) |

---

## 💼 License & Commercial

### Open Source License

Backend source code is licensed under **Apache License 2.0**. See `LICENSE`.

The frontend UI is provided as **pre-built files**. Trademark rights (name/logo/branding) are governed separately — see `TRADEMARKS.md`.

### 🎓 Free Source Code for Non-Profit & Education

If you are a **university**, **research institution**, **non-profit**, **community group**, or **educational program**, you can apply for **free authorization and full frontend source code**:

- 🏫 Universities & academic research
- 🌍 Open-source communities & developer groups
- 🤝 Non-profit & public welfare organizations
- 📚 Educational programs & student hackathons

### 💼 Commercial License

For **commercial use**, purchase a license to get:

- **Full frontend source code** + future updates
- **Branding authorization** — modify name/logo/copyright as agreed
- **Operations support** — deployment, upgrades, incident response
- **Consulting** — architecture review, performance tuning

### 📬 Contact

| Channel | Link |
|---------|------|
| **Telegram** | [t.me/worldinbroker](https://t.me/worldinbroker) |
| **Email** | [brokermr810@gmail.com](mailto:brokermr810@gmail.com) |

---

## 🤝 Community & Support

<p>
  <a href="https://t.me/quantdinger"><img src="https://img.shields.io/badge/Telegram-Group-26A5E4?style=for-the-badge&logo=telegram" alt="Telegram"></a>
  <a href="https://discord.gg/tyx5B6TChr"><img src="https://img.shields.io/badge/Discord-Server-5865F2?style=for-the-badge&logo=discord" alt="Discord"></a>
  <a href="https://youtube.com/@quantdinger"><img src="https://img.shields.io/badge/YouTube-Channel-FF0000?style=for-the-badge&logo=youtube" alt="YouTube"></a>
</p>

- [Contributing Guide](CONTRIBUTING.md) · [Contributors](CONTRIBUTORS.md)
- [Report Bugs / Request Features](https://github.com/brokermr810/QuantDinger/issues)
- Email: [brokermr810@gmail.com](mailto:brokermr810@gmail.com)

---

### 💝 Support the Project

**Crypto Donations (ERC-20 / BEP-20 / Polygon / Arbitrum)**

```
0x96fa4962181bea077f8c7240efe46afbe73641a7
```

<p>
  <img src="https://img.shields.io/badge/USDT-Accepted-26A17B?style=for-the-badge&logo=tether&logoColor=white" alt="USDT">
  <img src="https://img.shields.io/badge/ETH-Accepted-3C3C3D?style=for-the-badge&logo=ethereum&logoColor=white" alt="ETH">
</p>

---

### 🎓 Supporting Partners

<div align="center">
<table>
  <tr>
    <td align="center" width="50%">
      <a href="https://beinvolved.indiana.edu/organization/quantfiniu" target="_blank">
        <img src="docs/screenshots/qfs_logo.png" alt="Indiana University QFS" width="280" style="border-radius: 8px;">
      </a>
      <br/><br/>
      <strong>Quantitative Finance Society (QFS)</strong><br/>
      <small>Indiana University Bloomington</small>
    </td>
  </tr>
</table>
</div>

> 💡 **Want to become a partner?** Contact [brokermr810@gmail.com](mailto:brokermr810@gmail.com) or [Telegram](https://t.me/worldinbroker).

---

### Acknowledgements

Built with ❤️ on the shoulders of: [Flask](https://flask.palletsprojects.com/) · [Pandas](https://pandas.pydata.org/) · [CCXT](https://github.com/ccxt/ccxt) · [yfinance](https://github.com/ranaroussi/yfinance) · [Vue.js](https://vuejs.org/) · [Ant Design Vue](https://antdv.com/) · [KlineCharts](https://github.com/klinecharts/KLineChart) · [ECharts](https://echarts.apache.org/) · [Capacitor](https://capacitorjs.com/) · [bip-utils](https://github.com/ebellocchia/bip_utils)

<p align="center"><sub>If QuantDinger helps you, consider ⭐ starring the repo — it means a lot!</sub></p>
