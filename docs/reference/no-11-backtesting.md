## 1. No. 11 — Backtesting

**Backtesting** means running a fixed strategy on historical market data to estimate how it would have performed in the past.

It answers:

* How many trading opportunities occurred?
* What was the win rate?
* Was the strategy profitable after spread, commission and slippage?
* What was the maximum drawdown?
* Did it work across different years, symbols and market conditions?
* Are the rules genuinely useful, or were they overfitted to one period?

Backtesting does **not** prove that a strategy will be profitable in the future. It is an evidence-building stage.

---

# Backtesting process

## Step 1: Freeze the strategy rules

Before testing, create a versioned strategy specification.

```yaml
strategy:
  id: london_smc_reversal
  version: 1.0.0
  status: research

markets:
  symbols:
    - EURUSD
    - GBPUSD
    - XAUUSD

timeframes:
  bias: H1
  execution: M5

session:
  timezone: Europe/London
  start: "07:00"
  end: "11:00"

bias:
  bullish:
    require:
      - h1_bullish_bos
      - price_in_h1_discount
  bearish:
    require:
      - h1_bearish_bos
      - price_in_h1_premium

entry:
  long:
    require:
      - price_inside_bullish_poi
      - sell_side_liquidity_sweep
      - m5_bullish_choch
      - bullish_displacement
  short:
    require:
      - price_inside_bearish_poi
      - buy_side_liquidity_sweep
      - m5_bearish_choch
      - bearish_displacement

stop_loss:
  method: swept_liquidity_extreme
  atr_buffer: 0.15

take_profit:
  method: next_external_liquidity
  minimum_rr: 2.0

risk:
  risk_per_trade_pct: 0.5
  daily_loss_limit_pct: 2.0
  maximum_open_positions: 1

execution:
  entry_timing: next_bar_open
  spread_model: historical_or_broker_average
  slippage_points: 3
  commission_per_lot: 7.0
```

After testing starts, do not silently change these rules. Any change creates a new version, such as `1.1.0`.

---

## Step 2: Prepare historical data

You need historical candles or ticks containing:

```text
timestamp
open
high
low
close
volume
spread
symbol
timeframe
```

For higher-quality execution simulation, also include:

```text
bid
ask
tick volume
real spread
broker timezone
commission
swap
```

### Data quality checks

The data pipeline should detect:

* Missing candles
* Duplicate timestamps
* Incorrect timezone
* Weekend data
* Abnormal price jumps
* Incorrect decimal precision
* Symbol changes
* Daylight-saving-time errors

For your project, M1 data can be stored as the base timeframe, and H1, M15 and M5 candles can be generated from it.

---

## Step 3: Generate features

The feature engine converts raw candles into information used by the strategy.

For an SMC strategy, features may include:

```text
swing highs and swing lows
higher highs and lower lows
BOS
CHOCH
order blocks
fair-value gaps
liquidity sweeps
premium and discount
session high and low
ATR
spread
volatility regime
```

Example:

```python
features = {
    "h1_bias": "bullish",
    "inside_bullish_poi": True,
    "sell_side_sweep": True,
    "m5_bullish_choch": True,
    "bullish_displacement": True,
    "spread_points": 14,
}
```

---

## Step 4: Generate signals

The signal engine evaluates the strategy without placing an order.

```python
if (
    features["h1_bias"] == "bullish"
    and features["inside_bullish_poi"]
    and features["sell_side_sweep"]
    and features["m5_bullish_choch"]
    and features["bullish_displacement"]
):
    signal = "BUY"
else:
    signal = "NO_TRADE"
```

A professional signal should include more than `BUY` or `SELL`.

```json
{
  "signal_id": "SIG-XAUUSD-20260719-001",
  "strategy_id": "london_smc_reversal",
  "strategy_version": "1.0.0",
  "symbol": "XAUUSD",
  "direction": "BUY",
  "signal_time": "2026-07-19T08:35:00Z",
  "entry_reference": 2411.40,
  "stop_reference": 2407.90,
  "target_reference": 2418.40,
  "risk_reward": 2.0,
  "reason_codes": [
    "H1_BULLISH_BOS",
    "H1_DISCOUNT_POI",
    "SELL_SIDE_SWEEP",
    "M5_BULLISH_CHOCH"
  ]
}
```

