#!/usr/bin/env python3
"""Trade management rules (execution layer): breakeven, partial, target.

Deterministic: given an open trade and current price, returns the management
actions to apply via metatrader modify_position. Stops only ever tighten.
"""


def manage(entry, stop, target, price, direction, be_at_r):
    risk = abs(entry - stop)
    if risk <= 0:
        return {"r_multiple": 0, "actions": [{"action": "invalid_stop"}]}
    r = (price - entry) / risk if direction == "long" else (entry - price) / risk
    actions = []
    if (direction == "long" and price >= target) or (direction == "short" and price <= target):
        actions.append({"action": "target_hit", "detail": "close full"})
    elif r >= be_at_r:
        actions.append({"action": "move_stop_to_breakeven", "new_stop": round(entry, 5)})
        actions.append({"action": "take_partial", "detail": "50% at +" + str(be_at_r) + "R"})
    else:
        actions.append({"action": "hold"})
    return {"r_multiple": round(r, 2), "direction": direction, "actions": actions}


if __name__ == "__main__":
    import argparse, json
    import config
    ap = argparse.ArgumentParser()
    for f in ("entry", "stop", "target", "price"):
        ap.add_argument("--" + f, type=float, required=True)
    ap.add_argument("--direction", default="long")
    a = ap.parse_args()
    cfg = config.load()
    print(json.dumps(manage(a.entry, a.stop, a.target, a.price, a.direction, cfg.execution.breakeven_at_r), indent=2))
