Complete automated trading architecture

A professional architecture should separate research, strategy decisions, risk control and broker execution.

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

This matches your current direction: System 1 approves strategies; System 2 executes only approved packages.

4. System 1: Research and validation architecture
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
Recommended modules
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
5. System 2: Automated execution architecture
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
Recommended modules
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
6. Detailed live automation flow
Step 1: Receive market data
tick = broker.get_tick("XAUUSD")

The data validator checks:

Is the price recent?
Is bid lower than ask?
Is spread acceptable?
Is the symbol tradable?
Is the market session active?
Step 2: Build candles and features
features = feature_engine.calculate(
    symbol="XAUUSD",
    bias_timeframe="H1",
    execution_timeframe="M5",
)

Possible output:

{
  "h1_bias": "bullish",
  "inside_h1_poi": true,
  "sell_side_swept": true,
  "m5_choch": "bullish",
  "displacement": true
}
Step 3: Evaluate strategy
decision = strategy_engine.evaluate(features)

Output:

{
  "action": "BUY",
  "confidence": 1.0,
  "entry_model": "market_next_tick",
  "stop_loss": 2407.90,
  "take_profit": 2418.40
}

For a rule-based strategy, confidence should not replace the actual rule result. It should usually be:

All mandatory rules passed → valid
One mandatory rule failed → no trade
Step 4: Risk validation

The risk engine checks:

Is trading enabled?
Is demo-only mode active?
Has the daily loss limit been reached?
Is the account drawdown acceptable?
Is another XAUUSD position open?
Is risk below 0.5%?
Is the stop distance valid?
Is the calculated lot size broker-valid?
Is there enough free margin?

Example lot-size formula:

Risk amount = Account balance × Risk percentage

Risk amount:
$10,000 × 0.5% = $50

Lot size =
Risk amount ÷ monetary value of stop distance

The calculation must use the broker’s actual contract size, tick size, tick value, volume minimum and volume step.

Step 5: Create an order intent

Do not send a raw order directly from the strategy engine.

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

The intent is audited before execution.

Step 6: Execute through one canonical pipeline
Strategy
   ↓
Risk approval
   ↓
Order validation
   ↓
Idempotency check
   ↓
Broker adapter

Every strategy must use the same pipeline.

Never allow:

Strategy A → canonical pipeline
Strategy B → direct MT5 call
Strategy C → separate custom executor

That creates inconsistent risk control and duplicate execution paths.

Step 7: Broker adapter

The adapter translates your internal order format into an MT5 request.

class BrokerAdapter:
    def get_symbol_specification(self, symbol): ...
    def get_account_state(self): ...
    def place_order(self, intent): ...
    def cancel_order(self, broker_order_id): ...
    def close_position(self, position_id): ...
    def get_open_positions(self): ...

Possible implementations:

SimulatedBrokerAdapter
MT5TerminalAdapter
MetaApiAdapter
OandaAdapter
BybitAdapter

The strategy code should not know which broker is being used.

Step 8: Reconcile broker truth

After submitting the order, never assume it succeeded.

Requested order
    ↓
Broker response
    ↓
Query broker orders
    ↓
Query broker positions
    ↓
Compare internal state with broker state

Possible outcomes:

Order accepted and position opened
Order rejected
Order accepted but no fill
Partial fill
Position opened with different volume
Connection lost after submission
Duplicate submission attempted

The broker is the final authority for actual positions.

Step 9: Manage the trade

The trade-management engine can implement:

Fixed TP and SL
Break-even after +1R
Partial close at +1R
Trailing stop
Time-based exit
Session-close exit
Emergency close

These rules must be defined in the strategy package, not invented dynamically.

Example:

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
Step 10: Record every event

Use append-only events such as:

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

PostgreSQL is suitable for authoritative operational records and supports transactional updates with explicit commit and rollback behaviour.

7. Recommended technology stack
Core language
Python

Use Python for:

Data processing
Feature calculation
Strategy evaluation
Backtesting
Risk management
Broker integration
APIs
Analytics
AI-assisted analysis

Useful packages:

pandas or Polars
NumPy
Pydantic
SQLAlchemy
Alembic
pytest
scikit-learn, where justified
MT5 execution
Option A: Python connected to MT5 terminal

Best for your current Windows VPS setup.

Python service
→ MetaTrader5 Python package
→ locally running MT5 terminal
→ VT Markets/Vantage broker

The official integration communicates directly with the MetaTrader terminal and provides functions for market data and terminal interaction.

Option B: MQL5 Expert Advisor
Python strategy service
→ local REST/socket/file bridge
→ MQL5 EA
→ MT5

This can provide tighter terminal-level control but introduces bridge complexity.

Recommended for your first implementation

Use:

Python strategy and execution engine
+
MetaTrader5 Python terminal integration
+
Windows VPS

Later, add an EA bridge only when a measured technical need exists.

Database
PostgreSQL

Use it for:

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
Parquet or DuckDB

Use for:

historical candles
feature datasets
backtest outputs
large research queries

Recommended split:

DuckDB/Parquet → System 1 research
PostgreSQL → System 2 operational authority
API layer
FastAPI

Use it for:

