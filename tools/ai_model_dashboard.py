"""Pure derivations for the AI model dashboard.

The functions in this module never turn missing evidence into zero.  Values
returned here are intended for logarithmic charts, so every quantitative
dataclass rejects non-positive values at its boundary.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Iterable


POSITIVE_STATUSES = {"FACT", "DERIVED", "ESTIMATE", "SCENARIO"}
TRAINING_KEYS = (
    "parameters_total_active",
    "training_flop",
    "accelerators_and_hours",
    "power_or_energy_envelope",
    "replacement_value",
)
INFERENCE_KEYS = (
    "artifact_or_weight_floor",
    "h100_capacity_equivalents",
    "accelerator_tdp_scenario",
    "accelerator_capex_scenario",
    "parameters_total_active",
)
CAPACITY_SCOPE = "physical_capacity_floor_not_topology_not_sla"
TDP_SCOPE = "accelerator_only_tdp_scenario_not_wall_power"
CAPEX_SCOPE = "accelerator_equivalent_scenario_not_api_not_system_price"
SCENARIO_SOURCE = "S_COURSE_DESIGN"


def _decimal(value) -> Decimal:
    if isinstance(value, Decimal):
        return value
    return Decimal(str(value))


def _positive_finite_decimal(value, description: str) -> Decimal:
    number = _decimal(value)
    if not number.is_finite() or number <= 0:
        raise ValueError(f"{description} must be finite and positive")
    return number


@dataclass(frozen=True)
class PlotPoint:
    model_id: str
    year: int
    value: Decimal
    unit: str
    status: str
    low: Decimal | None
    high: Decimal | None
    source_ids: tuple[str, ...]
    label: str
    claim_scope: str

    def __post_init__(self):
        if isinstance(self.year, bool) or not isinstance(self.year, int) or self.year <= 0:
            raise ValueError("plot point year must be a positive integer")
        if isinstance(self.source_ids, str) or not isinstance(self.source_ids, tuple):
            raise ValueError("plot point source_ids must be a tuple")
        if not all(isinstance(source_id, str) and source_id for source_id in self.source_ids):
            raise ValueError("plot point source_ids require non-empty strings")
        if not all(
            (self.model_id, self.unit, self.status, self.source_ids, self.label, self.claim_scope)
        ):
            raise ValueError("plot points require traceability, labels, and claim scope")
        if self.status not in POSITIVE_STATUSES:
            raise ValueError("plot point status must describe positive evidence")
        value = _positive_finite_decimal(self.value, "log-axis values")
        low = (
            _positive_finite_decimal(self.low, "log-axis lower bound")
            if self.low is not None else None
        )
        high = (
            _positive_finite_decimal(self.high, "log-axis upper bound")
            if self.high is not None else None
        )
        if low is not None and low > value:
            raise ValueError("low/value/high must form an ordered interval")
        if high is not None and value > high:
            raise ValueError("low/value/high must form an ordered interval")
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "low", low)
        object.__setattr__(self, "high", high)
        object.__setattr__(self, "source_ids", tuple(self.source_ids))


@dataclass(frozen=True)
class ParetoPoint:
    model_id: str
    cost_low: Decimal
    cost_high: Decimal
    score_low: Decimal
    score_high: Decimal

    def __post_init__(self):
        if not isinstance(self.model_id, str) or not self.model_id:
            raise ValueError("Pareto model ID is required")
        values = tuple(
            _positive_finite_decimal(value, "Pareto values")
            for value in (self.cost_low, self.cost_high, self.score_low, self.score_high)
        )
        cost_low, cost_high, score_low, score_high = values
        if cost_low > cost_high or score_low > score_high:
            raise ValueError("Pareto bounds must form an ordered interval")
        for field, value in zip(
            ("cost_low", "cost_high", "score_low", "score_high"), values
        ):
            object.__setattr__(self, field, value)


@dataclass(frozen=True)
class ParetoResult:
    safe_ids: tuple[str, ...]
    possible_ids: tuple[str, ...]


@dataclass(frozen=True)
class CapacityScenario:
    hbm_gb: Decimal = Decimal("80")
    tdp_w: Decimal = Decimal("700")
    unit_price_usd: Decimal = Decimal("30000")
    precision: str = "BF16"

    def __post_init__(self):
        for field in ("hbm_gb", "tdp_w", "unit_price_usd"):
            value = _positive_finite_decimal(getattr(self, field), "scenario values")
            object.__setattr__(self, field, value)
        precision = self.precision.upper()
        if precision not in {"BF16", "FP8", "INT8", "INT4"}:
            raise ValueError("precision must be BF16, FP8, INT8, or INT4")
        object.__setattr__(self, "precision", precision)


def _is_positive_cell(cell: dict | None) -> bool:
    return bool(
        cell
        and cell.get("status") in POSITIVE_STATUSES
        and cell.get("value") is not None
        and not isinstance(cell.get("value"), bool)
        and _can_be_positive_decimal(cell["value"])
    )


def _can_be_positive_decimal(value) -> bool:
    try:
        number = _decimal(value)
        return number.is_finite() and number > 0
    except (ValueError, TypeError, ArithmeticError):
        return False


def _product_status(*statuses: str) -> str:
    """Classify a multiplication without hiding scenario or uncertainty."""
    if "SCENARIO" in statuses:
        return "SCENARIO"
    if "ESTIMATE" in statuses:
        return "ESTIMATE"
    return "DERIVED"


def _point(model: dict, cell: dict, label: str, claim_scope: str, **overrides) -> PlotPoint:
    return PlotPoint(
        model_id=model["id"],
        year=int(model["year"]["value"]),
        value=overrides.get("value", cell["value"]),
        unit=overrides.get("unit", cell["unit"]),
        status=overrides.get("status", cell["status"]),
        low=overrides.get("low", cell.get("low")),
        high=overrides.get("high", cell.get("high")),
        source_ids=tuple(overrides.get("source_ids", cell.get("source_ids", ()))),
        label=label,
        claim_scope=claim_scope,
    )


def _ordered(points: Iterable[PlotPoint]) -> list[PlotPoint]:
    label_order = {
        "concurrent accelerators": 0,
        "accelerator-hours": 1,
        "active": 0,
        "total": 1,
    }
    return sorted(
        points,
        key=lambda point: (
            point.year,
            point.model_id,
            label_order.get(point.label, 0),
            point.label,
            point.unit,
        ),
    )


def _parameter_points(model: dict) -> list[PlotPoint]:
    points = []
    for metric_id, label in (("parameters_total", "total"), ("parameters_active", "active")):
        cell = model["metrics"].get(metric_id)
        if _is_positive_cell(cell):
            points.append(_point(model, cell, label, "published_parameter_counts"))
    return points


def build_training_series(ledger: dict) -> dict[str, list[PlotPoint]]:
    """Build five training series without normalizing unlike hardware units."""
    series = {key: [] for key in TRAINING_KEYS}
    for model in ledger.get("dashboard_models", ()):
        metrics = model["metrics"]
        series["parameters_total_active"].extend(_parameter_points(model))

        flop = metrics.get("training_flop")
        if _is_positive_cell(flop):
            series["training_flop"].append(
                _point(model, flop, "training FLOP", "training_work_fact_derived_or_estimate")
            )

        for metric_id, label in (
            ("accelerators_concurrent", "concurrent accelerators"),
            ("accelerator_hours", "accelerator-hours"),
        ):
            cell = metrics.get(metric_id)
            if _is_positive_cell(cell):
                series["accelerators_and_hours"].append(
                    _point(model, cell, label, "native_accelerator_units_kept_separate")
                )

        count = metrics.get("accelerators_concurrent")
        power = metrics.get("accelerator_power_basis")
        if _is_positive_cell(count) and _is_positive_cell(power):
            basis = power.get("basis")
            if not basis or not str(power.get("unit", "")).startswith("W_per_"):
                raise ValueError("numeric accelerator power requires an explicit compatible basis")
            sources = tuple(dict.fromkeys(count.get("source_ids", ()) + power.get("source_ids", ())))
            count_value = _decimal(count["value"])
            power_value = _decimal(power["value"])
            status = _product_status(count["status"], power["status"])
            series["power_or_energy_envelope"].append(
                _point(
                    model,
                    power,
                    basis,
                    "accelerator_only_power_envelope_not_measured_wall_energy",
                    value=count_value * power_value,
                    unit="W",
                    status=status,
                    source_ids=sources,
                    low=_decimal(count.get("low", count_value))
                    * _decimal(power.get("low", power_value)),
                    high=_decimal(count.get("high", count_value))
                    * _decimal(power.get("high", power_value)),
                )
            )

    models_by_id = {model["id"]: model for model in ledger.get("dashboard_models", ())}
    for case in ledger.get("training_cases", ()):
        dashboard_id = case.get("model_id", "").replace("M_", "DM_", 1)
        model = models_by_id.get(dashboard_id)
        power = case.get("metrics", {}).get("accelerator_power")
        if model is None or not _is_positive_cell(power):
            continue
        series["power_or_energy_envelope"].append(
            _point(
                model,
                power,
                power.get("power_basis", "documented_power_basis"),
                "accelerator_only_power_envelope_not_measured_wall_energy",
            )
        )
    return {key: _ordered(points) for key, points in series.items()}


def build_inference_series(
    ledger: dict, scenario: CapacityScenario
) -> dict[str, list[PlotPoint]]:
    """Build physical-capacity scenarios; no point represents runtime or SLA."""
    series = {key: [] for key in INFERENCE_KEYS}
    floor_metric = f"weight_floor_{scenario.precision.lower()}"
    capacity_bytes = scenario.hbm_gb * Decimal("1e9")

    for model in ledger.get("dashboard_models", ()):
        metrics = model["metrics"]
        series["parameters_total_active"].extend(_parameter_points(model))

        artifact = metrics.get("artifact_bytes")
        artifact_matches = (
            _is_positive_cell(artifact)
            and str(artifact.get("precision", "")).upper() == scenario.precision
        )
        floor = metrics.get(floor_metric)
        if _is_positive_cell(artifact):
            artifact_scope = (
                "documented_artifact_bytes_not_runtime"
                if artifact_matches
                else "documented_artifact_bytes_precision_unspecified_not_runtime"
            )
            series["artifact_or_weight_floor"].append(
                _point(model, artifact, "documented artifact", artifact_scope)
            )
        if artifact_matches:
            selected = artifact
        elif _is_positive_cell(floor):
            selected = floor
            label = f"{scenario.precision} weight floor"
            selected_scope = "theoretical_weight_payload_floor_not_artifact_not_runtime"
            series["artifact_or_weight_floor"].append(
                _point(model, selected, label, selected_scope)
            )
        else:
            continue
        count = (_decimal(selected["value"]) / capacity_bytes).to_integral_value(
            rounding="ROUND_CEILING"
        )
        sources = tuple(dict.fromkeys((*selected.get("source_ids", ()), SCENARIO_SOURCE)))
        common = dict(
            cell=selected,
            source_ids=sources,
            low=None,
            high=None,
            status="SCENARIO",
        )
        series["h100_capacity_equivalents"].append(
            _point(model, label=f"{scenario.hbm_gb} GB HBM capacity floor", claim_scope=CAPACITY_SCOPE, value=count, unit="accelerator", **common)
        )
        series["accelerator_tdp_scenario"].append(
            _point(model, label=f"{scenario.tdp_w} W per accelerator", claim_scope=TDP_SCOPE, value=count * scenario.tdp_w, unit="W", **common)
        )
        series["accelerator_capex_scenario"].append(
            _point(model, label=f"USD {scenario.unit_price_usd} per accelerator", claim_scope=CAPEX_SCOPE, value=count * scenario.unit_price_usd, unit="USD", **common)
        )
    return {key: _ordered(points) for key, points in series.items()}


def _dominates(a_cost, a_score, b_cost, b_score) -> bool:
    return a_cost <= b_cost and a_score >= b_score and (
        a_cost < b_cost or a_score > b_score
    )


def pareto_frontier(points: list[ParetoPoint]) -> ParetoResult:
    """Return robust (safe) and optimistic (possible) interval frontiers.

    A point is safe only if no competitor's optimistic corner dominates its
    pessimistic corner.  A point is possible when its own optimistic corner is
    not dominated by any competitor's pessimistic corner.  This is an
    existence test: select the candidate's best realization and every rival's
    worst realization.  No interval midpoint is used.
    """
    if len({point.model_id for point in points}) != len(points):
        raise ValueError("Pareto model IDs must be unique")

    safe = []
    possible = []
    for point in points:
        competitors = [other for other in points if other.model_id != point.model_id]
        if not any(
            _dominates(
                other.cost_low,
                other.score_high,
                point.cost_high,
                point.score_low,
            )
            for other in competitors
        ):
            safe.append(point)
        if not any(
            _dominates(
                other.cost_high,
                other.score_low,
                point.cost_low,
                point.score_high,
            )
            for other in competitors
        ):
            possible.append(point)

    order = lambda point: (point.cost_low, point.model_id)
    return ParetoResult(
        safe_ids=tuple(point.model_id for point in sorted(safe, key=order)),
        possible_ids=tuple(point.model_id for point in sorted(possible, key=order)),
    )