---

## Step 5: Simulate execution realistically

A weak backtest enters at an impossible price.

For example:

```text
Signal detected using the complete M5 candle.
Entry assumed at the same candle's lowest price.
```

That creates look-ahead bias because the strategy could not know the completed candle and enter earlier inside it.

A more realistic rule is:

```text
Signal confirmed at M5 candle close.
Entry occurs at the next candle's open or next available ask/bid price.
```

The simulator should include:

* Bid/ask spread
* Commission
* Slippage
* Minimum stop distance
* Lot-size rules
* Partial fills where relevant
* Trading-session limits
* Position and order conflicts
* Broker symbol specifications

---

## Step 6: Calculate trade results

Example long trade:

```text
Entry: 2411.40
Stop loss: 2407.90
Target: 2418.40

Risk distance:
2411.40 - 2407.90 = 3.50

Reward distance:
2418.40 - 2411.40 = 7.00

Reward-to-risk:
7.00 ÷ 3.50 = 2R
```

Outcomes may be recorded as:

```text
Stop hit:        -1R
Target hit:      +2R
Break-even:       0R
Partial result:  +0.7R
Timeout exit:    -0.2R
```

Using R-multiples makes comparison easier across symbols.

---

## Step 7: Evaluate performance

Important metrics include:

| Metric             | Meaning                            |
| ------------------ | ---------------------------------- |
| Net profit         | Total profit after costs           |
| Win rate           | Percentage of winning trades       |
| Profit Factor      | Gross profit divided by gross loss |
| Expectancy         | Expected return per trade          |
| Maximum drawdown   | Largest account decline            |
| Sharpe ratio       | Return relative to variability     |
| Average R          | Average result per trade           |
| Trade count        | Sample size                        |
| Exposure           | Time spent in positions            |
| Consecutive losses | Losing-streak risk                 |

Example:

```yaml
results:
  trades: 428
  wins: 201
  losses: 227
  win_rate: 46.96
  average_win_r: 1.82
  average_loss_r: -0.93
  expectancy_r: 0.36
  profit_factor: 1.42
  max_drawdown_pct: 8.7
  sharpe_ratio: 1.31
```

Expectancy can be calculated as:

```text
Expectancy =
(Win Rate × Average Win)
-
(Loss Rate × Average Loss)
```

Example:

```text
Win rate: 47%
Average win: 1.82R
Loss rate: 53%
Average loss: 0.93R

Expectancy =
(0.47 × 1.82) - (0.53 × 0.93)
= 0.8554 - 0.4929
= +0.3625R per trade
```

---

## Step 8: Separate training and testing periods

Do not repeatedly optimize on the complete dataset.

Example:

```text
2020–2023: strategy development/in-sample
2024: validation
2025: out-of-sample
2026: forward/demo test
```

A stronger process uses rolling walk-forward testing:

```text
Train: Jan 2020–Dec 2022
Test:  Jan 2023–Jun 2023

Train: Jul 2020–Jun 2023
Test:  Jul 2023–Dec 2023

Train: Jan 2021–Dec 2023
Test:  Jan 2024–Jun 2024
```

The strategy should survive several independent periods rather than one favourable period.

---

## Step 9: Test robustness

Professional validation may include:

* Out-of-sample testing
* Walk-forward testing
* Monte Carlo simulation
* Parameter sensitivity testing
* Cross-symbol testing
* Cross-session testing
* Different spread and slippage assumptions
* Market-regime testing
* Consecutive-loss simulations

Example parameter sensitivity:

```text
CHOCH swing length:
3, 4, 5, 6, 7

ATR stop buffer:
0.10, 0.15, 0.20, 0.25

Minimum RR:
1.5, 2.0, 2.5, 3.0
```

A strategy is stronger when neighbouring parameter values also perform acceptably.

A fragile result looks like:

```text
Swing length 4 → PF 0.91
Swing length 5 → PF 1.85
Swing length 6 → PF 0.88
```

