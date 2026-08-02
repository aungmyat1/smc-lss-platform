# Provider Connection Handoff Checklist

Status: **ACTIVE**

Purpose: prevent cross-provider contamination before any provider history gate
or export run.

Complete this checklist before every provider qualification attempt.

## Required Checks

| Check | Required Evidence |
| --- | --- |
| Previous broker evaluation closed or paused | Provider capability matrix entry |
| Previous broker disconnected | MT5 connection precheck |
| New broker connected | MT5 connection precheck |
| Exact server recorded | MT5 account info |
| Account type recorded | Demo or Live |
| UTC timestamp recorded | Connection evidence file |
| Required symbols verified | EURUSD and GBPUSD symbol metadata |
| Pipeline unchanged | Frozen ST-C5 pipeline reference |
| Validation criteria unchanged | ST-C3/ST-C5 freeze references |
| Provider evaluation SLA active | `reports/operations/PROVIDER_EVALUATION_SLA.md` |

## MetaQuotes Current State

| Field | Current Value |
| --- | --- |
| Expected provider | MetaQuotes Demo |
| Current active server | VTMarkets-Demo |
| Status | PENDING_METAQUOTES_CONNECTION |
| Evidence | `reports/operations/providers/MetaQuotes/attempt_01/CONNECTION_PRECHECK.json` |

## Guardrail

Do not run a provider history gate unless the active MT5 account/server matches
the provider under evaluation. Do not run export, ST-C3 validation, replay,
demo, or live actions from a mismatched provider connection.
