# S1-G7 Alignment Matrix (Real Evidence Intake)
Stage: A  
Gate: S1-G7  
Status: Real Evidence Intake  
Spec Basis: v1.0.7 authoritative, v1.0.8 draft analytical-only

| Component | Signal Evidence | SOP-A Evidence | Execution Requirement | Alignment (Y/P/N) | Notes |
|---|---|---|---|---|---|
| HTF Bias | BEARISH | BEARISH | bearish | Y | H4 bias aligns with the selected intake snapshot. |
| HTF POI | OB/FVG present | order_block_or_fvg_confluence | htf_poi alignment | P | POI exists, but sits outside OTE at the snapshot. |
| Draw-on-Liquidity | buy-side sweep, sell-side draw | sell_side | draw_on_liquidity | Y | Buy-side liquidity was swept at the intake bar. |
| OB Validation | present, fresh | present | OB interaction | P | OB is present but outside OTE. |
| FVG Validation | present, fresh | present | FVG interaction | P | FVG is present but outside OTE. |
| Liquidity Behavior | sweep + reclaim | sweep=valid | reclaim model | Y | Sweep and reclaim were both real and valid. |
| Sweep | valid | valid | sweep structure | Y | Sweep evidence is present in the real bundle. |
| CHoCH | M3 CHoCH present | m3_choch_with_local_sweep | confirmation structure | P | M3 confirmation exists; M1 is missing, so this remains partial. |
| MSS | partial M3 only | partial_m3_only | confirmation structure | P | M1 microstructure is unavailable. |
| Analytical OTE | not detected | not_detected | OTE zone | N | Dealing range and OTE did not form at the intake bar. |
| Session Gate | LONDON | session=LONDON | session gate | Y | The selected bar is inside the allowed London window. |
| News Gate | not evaluated | not_evaluated | news gate | P | No news feed is wired into this intake snapshot. |
| Spread Gate | not evaluated | not_evaluated | spread gate | P | No spread feed is wired into this intake snapshot. |
| Daily Risk Gate | not evaluated | not_evaluated | daily risk gate | P | No account-risk feed is wired into this intake snapshot. |

## Notes
- This matrix is analytical-only.
- No execution, lifecycle, kernel, or evidence-engine behavior is introduced.
- Alignment values:
  - **Y** = aligned
  - **P** = partially aligned
  - **N** = misaligned