This suggests the result may be overfitted.

---

# Example backtest output

```yaml
backtest_run:
  run_id: BT-2026-07-19-001
  strategy_id: london_smc_reversal
  strategy_version: 1.0.0

dataset:
  symbols: [EURUSD, GBPUSD, XAUUSD]
  start: 2021-01-01
  end: 2025-12-31
  base_timeframe: M1

execution_assumptions:
  signal_confirmation: candle_close
  entry: next_bar_open
  spread: historical
  slippage: enabled
  commission: enabled

performance:
  trades: 731
  profit_factor: 1.38
  expectancy_r: 0.21
  max_drawdown_pct: 11.4
  sharpe_ratio: 1.09

decision:
  status: RESEARCH_ONLY
  reason:
    - sharpe_below_required_threshold
    - drawdown_above_target
```

Even though this backtest is profitable, it should not automatically be promoted because it failed some qualification conditions.

---

# 2. No. 12 — Forward testing

**Forward testing** means running the strategy against new live market data without using future information.

It normally happens after backtesting.

There are two main forms:

### Paper or virtual forward testing

The system receives live prices and creates simulated orders internally. Nothing is sent to a broker.

### Broker demo forward testing

The system sends real orders to a broker demo account. This tests actual broker execution behaviour without risking real money.

For your project, the safer path is:

```text
Historical backtest
→ Replay test
→ Live shadow mode
→ Paper trading
→ MT5 demo trading
→ Limited live trading
```

---

## Why forward testing is necessary

Backtesting cannot fully reproduce:

* Real-time latency
* Broker disconnections
* Changing spreads
* Slippage
* Requotes
* Rejected orders
* Partial fills
* VPS failure
* MT5 terminal restart
* Duplicate signals
* Duplicate orders
* Stale prices
* Missing candles
* Real news volatility
* Broker-specific symbol properties

Forward testing validates both the **strategy** and the **execution system**.

---

# Forward-test modes

## Mode 1: Shadow mode

The strategy analyzes live data but places no order.

```text
Market data → signal → proposed order → logged only
```

Example:

```json
{
  "mode": "shadow",
  "decision": "BUY",
  "symbol": "XAUUSD",
  "entry": 2411.40,
  "stop": 2407.90,
  "target": 2418.40,
  "broker_order_sent": false
}
```

Use shadow mode to verify signal timing and rule correctness.

---

## Mode 2: Paper trading

The system simulates an account and fills.

```text
Live prices
→ real-time signal
→ simulated broker
→ virtual positions
→ virtual P&L
```

This tests the live event pipeline while keeping execution internal.

---

## Mode 3: MT5 demo trading

The complete execution pipeline connects to an MT5 demo account.

MetaTrader’s official Python integration supports communicating with an installed MT5 terminal, retrieving market and account information and performing trading-related integration. The connection is established through the terminal process, so your Windows VPS must keep the MT5 terminal running and authenticated. ([MQL5][1])

```text
Live data
→ strategy decision
→ risk validation
→ order intent
→ MT5 adapter
→ MT5 terminal
→ broker demo server
```

---

## Forward-test acceptance criteria

Example:

```yaml
forward_test:
  required_duration_days: 60
  minimum_closed_trades: 100

  strategy_metrics:
    minimum_profit_factor: 1.25
    minimum_expectancy_r: 0.10
    maximum_drawdown_pct: 10
    minimum_execution_match_rate_pct: 99

  operational_metrics:
    duplicate_orders: 0
    orphan_positions: 0
    unresolved_reconciliation_errors: 0
    maximum_stale_price_seconds: 5
    order_rejection_rate_pct_max: 1
    event_recording_completeness_pct: 100
```

Your existing stronger qualification rule can remain:

```text
Net Profit Factor > 1.25
Sharpe Ratio > 1.2
Walk-forward passed
Monte Carlo passed
Out-of-sample passed
Owner approval required
```

---

# 3. Complete automated trading architecture

A professional architecture should separate research, strategy decisions, risk control and broker execution.

