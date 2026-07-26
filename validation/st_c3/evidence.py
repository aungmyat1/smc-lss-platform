"""ST-C3 evidence objects.

Evidence field names/requiredness are pulled at construction time from
`specs/st-c3_v1.0.1.yaml`'s `evidence` registry (§4.0) so this module cannot
silently drift from the frozen spec. This module does not compute evidence
from price data (that is out of scope until the relevant thresholds are
frozen — see `validation/st_c3/__init__.py`); it only validates and holds
evidence objects supplied by a caller (e.g. a golden/negative test case).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any, Mapping

import yaml

SPEC_PATH = Path("specs/st-c3_v1.0.1.yaml")

_UNIVERSAL_FIELDS = frozenset({"valid", "reason"})


@lru_cache(maxsize=1)
def load_spec(path: str = str(SPEC_PATH)) -> dict[str, Any]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _evidence_registry() -> Mapping[str, frozenset[str]]:
    spec = load_spec()
    registry = {}
    for kind, entry in spec["evidence"].items():
        registry[kind] = frozenset(entry["fields"]) - _UNIVERSAL_FIELDS
    return registry


def required_extra_fields(kind: str) -> frozenset[str]:
    registry = _evidence_registry()
    if kind not in registry:
        raise ValueError(f"Unknown ST-C3 evidence kind: {kind!r}")
    return registry[kind]


@dataclass(frozen=True)
class Evidence:
    """A single ST-C3 evidence object, spec-conformant by construction."""

    kind: str
    id: str
    tf: tuple[str, ...]
    valid: bool
    reason: str
    timestamp: str
    fields: Mapping[str, Any] = field(default_factory=dict)
    provenance: str = "STC3_v1"

    def get(self, name: str) -> Any:
        if name not in self.fields:
            raise AttributeError(f"{self.kind} evidence {self.id!r} has no field {name!r}")
        return self.fields[name]


def make_evidence(
    kind: str,
    *,
    id: str,
    tf: str | tuple[str, ...],
    valid: bool,
    reason: str,
    timestamp: str,
    provenance: str = "STC3_v1",
    **extra_fields: Any,
) -> Evidence:
    """Build a spec-validated Evidence object.

    Raises ValueError if `extra_fields` does not exactly match the field set
    the frozen spec's evidence registry declares for `kind`.
    """
    required = required_extra_fields(kind)
    given = frozenset(extra_fields)
    missing = required - given
    unexpected = given - required
    if missing:
        raise ValueError(f"{kind} missing required fields: {sorted(missing)}")
    if unexpected:
        raise ValueError(f"{kind} got unexpected fields not in the frozen spec: {sorted(unexpected)}")
    tf_tuple = (tf,) if isinstance(tf, str) else tuple(tf)
    return Evidence(
        kind=kind,
        id=id,
        tf=tf_tuple,
        valid=valid,
        reason=reason,
        timestamp=timestamp,
        fields=dict(extra_fields),
        provenance=provenance,
    )
