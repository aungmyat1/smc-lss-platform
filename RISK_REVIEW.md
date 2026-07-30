# ST-C3 Canonical Provider Risk Review

Status: **COMPLETE**

Date: 2026-07-30

Provider under review: **Dukascopy**

## Risks And Mitigations

| Risk | Impact | Mitigation |
|---|---|---|
| Provider outage during acquisition | Download interruption or partial raw cache | Cache every successful hour; retry with deterministic backoff; resume from cache |
| Missing hourly tick files | Incomplete M1/M3/M15/H4 construction | Stop and report exact symbol/hour; do not fill gaps |
| Empty market-open files | Missing bars under validator | Treat as blocker unless validator market-closed logic permits the interval |
| Licensing/access changes | Dataset may become unsuitable for research use | Owner license review before full acquisition; record provider terms snapshot |
| Historical data revisions | Checksums may drift across future downloads | Store raw file checksums; version dataset immutably; future changes require new dataset version |
| DST or timezone mistake | Session drift and invalid replay evidence | Use UTC-hour URL addressing; verify sample timestamps; require UTC output only |
| Tick-to-bar aggregation mismatch | Derived bars may differ from provider UI/export bars | Document aggregation rules; validate against fixed OHLC rules; never mix methods in one dataset version |
| Large storage footprint | Disk pressure and slow runs | Stream parsing; ignore raw cache from git; estimate storage before full acquisition |
| Rate limiting | Slow or failed acquisition | Throttle concurrency; retry deterministically; avoid full acquisition in CI |
| Checksum mismatch | Release cannot be reproduced | Hash raw files and constructed CSVs; fail release if hashes differ |
| Validator failure after full acquisition | Dataset remains blocked | Stop; document exact missing timestamps; escalate to institutional vendor if source cannot satisfy contract |

## Residual Risk

Dukascopy passed limited provider verification, but full 2018-2024 continuity
is not proven until the complete acquisition sprint runs and the unchanged
ST-C3 validator passes.

## Recommendation

Proceed to Dataset Acquisition Sprint only after owner approval of
`DATASET_ACQUISITION_PLAN.md`.

Replay remains blocked until the full dataset is acquired, validated,
approved, checksummed, versioned, and recorded in the dataset contract.