```text
┌───────────────────────────────────────────────┐
│                SYSTEM 1: RESEARCH             │
│                                               │
│ Historical Data → Features → Signals          │
│ → Backtest → Validation → Approval            │
└────────────────────────┬──────────────────────┘
                         │
                  Signed strategy package
                         │
┌────────────────────────▼──────────────────────┐
│             SYSTEM 2: EXECUTION               │
│                                               │
│ Live Data → Feature Engine → Strategy Engine  │
│ → Risk Engine → Execution Pipeline            │
│ → Broker Adapter → MT5/Broker                 │
│                                               │
│ Reconciliation ← Broker Orders/Positions      │
│ Monitoring ← Events, Trades, Health           │
└───────────────────────────────────────────────┘
```

This matches your current direction: **System 1 approves strategies; System 2 executes only approved packages.**

---

# 4. System 1: Research and validation architecture

```text
Data Ingestion
      ↓
Data Validation
      ↓
Timeframe Builder
      ↓
Feature Engine
      ↓
Signal Generator
      ↓
Backtest Engine
      ↓
Cost and Execution Simulator
      ↓
Analytics Engine
      ↓
Walk-Forward / Monte Carlo / OOS
      ↓
Qualification Gate
      ↓
Signed Strategy Package
```

## Recommended modules

```text
system1/
├── data/
│   ├── ingestion.py
│   ├── quality_checker.py
│   ├── timeframe_builder.py
│   └── dataset_registry.py
│
├── features/
│   ├── market_structure.py
│   ├── liquidity.py
│   ├── order_blocks.py
│   ├── fair_value_gaps.py
│   └── sessions.py
│
├── strategy/
│   ├── schema.py
│   ├── rule_engine.py
│   ├── signal_generator.py
│   └── strategy_registry.py
│
├── backtest/
│   ├── event_engine.py
│   ├── execution_simulator.py
│   ├── portfolio.py
│   ├── cost_model.py
│   └── result_recorder.py
│
├── validation/
│   ├── out_of_sample.py
│   ├── walk_forward.py
│   ├── monte_carlo.py
│   ├── sensitivity.py
│   └── qualification_gate.py
│
└── packaging/
    ├── manifest.py
    ├── signer.py
    └── publisher.py
```

---

# 5. System 2: Automated execution architecture

```text
Market Data Adapter
        ↓
Candle/Feature Builder
        ↓
Strategy Runtime
        ↓
Signal Validator
        ↓
Risk Engine
        ↓
Order Intent
        ↓
Canonical Execution Pipeline
        ↓
MT5 Adapter
        ↓
Broker
        ↓
Order/Position Reconciliation
        ↓
Trade Journal + Monitoring
```

## Recommended modules

```text
system2/
├── runtime/
│   ├── runtime_authority.py
│   ├── scheduler.py
│   ├── state_manager.py
│   └── recovery_manager.py
│
├── market_data/
│   ├── mt5_market_data.py
│   ├── candle_builder.py
│   └── freshness_validator.py
│
├── strategy_runtime/
│   ├── package_loader.py
│   ├── rule_evaluator.py
│   ├── feature_adapter.py
│   └── signal_service.py
│
├── risk/
│   ├── position_sizer.py
│   ├── exposure_guard.py
│   ├── daily_loss_guard.py
│   ├── drawdown_guard.py
│   └── kill_switch.py
│
├── execution/
│   ├── canonical_pipeline.py
│   ├── order_validator.py
│   ├── idempotency.py
│   ├── mt5_adapter.py
│   └── simulated_adapter.py
│
├── reconciliation/
│   ├── order_reconciler.py
│   ├── position_reconciler.py
│   └── startup_recovery.py
│
├── persistence/
│   ├── event_repository.py
│   ├── trade_repository.py
│   └── checkpoint_repository.py
│
└── monitoring/
    ├── health_service.py
    ├── metrics.py
    ├── alerts.py
    └── dashboard_api.py
```

---

# 6. Detailed live automation flow

## Step 1: Receive market data

```python
tick = broker.get_tick("XAUUSD")
```

The data validator checks:

