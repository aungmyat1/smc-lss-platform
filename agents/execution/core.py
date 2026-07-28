from __future__ import annotations


def _blocked(name: str) -> dict[str, str]:
    return {
        "agent": name,
        "status": "blocked",
        "reason": "Execution-stage agents are unavailable until Stage B authorization.",
    }


class SignalIngestAgent:
    def load(self) -> dict[str, str]:
        return _blocked("SignalIngestAgent")


class RiskManagerAgent:
    def check(self) -> dict[str, str]:
        return _blocked("RiskManagerAgent")


class OrderManagerAgent:
    def execute(self) -> dict[str, str]:
        return _blocked("OrderManagerAgent")


class MT5AdapterAgent:
    def send(self) -> dict[str, str]:
        return _blocked("MT5AdapterAgent")


class PositionManagerAgent:
    def update(self) -> dict[str, str]:
        return _blocked("PositionManagerAgent")


class ExecutionLoggerAgent:
    def log(self) -> dict[str, str]:
        return _blocked("ExecutionLoggerAgent")


class KillSwitchAgent:
    def monitor(self) -> dict[str, str]:
        return _blocked("KillSwitchAgent")
