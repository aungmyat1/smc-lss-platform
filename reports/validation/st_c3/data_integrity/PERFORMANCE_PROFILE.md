# ST-C3 Source Integrity Performance Profile

Status: **IN_PROGRESS**

Recommendation: **CONTINUE_EVIDENCE_COLLECTION**

Guardrail: Evidence-sample acquisition downloads raw source files only; it does not approve data, change governance, or open replay.

## Throughput

- Mode: `parallel`
- Workers: `8`
- Elapsed seconds: `2464.029992900003`
- Acquisition seconds: `2193.6360436999967`
- Profiling/report seconds: `270.3939434000058`
- Attempted source hours: `3276`
- Downloaded source hours: `3276`
- Cached verified source hours: `0`
- Failed source hours: `0`
- Cache hit rate: `0.0`
- Download throughput hours/minute: `79.77175625555664`
- Payload MB: `62.126862`
- Parallel efficiency proxy: `0.7727854900454859`
- Top bottlenecks: `[{'stage': 'download_cache', 'seconds': 2193.6360436999967}, {'stage': 'bi5_decompression_parse', 'seconds': 222.93033089970413}]`

## Stage Timings

- Download/cache seconds: `2193.6360436999967`
- `.bi5` decompression/parse seconds: `222.93033089970413`
- M1 reconstruction seconds: `44.393701399996644`
- Aggregation seconds: `None`
- Validation seconds: `None`
- Cross-provider lookup seconds: `None`
- Report generation/profile seconds: `270.3939434000058`

## Stage Notes

- Download/cache: includes network download, cache verification, retries, and payload parse verification inside _download_hour
- `.bi5` decompression/parse: post-acquisition profiling pass over successful source-hour files
- M1 reconstruction: post-acquisition minute grouping profile over parsed ticks
- Aggregation: not run in provider-qualification acquisition pipeline
- Validation: not run in provider-qualification acquisition pipeline
- Cross-provider lookup: measured by statistical/cross-provider report generation, not acquisition

## Worker Utilization

- Deterministic assignment: `task_index modulo worker_count`
- Planned by worker: `{'1': 410, '2': 410, '3': 410, '4': 410, '5': 409, '6': 409, '7': 409, '8': 409}`
- Completed by worker: `{'1': 410, '2': 410, '3': 410, '4': 410, '5': 409, '6': 409, '7': 409, '8': 409}`
- Failed by worker: `{'1': 0, '2': 0, '3': 0, '4': 0, '5': 0, '6': 0, '7': 0, '8': 0}`
- Task seconds by worker: `{'1': 1871.2342163001886, '2': 1869.8060353000183, '3': 1955.772226200119, '4': 1996.501723499954, '5': 1868.5672594999342, '6': 1913.242094999805, '7': 1886.641744799941, '8': 1871.5677038000722}`
- Task order matches plan: `True`

No market data was altered, fabricated, interpolated, or approved.