```text
Is the price recent?
Is bid lower than ask?
Is spread acceptable?
Is the symbol tradable?
Is the market session active?
```

---

## Step 2: Build candles and features

```python
features = feature_engine.calculate(
    symbol="XAUUSD",
    bias_timeframe="H1",
    execution_timeframe="M5",
)
```

Possible output:

```json
{
  "h1_bias": "bullish",
  "inside_h1_poi": true,
  "sell_side_swept": true,
  "m5_choch": "bullish",
  "displacement": true
}
```

---

## Step 3: Evaluate strategy

```python
decision = strategy_engine.evaluate(features)
```

Output:

```json
{
  "action": "BUY",
  "confidence": 1.0,
  "entry_model": "market_next_tick",
  "stop_loss": 2407.90,
  "take_profit": 2418.40
}
```

For a rule-based strategy, `confidence` should not replace the actual rule result. It should usually be:

```text
All mandatory rules passed → valid
One mandatory rule failed → no trade
```

---

## Step 4: Risk validation

The risk engine checks:

```text
Is trading enabled?
Is demo-only mode active?
Has the daily loss limit been reached?
Is the account drawdown acceptable?
Is another XAUUSD position open?
Is risk below 0.5%?
Is the stop distance valid?
Is the calculated lot size broker-valid?
Is there enough free margin?
```

Example lot-size formula:

```text
Risk amount = Account balance × Risk percentage

Risk amount:
$10,000 × 0.5% = $50

Lot size =
Risk amount ÷ monetary value of stop distance
```

The calculation must use the broker’s actual contract size, tick size, tick value, volume minimum and volume step.

---

## Step 5: Create an order intent

Do not send a raw order directly from the strategy engine.

```json
{
  "intent_id": "INT-20260719-XAUUSD-001",
  "strategy_id": "london_smc_reversal",
  "strategy_version": "1.0.0",
  "account_mode": "demo",
  "symbol": "XAUUSD",
  "side": "BUY",
  "volume": 0.14,
  "stop_loss": 2407.90,
  "take_profit": 2418.40,
  "maximum_slippage_points": 10
}
```

The intent is audited before execution.

---

## Step 6: Execute through one canonical pipeline

```text
Strategy
   ↓
Risk approval
   ↓
Order validation
   ↓
Idempotency check
   ↓
Broker adapter
```

Every strategy must use the same pipeline.

Never allow:

```text
Strategy A → canonical pipeline
Strategy B → direct MT5 call
Strategy C → separate custom executor
```

That creates inconsistent risk control and duplicate execution paths.

---

## Step 7: Broker adapter

The adapter translates your internal order format into an MT5 request.

```python
class BrokerAdapter:
    def get_symbol_specification(self, symbol): ...
    def get_account_state(self): ...
    def place_order(self, intent): ...
    def cancel_order(self, broker_order_id): ...
    def close_position(self, position_id): ...
    def get_open_positions(self): ...
```

Possible implementations:

```text
SimulatedBrokerAdapter
MT5TerminalAdapter
MetaApiAdapter
OandaAdapter
BybitAdapter
```

The strategy code should not know which broker is being used.

---

## Step 8: Reconcile broker truth

After submitting the order, never assume it succeeded.

```text
Requested order
    ↓
Broker response
    ↓
Query broker orders
    ↓
Query broker positions
    ↓
Compare internal state with broker state
```

Possible outcomes:

```text
Order accepted and position opened
Order rejected
Order accepted but no fill
Partial fill
Position opened with different volume
Connection lost after submission
Duplicate submission attempted
```

The broker is the final authority for actual positions.

---

## Step 9: Manage the trade

The trade-management engine can implement:

```text
Fixed TP and SL
Break-even after +1R
Partial close at +1R
Trailing stop
Time-based exit
Session-close exit
Emergency close
```

These rules must be defined in the strategy package, not invented dynamically.

Example:

```yaml
trade_management:
  break_even:
    enabled: true
    activation_r: 1.0
    new_stop_offset_r: 0.05

  partial_close:
    enabled: true
    activation_r: 1.5
    close_percentage: 50

  final_target:
    target_r: 3.0

  timeout:
    maximum_bars: 36
```

