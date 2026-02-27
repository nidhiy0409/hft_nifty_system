hft_nifty_system/
├── config/
├── data/
│   ├── historical_ticks/
│   └── sql_schemas/
├── docs/
├── research/
│   ├── notebooks/
│   └── backtester/
├── scripts/
├── src/
│   ├── core/
│   │   ├── ems/
│   │   ├── oms/
│   │   └── fix_engine/
│   ├── feed/
│   │   ├── mkt_data_handler/
│   │   └── order_book/
│   ├── risk/
│   │   └── pre_trade_checks/
│   ├── strategies/
│   │   ├── base/
│   │   └── active/
│   └── utils/
│       ├── logger/
│       └── metrics/
├── tests/
│   ├── integration/
│   └── unit/
├── .env.example
├── .gitignore
├── pom.xml
├── requirements.txt
└── README.md


Core Architecture Breakdown
config/: Holds environment variables, API keys, and strategy parameters (JSON/YAML).

data/: Stores local historical tick data and database schemas for time-series storage.

research/: The quantitative workspace for data exploration, alpha discovery, and historical backtesting.

src/core/: The execution heart of the system. Contains the Execution Management System (EMS), Order Management System (OMS), and FIX protocol handlers for low-latency broker communication.

src/feed/: Handles the ingestion of live UDP/TCP market data and reconstructs the limit order book (LOB) in real-time.

src/risk/: Hardcoded pre-trade risk limits (max position size, daily loss limits) to prevent rogue algorithmic behavior.

src/strategies/: Where the actual trading logic resides, inheriting from a base strategy class.





FIX Engine
A FIX (Financial Information eXchange) Engine is a specialized piece of software that implements the FIX protocol.

Its Use:
It provides a standardized, high-speed, and reliable method to communicate electronic trading messages between your HFT system and the exchange (like the NSE) or a broker. Instead of dealing with proprietary exchange APIs, the FIX engine formats your buy/sell orders, order cancellations, and execution reports into universally understood key-value pairs (e.g., 35=D for a New Order Single, 54=1 for Buy). It also handles the continuous network session, message sequence numbers, and heartbeat monitoring to ensure the connection remains active and no orders are lost.