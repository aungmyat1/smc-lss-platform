# ST-C5 Paid Provider Fallback Plan

If broker MT5 data fails or cannot be exported reproducibly, evaluate paid/API
providers in this priority order:

1. Tiingo FX: configure `TIINGO_API_TOKEN`, approve license, acquire 100 deterministic EURUSD/GBPUSD days.
2. TrueFX: create account/subscription, document terms, acquire 100 deterministic tick days.
3. Darwinex: obtain FTP/live-account access and terms approval, acquire 100 deterministic tick days.

No paid provider may become canonical without passing unchanged ST-C3 evidence gates.