---

## Step 10: Record every event

Use append-only events such as:

```text
SIGNAL_GENERATED
SIGNAL_REJECTED
RISK_APPROVED
RISK_REJECTED
ORDER_INTENT_CREATED
ORDER_SUBMITTED
ORDER_ACCEPTED
ORDER_REJECTED
POSITION_OPENED
STOP_MOVED
POSITION_PARTIALLY_CLOSED
POSITION_CLOSED
RECONCILIATION_MISMATCH
KILL_SWITCH_ACTIVATED
```

PostgreSQL is suitable for authoritative operational records and supports transactional updates with explicit commit and rollback behaviour. ([PostgreSQL][2])

---

# 7. Recommended technology stack

## Core language

### Python

Use Python for:

* Data processing
* Feature calculation
* Strategy evaluation
* Backtesting
* Risk management
* Broker integration
* APIs
* Analytics
* AI-assisted analysis

Useful packages:

```text
pandas or Polars
NumPy
Pydantic
SQLAlchemy
Alembic
pytest
scikit-learn, where justified
```

---

## MT5 execution

### Option A: Python connected to MT5 terminal

Best for your current Windows VPS setup.

```text
Python service
→ MetaTrader5 Python package
→ locally running MT5 terminal
→ VT Markets/Vantage broker
```

The official integration communicates directly with the MetaTrader terminal and provides functions for market data and terminal interaction. ([MQL5][1])

### Option B: MQL5 Expert Advisor

```text
Python strategy service
→ local REST/socket/file bridge
→ MQL5 EA
→ MT5
```

This can provide tighter terminal-level control but introduces bridge complexity.

### Recommended for your first implementation

Use:

```text
Python strategy and execution engine
+
MetaTrader5 Python terminal integration
+
Windows VPS
```

Later, add an EA bridge only when a measured technical need exists.

---

## Database

### PostgreSQL

Use it for:

```text
strategy registry
signals
order intents
broker orders
positions
closed trades
risk state
runtime checkpoints
audit events
incidents
approvals
```

### Parquet or DuckDB

Use for:

```text
historical candles
feature datasets
backtest outputs
large research queries
```

Recommended split:

```text
DuckDB/Parquet → System 1 research
PostgreSQL → System 2 operational authority
```

---

## API layer

### FastAPI

Use it for:

```text
dashboard APIs
health endpoints
manual kill switch
strategy status
trade history
readiness status
risk status
operational controls
```

FastAPI is designed for typed Python API development, and its official guidance supports structuring larger applications across multiple files and routers. ([FastAPI][3])

Do not use simple FastAPI background tasks as the main trading runtime. The trading engine should run as an independent supervised process.

---

## Deployment

### Windows VPS

Because MT5 normally runs as a Windows desktop terminal:

```text
Windows VPS
├── MT5 terminal
├── Python trading runtime
├── PostgreSQL or remote PostgreSQL connection
├── FastAPI dashboard API
├── monitoring agent
└── log collector
```

Run the Python components as Windows services using:

```text
NSSM
Windows Task Scheduler for limited maintenance jobs
PowerShell management scripts
```

### Docker

Docker is useful for:

```text
PostgreSQL
dashboard API
research services
monitoring
Redis
Grafana
```

However, the desktop MT5 terminal is usually easier to run directly on the Windows host.

Docker Compose can define application services, networks and persistent volumes in one YAML configuration and manage the application stack together. ([Docker Documentation][4])

Recommended hybrid deployment:

```text
Windows host:
  MT5 terminal
  MT5 Python execution worker

Docker:
  PostgreSQL
  FastAPI
  dashboard
  Prometheus
  Grafana
```

---

## Monitoring

Recommended tools:

```text
Prometheus → metrics
Grafana → dashboards
Structured JSON logs → event analysis
Telegram/email → critical alerts
Sentry → application exceptions
```

Monitor:

```text
runtime heartbeat
MT5 connection state
last market tick time
signal count
order count
order rejection rate
open positions
daily P&L
drawdown
database connectivity
reconciliation mismatches
CPU, RAM and disk
```

