# HFT NIFTY Trading System

A high-frequency trading (HFT) and quantitative execution system built in Python, specifically designed for trading NIFTY 50 equities and F&O on the National Stock Exchange (NSE).

## Architecture

The system is built with a modular architecture to ensure low latency and separation of concerns:

* **Market Data Handler (`src/feed/mkt_data_handler`)**: Listens to raw exchange feeds via TCP/UDP, decodes byte streams using `struct`, and publishes normalized market messages.
* **Order Book (`src/feed/order_book`)**: Reconstructs and maintains the Limit Order Book (LOB) in real-time, tracking bids, asks, and order modifications/cancellations.
* **Order Management System (`src/core/oms`)**: Manages the lifecycle of active orders, tracks filled quantities, and processes execution reports.
* **Execution Management System (`src/core/ems`)**: Acts as the bridge between the OMS and the exchange, translating internal order representations into protocol-specific messages.
* **FIX Engine (`src/core/fix_engine`)**: A custom implementation of the FIX 4.4 protocol for high-speed, reliable order routing and session management with the broker/exchange.

## Directory Structure

```text
hft_nifty_system/
├── config/                  # Configuration files and API keys
├── data/
│   ├── historical_ticks/    # Local tick data storage for backtesting
│   └── sql_schemas/         # Database schemas
├── docs/                    # Project documentation
├── research/
│   ├── notebooks/           # Jupyter notebooks for alpha discovery
│   └── backtester/          # Historical backtesting engine
├── scripts/                 # Utility and deployment scripts
├── src/
│   ├── core/                # OMS, EMS, and FIX Engine
│   ├── feed/                # Market data ingestion and LOB
│   ├── risk/                # Pre-trade risk limits and compliance
│   ├── strategies/          # Trading logic (Base and Active)
│   └── utils/               # Logging and performance metrics
└── tests/                   # Unit and integration tests