dashboard APIs
health endpoints
manual kill switch
strategy status
trade history
readiness status
risk status
operational controls

FastAPI is designed for typed Python API development, and its official guidance supports structuring larger applications across multiple files and routers.

Do not use simple FastAPI background tasks as the main trading runtime. The trading engine should run as an independent supervised process.

Deployment
Windows VPS

Because MT5 normally runs as a Windows desktop terminal:

Windows VPS
├── MT5 terminal
├── Python trading runtime
├── PostgreSQL or remote PostgreSQL connection
├── FastAPI dashboard API
├── monitoring agent
└── log collector

Run the Python components as Windows services using:

NSSM
Windows Task Scheduler for limited maintenance jobs
PowerShell management scripts
Docker

Docker is useful for:

PostgreSQL
dashboard API
research services
monitoring
Redis
Grafana

However, the desktop MT5 terminal is usually easier to run directly on the Windows host.

Docker Compose can define application services, networks and persistent volumes in one YAML configuration and manage the application stack together.

Recommended hybrid deployment:

Windows host:
  MT5 terminal
  MT5 Python execution worker

Docker:
  PostgreSQL
  FastAPI
  dashboard
  Prometheus
  Grafana
Monitoring

Recommended tools:

Prometheus → metrics
Grafana → dashboards
Structured JSON logs → event analysis
Telegram/email → critical alerts
Sentry → application exceptions

Monitor:

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
8. Suggested repository architecture
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
9. One strategy, multiple operating modes

The most important design principle is that all environments should run the same strategy rules.

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

Only adapters and safety configuration should change.

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

This prevents the common mistake of having one strategy implementation for backtesting and another for live execution.

10. Automation state machine

Use an explicit state machine:

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

Failure states:

SAFE_MODE
DATA_STALE
BROKER_DISCONNECTED
DATABASE_UNAVAILABLE
RECONCILIATION_FAILED
DAILY_LIMIT_REACHED
EMERGENCY_STOPPED

No order should be allowed unless the runtime is in an approved READY or SCANNING state.

11. Example end-to-end automated trade
Market condition
Symbol: XAUUSD
H1 trend: bullish
Price: inside H1 bullish order block
Liquidity: Asian low swept
M5: bullish CHOCH
Session: London
Spread: acceptable
Strategy output
{
  "action": "BUY",
  "entry": 2411.40,
  "stop": 2407.90,
  "target": 2418.40,
  "risk_reward": 2.0
}
Risk engine
Balance: $10,000
Risk: 0.5%
Maximum loss: $50
Calculated volume: 0.14 lots
Daily risk used before trade: 0.5%
Daily risk after approval: 1.0%
Decision: approved
Execution
Order intent created
Idempotency key checked
MT5 order submitted
Broker order accepted
Broker position discovered
Internal position reconciled
Management
Price reaches +1R
Stop moved to break-even
Price reaches +2R
Position closed
Recording
{
  "result_r": 2.0,
  "gross_profit": 100.0,
  "commission": 2.1,
  "slippage_cost": 1.4,
  "net_profit": 96.5,
  "execution_status": "RECONCILED"
}
12. AI’s role

AI can help with:

Translating a discretionary idea into precise rules
Generating strategy documentation
Reviewing backtest reports
Categorizing losing trades
Detecting data-quality problems
Comparing strategy versions
Suggesting hypotheses for testing
Explaining unusual drawdowns
Creating monitoring summaries
Assisting code development and test generation

AI should not be the unrestricted execution authority.

Avoid this architecture:

Chart screenshot
→ LLM says BUY
→ immediate live order

Prefer:

Validated numerical features
→ deterministic strategy rules
→ deterministic risk controls
→ canonical execution pipeline
→ broker

An LLM may provide a recommendation, but it should not bypass:

strategy approval
position limits
daily loss limits
price freshness checks
order validation
kill switch
broker reconciliation
13. Recommended implementation order for your project

Since your System 2 is the execution system, use this order:

Stage A — Strategy contract

Create one machine-readable, versioned strategy specification with exact entry, SL, TP, filter and risk rules.

Stage B — Shared feature engine

Use the same market-structure and SMC definitions in backtest, replay, shadow and demo modes.

Stage C — Deterministic backtester

Implement next-bar execution, spread, commission, slippage and no-look-ahead validation.

Stage D — Validation gate

Require out-of-sample, walk-forward, Monte Carlo and your locked performance thresholds.

Stage E — Replay mode

Feed historical candles one at a time through the live System 2 pipeline.

Stage F — Shadow mode

Run against live MT5 prices without submitting orders.

Stage G — Paper mode

Simulate orders using live prices.

Stage H — MT5 demo

Enable broker demo writes through the canonical execution pipeline.

Stage I — Operational qualification

Validate restart recovery, duplicate prevention, reconciliation, stale data handling and kill-switch behaviour.

Stage J — Limited live mode

Use minimum volume, 0.5% or lower risk, strict daily loss limits and explicit owner approval.

Final professional pipeline
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

The most suitable design for your current project is Python for strategy, research and risk control; MT5 terminal integration for execution; DuckDB/Parquet for research data; PostgreSQL for operational authority; FastAPI for controls and dashboards; and one canonical execution pipeline shared by demo and live modes.