---

# 8. Suggested repository architecture

```text
trading-platform/
├── config/
│   ├── strategy.yaml
│   ├── risk.yaml
│   ├── symbols.yaml
│   └── environments/
│       ├── backtest.yaml
│       ├── shadow.yaml
│       ├── demo.yaml
│       └── live.yaml
│
├── domain/
│   ├── models.py
│   ├── enums.py
│   └── events.py
│
├── strategies/
│   └── london_smc/
│       ├── specification.yaml
│       ├── features.py
│       ├── rules.py
│       └── tests/
│
├── research/
│   ├── data_pipeline/
│   ├── features/
│   ├── backtest/
│   ├── validation/
│   └── reports/
│
├── runtime/
│   ├── market_data/
│   ├── strategy_engine/
│   ├── risk_engine/
│   ├── execution/
│   ├── reconciliation/
│   └── recovery/
│
├── brokers/
│   ├── base.py
│   ├── simulated.py
│   └── mt5_terminal.py
│
├── persistence/
│   ├── models/
│   ├── repositories/
│   └── migrations/
│
├── api/
│   ├── main.py
│   └── routers/
│
├── monitoring/
│   ├── metrics.py
│   ├── alerts.py
│   └── health.py
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── replay/
│   └── broker_demo/
│
└── scripts/
    ├── run_backtest.py
    ├── run_replay.py
    ├── run_shadow.py
    ├── run_demo.py
    └── check_readiness.py
```

---

# 9. One strategy, multiple operating modes

The most important design principle is that all environments should run the **same strategy rules**.

```text
Backtest mode:
HistoricalDataAdapter
+ SimulatedBrokerAdapter

Replay mode:
HistoricalDataAdapter played chronologically
+ SimulatedBrokerAdapter

Shadow mode:
MT5LiveDataAdapter
+ NoExecutionAdapter

Paper mode:
MT5LiveDataAdapter
+ SimulatedBrokerAdapter

Demo mode:
MT5LiveDataAdapter
+ MT5DemoBrokerAdapter

Live mode:
MT5LiveDataAdapter
+ MT5LiveBrokerAdapter
```

Only adapters and safety configuration should change.

```python
strategy = LondonSMCStrategy(specification)
risk_engine = RiskEngine(risk_config)

if mode == "backtest":
    market_data = HistoricalDataAdapter()
    broker = SimulatedBrokerAdapter()

elif mode == "shadow":
    market_data = MT5LiveDataAdapter()
    broker = NoExecutionAdapter()

elif mode == "demo":
    market_data = MT5LiveDataAdapter()
    broker = MT5BrokerAdapter(account_type="demo")

elif mode == "live":
    market_data = MT5LiveDataAdapter()
    broker = MT5BrokerAdapter(account_type="live")
```

This prevents the common mistake of having one strategy implementation for backtesting and another for live execution.

---

# 10. Automation state machine

Use an explicit state machine:

```text
STARTING
   ↓
PREFLIGHT
   ↓
DATA_CONNECTED
   ↓
BROKER_CONNECTED
   ↓
STATE_RECONCILED
   ↓
READY
   ↓
SCANNING
   ↓
SIGNAL_FOUND
   ↓
RISK_CHECKED
   ↓
ORDER_SUBMITTED
   ↓
POSITION_MANAGED
   ↓
POSITION_CLOSED
```

Failure states:

```text
SAFE_MODE
DATA_STALE
BROKER_DISCONNECTED
DATABASE_UNAVAILABLE
RECONCILIATION_FAILED
DAILY_LIMIT_REACHED
EMERGENCY_STOPPED
```

No order should be allowed unless the runtime is in an approved `READY` or `SCANNING` state.

---

# 11. Example end-to-end automated trade

## Market condition

```text
Symbol: XAUUSD
H1 trend: bullish
Price: inside H1 bullish order block
Liquidity: Asian low swept
M5: bullish CHOCH
Session: London
Spread: acceptable
```

## Strategy output

```json
{
  "action": "BUY",
  "entry": 2411.40,
  "stop": 2407.90,
  "target": 2418.40,
  "risk_reward": 2.0
}
```

