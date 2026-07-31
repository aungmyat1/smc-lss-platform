# ST-C3 Source Integrity Performance Profile

Status: **IN_PROGRESS**

Recommendation: **CONTINUE_EVIDENCE_COLLECTION**

Guardrail: Evidence-sample acquisition downloads raw source files only; it does not approve data, change governance, or open replay.

## Throughput

- Mode: `parallel`
- Workers: `2`
- Elapsed seconds: `57.74290550000296`
- Acquisition seconds: `49.77690850000363`
- Profiling/report seconds: `7.9659919000041555`
- Attempted source hours: `48`
- Downloaded source hours: `48`
- Cached verified source hours: `0`
- Failed source hours: `0`
- Cache hit rate: `0.0`
- Download throughput hours/minute: `49.87625709274107`
- Payload MB: `1.950616`
- Parallel efficiency proxy: `0.7903007928827127`
- Top bottlenecks: `[{'stage': 'download_cache', 'seconds': 49.77690850000363}, {'stage': 'bi5_decompression_parse', 'seconds': 6.610903299981146}]`

## Stage Timings

- Download/cache seconds: `49.77690850000363`
- `.bi5` decompression/parse seconds: `6.610903299981146`
- M1 reconstruction seconds: `1.3092256000018097`
- Aggregation seconds: `None`
- Validation seconds: `None`
- Cross-provider lookup seconds: `None`
- Report generation/profile seconds: `7.9659919000041555`

## Stage Notes

- Download/cache: includes network download, cache verification, retries, and payload parse verification inside _download_hour
- `.bi5` decompression/parse: post-acquisition profiling pass over successful source-hour files
- M1 reconstruction: post-acquisition minute grouping profile over parsed ticks
- Aggregation: not run in provider-qualification acquisition pipeline
- Validation: not run in provider-qualification acquisition pipeline
- Cross-provider lookup: measured by statistical/cross-provider report generation, not acquisition

## Worker Utilization

- Deterministic assignment: `task_index modulo worker_count`
- Planned by worker: `{'1': 24, '2': 24}`
- Completed by worker: `{'1': 24, '2': 24}`
- Failed by worker: `{'1': 0, '2': 0}`
- Task seconds by worker: `{'1': 44.090181200022926, '2': 47.178346799984865}`
- Task order matches plan: `True`

No market data was altered, fabricated, interpolated, or approved.