## Risk engine

```text
Balance: $10,000
Risk: 0.5%
Maximum loss: $50
Calculated volume: 0.14 lots
Daily risk used before trade: 0.5%
Daily risk after approval: 1.0%
Decision: approved
```

## Execution

```text
Order intent created
Idempotency key checked
MT5 order submitted
Broker order accepted
Broker position discovered
Internal position reconciled
```

## Management

```text
Price reaches +1R
Stop moved to break-even
Price reaches +2R
Position closed
```

## Recording

```json
{
  "result_r": 2.0,
  "gross_profit": 100.0,
  "commission": 2.1,
  "slippage_cost": 1.4,
  "net_profit": 96.5,
  "execution_status": "RECONCILED"
}
```

---

# 12. AI’s role

AI can help with:

* Translating a discretionary idea into precise rules
* Generating strategy documentation
* Reviewing backtest reports
* Categorizing losing trades
* Detecting data-quality problems
* Comparing strategy versions
* Suggesting hypotheses for testing
* Explaining unusual drawdowns
* Creating monitoring summaries
* Assisting code development and test generation

AI should not be the unrestricted execution authority.

Avoid this architecture:

```text
Chart screenshot
→ LLM says BUY
→ immediate live order
```

Prefer:

```text
Validated numerical features
→ deterministic strategy rules
→ deterministic risk controls
→ canonical execution pipeline
→ broker
```

An LLM may provide a recommendation, but it should not bypass:

```text
strategy approval
position limits
daily loss limits
price freshness checks
order validation
kill switch
broker reconciliation
```

---

# 13. Recommended implementation order for your project

Since your System 2 is the execution system, use this order:

### Stage A — Strategy contract

Create one machine-readable, versioned strategy specification with exact entry, SL, TP, filter and risk rules.

### Stage B — Shared feature engine

Use the same market-structure and SMC definitions in backtest, replay, shadow and demo modes.

### Stage C — Deterministic backtester

Implement next-bar execution, spread, commission, slippage and no-look-ahead validation.

### Stage D — Validation gate

Require out-of-sample, walk-forward, Monte Carlo and your locked performance thresholds.

### Stage E — Replay mode

Feed historical candles one at a time through the live System 2 pipeline.

### Stage F — Shadow mode

Run against live MT5 prices without submitting orders.

### Stage G — Paper mode

Simulate orders using live prices.

### Stage H — MT5 demo

Enable broker demo writes through the canonical execution pipeline.

### Stage I — Operational qualification

Validate restart recovery, duplicate prevention, reconciliation, stale data handling and kill-switch behaviour.

### Stage J — Limited live mode

Use minimum volume, 0.5% or lower risk, strict daily loss limits and explicit owner approval.

---

## Final professional pipeline

```text
Trading hypothesis
      ↓
Machine-readable strategy specification
      ↓
Historical data validation
      ↓
Feature generation
      ↓
Realistic backtesting
      ↓
Out-of-sample and robustness tests
      ↓
Signed approved strategy package
      ↓
Historical replay through System 2
      ↓
Live shadow test
      ↓
Paper forward test
      ↓
MT5 demo forward test
      ↓
Operational qualification
      ↓
Limited live deployment
      ↓
Monitoring and versioned improvement
```

The most suitable design for your current project is **Python for strategy, research and risk control; MT5 terminal integration for execution; DuckDB/Parquet for research data; PostgreSQL for operational authority; FastAPI for controls and dashboards; and one canonical execution pipeline shared by demo and live modes.**

[1]: https://www.mql5.com/en/docs/python_metatrader5?utm_source=chatgpt.com "Python Integration - MQL5 Reference"
[2]: https://www.postgresql.org/docs/current/transaction-iso.html?utm_source=chatgpt.com "Documentation: 18: 13.2. Transaction Isolation"
[3]: https://fastapi.tiangolo.com/?utm_source=chatgpt.com "FastAPI - FastAPI"
[4]: https://docs.docker.com/compose/?utm_source=chatgpt.com "Docker Compose"
