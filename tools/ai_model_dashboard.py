"""Pure derivations for the AI model dashboard.

The functions in this module never turn missing evidence into zero.  Values
returned here are intended for logarithmic charts, so every quantitative
dataclass rejects non-positive values at its boundary.
"""

from dataclasses import dataclass, replace
from decimal import Decimal
from typing import Iterable, Literal, Mapping


POSITIVE_STATUSES = {"FACT", "DERIVED", "ESTIMATE", "SCENARIO"}
NEGATIVE_STATUSES = {
    "UNDISCLOSED_BY_CREATOR", "NOT_FOUND", "ESTIMATION_NOT_IDENTIFIABLE",
    "NOT_APPLICABLE",
}
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
TRAINING_REPLACEMENT_SCOPE = (
    "accelerator_only_common_date_replacement_scenario_not_historical_training_cost"
)


def cell_confidence(
    cell: dict,
    cells: dict[str, dict] | None = None,
    _seen: frozenset[str] = frozenset(),
) -> str:
    """Rate evidence/reproducibility for one cell, never model quality.

    ``not_applicable`` is deliberate for scenarios: their arithmetic can be
    reproduced, but the hypothetical premise has no empirical confidence.
    """
    status = cell.get("status")
    sources = tuple(cell.get("source_ids") or ())
    if status == "FACT":
        return "high" if sources else "low"
    if status == "DERIVED":
        inputs = tuple(cell.get("input_metric_ids") or cell.get("inputs") or ())
        if not cell.get("formula") or not sources:
            return "low"
        if not inputs or not cells:
            return "medium"
        levels = []
        for metric_id in inputs:
            if metric_id in _seen or metric_id not in cells:
                return "low"
            levels.append(
                cell_confidence(cells[metric_id], cells, _seen | {metric_id})
            )
        if "low" in levels or "not_applicable" in levels:
            return "low"
        return "medium" if "medium" in levels else "high"
    if status == "ESTIMATE":
        bounded = cell.get("low") is not None and cell.get("high") is not None
        anchored = bool(sources and cell.get("assumptions"))
        return "medium" if bounded and anchored else "low"
    if status == "SCENARIO":
        return "not_applicable"
    if status in NEGATIVE_STATUSES:
        audited = bool(cell.get("corpus_checked") or cell.get("missing_observables"))
        dated = bool(cell.get("searched_on") or status == "UNDISCLOSED_BY_CREATOR")
        return "high" if sources and audited and dated else "low"
    return "low"


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
    confidence: str = "medium"

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
        if self.confidence not in {"high", "medium", "low", "not_applicable"}:
            raise ValueError("plot point confidence must use the documented policy")
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
class AbsenceSummary:
    """Auditable count of cells deliberately excluded from a figure.

    The count has a normalized ``UNDISCLOSED`` key so a reader need not know
    the ledger's longer ``UNDISCLOSED_BY_CREATOR`` status to understand the
    absence note.  It is metadata for the visual, never a plotted datum.
    """

    metric_id: str
    counts: Mapping[str, int]
    searched_on: str

    def __post_init__(self):
        if not self.metric_id or not self.searched_on:
            raise ValueError("absence summaries require a metric and search date")
        if any(count < 0 for count in self.counts.values()):
            raise ValueError("absence summary counts cannot be negative")
        # A copied dict remains JSON/asdict-friendly for the Markdown and SVG
        # writer.  ``frozen`` protects replacement of the field at this layer.
        object.__setattr__(self, "counts", dict(self.counts))


@dataclass(frozen=True)
class FigureRow:
    """One serializable mark shared by a figure and its equivalent table."""

    model_id: str
    label: str
    year: int
    low: Decimal
    high: Decimal
    unit: str
    status: str
    confidence: str
    scope: str
    source_ids: tuple[str, ...]
    x_offset: float = 0.0
    cost_low: Decimal | None = None
    cost_high: Decimal | None = None
    frontier: Literal["safe", "possible", "dominated"] | None = None

    def __post_init__(self):
        if not all((self.model_id, self.label, self.unit, self.status, self.confidence, self.scope)):
            raise ValueError("figure rows require traceability and visual metadata")
        if isinstance(self.year, bool) or not isinstance(self.year, int) or self.year <= 0:
            raise ValueError("figure row year must be a positive integer")
        bounds = tuple(
            _positive_finite_decimal(value, "figure row bounds")
            for value in (self.low, self.high)
        )
        if bounds[0] > bounds[1]:
            raise ValueError("figure row bounds must be ordered")
        if isinstance(self.source_ids, str) or not isinstance(self.source_ids, tuple):
            raise ValueError("figure row source_ids must be a tuple")
        if not all(isinstance(source_id, str) and source_id for source_id in self.source_ids):
            raise ValueError("figure row source_ids require non-empty strings")
        if self.cost_low is not None or self.cost_high is not None:
            if self.cost_low is None or self.cost_high is None:
                raise ValueError("Pareto costs require both bounds")
            costs = tuple(
                _positive_finite_decimal(value, "Pareto cost bounds")
                for value in (self.cost_low, self.cost_high)
            )
            if costs[0] > costs[1]:
                raise ValueError("Pareto cost bounds must be ordered")
            object.__setattr__(self, "cost_low", costs[0])
            object.__setattr__(self, "cost_high", costs[1])
        if self.frontier not in {None, "safe", "possible", "dominated"}:
            raise ValueError("figure row frontier must be safe, possible, or dominated")
        object.__setattr__(self, "low", bounds[0])
        object.__setattr__(self, "high", bounds[1])
        object.__setattr__(self, "x_offset", float(self.x_offset))


@dataclass(frozen=True)
class FigureSpec:
    """A single source of truth for one plotted figure and both of its tables."""

    figure_id: str
    filename: str
    route: Literal["essential", "annex"]
    question: str
    rows: tuple[FigureRow, ...]
    compact_ids: tuple[str, ...]
    direct_label_ids: tuple[str, ...]
    x_scale: Literal["year", "log_cost"]
    y_scale: Literal["linear", "log"]
    absence: AbsenceSummary | None
    snapshot_date: str | None = None

    def __post_init__(self):
        if not self.figure_id or not self.filename or not self.question:
            raise ValueError("figure specs require an identity, filename, and question")
        if self.route not in {"essential", "annex"}:
            raise ValueError("figure spec route must be essential or annex")
        if self.x_scale not in {"year", "log_cost"} or self.y_scale not in {"linear", "log"}:
            raise ValueError("figure spec scales must use the documented vocabulary")
        if not isinstance(self.rows, tuple):
            raise ValueError("figure spec rows must be a tuple")
        if self.snapshot_date is not None and not self.snapshot_date:
            raise ValueError("snapshot date cannot be empty")
        model_ids = {row.model_id for row in self.rows}
        if not set(self.compact_ids) <= model_ids:
            raise ValueError("compact IDs must identify plotted rows")
        if not set(self.direct_label_ids) <= model_ids:
            raise ValueError("direct label IDs must identify plotted rows")
        if self.route == "essential":
            if len(self.rows) > 15:
                raise ValueError("essential figures may contain at most 15 marks")
            if len(self.direct_label_ids) > 5:
                raise ValueError("essential figures may contain at most five direct labels")

    @property
    def compact_rows(self) -> tuple[FigureRow, ...]:
        """Rows for the compact table, always a subset of the plotted rows."""
        return tuple(row for row in self.rows if row.model_id in self.compact_ids)


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


@dataclass(frozen=True)
class TrainingReplacementScenario:
    as_of: str = "2026-08-18"
    unit_price_low_usd: Decimal = Decimal("20000")
    unit_price_base_usd: Decimal = Decimal("30000")
    unit_price_high_usd: Decimal = Decimal("40000")
    source_ids: tuple[str, ...] = (SCENARIO_SOURCE,)

    def __post_init__(self):
        prices = tuple(
            _positive_finite_decimal(getattr(self, field), "replacement scenario price")
            for field in ("unit_price_low_usd", "unit_price_base_usd", "unit_price_high_usd")
        )
        if not prices[0] <= prices[1] <= prices[2]:
            raise ValueError("replacement scenario prices must be ordered")
        for field, value in zip(
            ("unit_price_low_usd", "unit_price_base_usd", "unit_price_high_usd"), prices
        ):
            object.__setattr__(self, field, value)


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
    cells = {
        "year": model["year"],
        "architecture": model.get("architecture", {}),
        **model.get("metrics", {}),
    }
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
        confidence=overrides.get("confidence", cell_confidence(cell, cells)),
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


def build_training_series(
    ledger: dict,
    replacement_scenario: TrainingReplacementScenario | None = None,
) -> dict[str, list[PlotPoint]]:
    """Build five training series without normalizing unlike hardware units."""
    if replacement_scenario is None:
        raw = ledger.get("dashboard_training_replacement_scenario", {})
        prices = raw.get("unit_price_usd", {})
        replacement_scenario = TrainingReplacementScenario(
            as_of=str(raw.get("as_of", "2026-08-18")),
            unit_price_low_usd=prices.get("low", 20000),
            unit_price_base_usd=prices.get("base", 30000),
            unit_price_high_usd=prices.get("high", 40000),
            source_ids=tuple(raw.get("source_ids", (SCENARIO_SOURCE,))),
        )
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

        # A common 2026 dollar base makes fleet scale comparable without
        # pretending to reconstruct procurement history or hardware parity.
        if _is_positive_cell(count) and count.get("status") == "FACT":
            count_value = _decimal(count["value"])
            sources = tuple(
                dict.fromkeys(
                    (*count.get("source_ids", ()), *replacement_scenario.source_ids)
                )
            )
            series["replacement_value"].append(
                _point(
                    model,
                    count,
                    f"{count['unit']} × common 2026 slot price",
                    TRAINING_REPLACEMENT_SCOPE,
                    value=count_value * replacement_scenario.unit_price_base_usd,
                    low=count_value * replacement_scenario.unit_price_low_usd,
                    high=count_value * replacement_scenario.unit_price_high_usd,
                    unit="USD",
                    status="SCENARIO",
                    source_ids=sources,
                    confidence="not_applicable",
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
            confidence="not_applicable",
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


def _corpus_parts(corpus: dict) -> tuple[dict, dict]:
    """Accept the combined corpus while keeping the view-model pure.

    ``ledger``/``eci`` are the names used by the generator.  The aliases make
    the boundary clear for callers that name their checked-in sources rather
    than their roles.
    """
    if "dashboard_models" in corpus:
        ledger = corpus
        eci = corpus.get("eci")
    else:
        ledger = corpus.get("ledger") or corpus.get("hardware_costs")
        eci = corpus.get("eci") or corpus.get("eci_snapshot")
    if not isinstance(ledger, dict) or not isinstance(eci, dict):
        raise ValueError("dashboard corpus requires ledger and eci mappings")
    return ledger, eci


def _row_from_point(point: PlotPoint, *, x_offset: float = 0.0) -> FigureRow:
    """Convert an existing positive derivation without recalculating it."""
    return FigureRow(
        model_id=point.model_id,
        label=point.label,
        year=point.year,
        low=point.low if point.low is not None else point.value,
        high=point.high if point.high is not None else point.value,
        unit=point.unit,
        status=point.status,
        confidence=point.confidence,
        scope=point.claim_scope,
        source_ids=point.source_ids,
        x_offset=x_offset,
    )


def _temporal_rows(points: Iterable[PlotPoint]) -> tuple[FigureRow, ...]:
    """Sort points and spread ties symmetrically within their exact year."""
    ordered = tuple(_row_from_point(point) for point in _ordered(points))
    return _with_symmetric_offsets(ordered)


def _with_symmetric_offsets(rows: tuple[FigureRow, ...]) -> tuple[FigureRow, ...]:
    """Apply tie offsets after every deterministic selection step."""
    offset_rows = []
    for year in sorted({row.year for row in rows}):
        group = [row for row in rows if row.year == year]
        center = (len(group) - 1) / 2
        for index, row in enumerate(group):
            # A narrow, stable offset prevents overplotting without claiming a
            # different publication year.  It is intentionally not random.
            offset_rows.append(replace(row, x_offset=(index - center) * 0.12))
    return tuple(offset_rows)


def _select_essential_rows(rows: tuple[FigureRow, ...]) -> tuple[FigureRow, ...]:
    """Keep chronological teaching marks within the 15-mark reading limit."""
    return _with_symmetric_offsets(rows[:15])


def _compact_ids(rows: tuple[FigureRow, ...]) -> tuple[str, ...]:
    """Choose the first stable model set that yields four to six table rows."""
    selected: list[str] = []
    for row in rows:
        if row.model_id in selected:
            continue
        candidate = (*selected, row.model_id)
        count = sum(item.model_id in candidate for item in rows)
        if count > 6:
            continue
        selected.append(row.model_id)
        if count >= 4:
            return tuple(selected)
    return tuple(selected)


def _y_scale(rows: tuple[FigureRow, ...]) -> Literal["linear", "log"]:
    """Use log only for positive data spanning at least two orders of magnitude."""
    if not rows:
        return "linear"
    low = min(row.low for row in rows)
    high = max(row.high for row in rows)
    return "log" if low > 0 and high / low >= 100 else "linear"


def _absence_summary(ledger: dict, metric_id: str) -> AbsenceSummary:
    """Count audited negative cells without transforming any into a number."""
    status_keys = {
        "UNDISCLOSED_BY_CREATOR": "UNDISCLOSED",
        "NOT_FOUND": "NOT_FOUND",
        "ESTIMATION_NOT_IDENTIFIABLE": "ESTIMATION_NOT_IDENTIFIABLE",
    }
    counts = {key: 0 for key in status_keys.values()}
    for model in ledger.get("dashboard_models", ()):
        cell = model.get("metrics", {}).get(metric_id, {})
        normalized = status_keys.get(cell.get("status"))
        if normalized:
            counts[normalized] += 1
    return AbsenceSummary(
        metric_id=metric_id,
        counts=counts,
        searched_on=str(ledger.get("cutoff", "unknown")),
    )


def _pareto_rows(ledger: dict, eci: dict) -> tuple[FigureRow, ...]:
    """Build interval Pareto rows from the same capex and ECI bounds we plot."""
    score_by_model = {
        row["benchmark_model_id"]
        : row
        for row in eci.get("models", ())
        if row.get("pareto_eligible")
    }
    model_by_id = {model["id"]: model for model in ledger.get("dashboard_models", ())}
    capex_by_model = {
        point.model_id: point
        for point in build_inference_series(ledger, CapacityScenario())["accelerator_capex_scenario"]
        if point.model_id in score_by_model
    }
    inputs = [
        ParetoPoint(
            model_id=model_id,
            cost_low=point.low if point.low is not None else point.value,
            cost_high=point.high if point.high is not None else point.value,
            score_low=score_by_model[model_id]["score_low"],
            score_high=score_by_model[model_id]["score_high"],
        )
        for model_id, point in capex_by_model.items()
    ]
    frontier = pareto_frontier(inputs)
    safe_ids = set(frontier.safe_ids)
    possible_ids = set(frontier.possible_ids)
    score_source = eci.get("snapshot", {}).get("scores_source_id", "S_EPOCH_ECI_SCORES")
    rows = []
    for point in sorted(inputs, key=lambda item: (item.cost_low, item.model_id)):
        capex = capex_by_model[point.model_id]
        model = model_by_id[point.model_id]
        membership = (
            "safe" if point.model_id in safe_ids else
            "possible" if point.model_id in possible_ids else
            "dominated"
        )
        rows.append(
            FigureRow(
                model_id=point.model_id,
                label="ECI",
                year=int(model["year"]["value"]),
                low=point.score_low,
                high=point.score_high,
                unit="ECI",
                status=capex.status,
                confidence=capex.confidence,
                scope=f"{capex.claim_scope};eci_exact_variant",
                source_ids=tuple(dict.fromkeys((*capex.source_ids, score_source))),
                cost_low=point.cost_low,
                cost_high=point.cost_high,
                frontier=membership,
            )
        )
    return tuple(rows)


def _spec(
    *,
    figure_id: str,
    filename: str,
    route: Literal["essential", "annex"],
    question: str,
    rows: tuple[FigureRow, ...],
    x_scale: Literal["year", "log_cost"] = "year",
    absence: AbsenceSummary | None = None,
    snapshot_date: str | None = None,
) -> FigureSpec:
    if route == "essential" and figure_id != "pareto_inference":
        rows = _select_essential_rows(rows)
    compact_ids = _compact_ids(rows)
    return FigureSpec(
        figure_id=figure_id,
        filename=filename,
        route=route,
        question=question,
        rows=rows,
        compact_ids=compact_ids,
        direct_label_ids=compact_ids[:5],
        x_scale=x_scale,
        y_scale=_y_scale(rows),
        absence=absence,
        snapshot_date=snapshot_date,
    )


def build_figure_specs(corpus: dict) -> tuple[FigureSpec, ...]:
    """Return the deterministic, shared view-model for the nine dashboard views."""
    ledger, eci = _corpus_parts(corpus)
    training = build_training_series(ledger)
    inference = build_inference_series(ledger, CapacityScenario())

    return (
        _spec(
            figure_id="parameters",
            filename="ai-dashboard-parameters.svg",
            route="essential",
            question="¿Cuántos parámetros almacena o activa el modelo?",
            rows=_temporal_rows(training["parameters_total_active"]),
        ),
        _spec(
            figure_id="training_flop",
            filename="ai-dashboard-training-flop.svg",
            route="essential",
            question="¿Cuánto trabajo requirió el entrenamiento?",
            rows=_temporal_rows(training["training_flop"]),
            absence=_absence_summary(ledger, "training_flop"),
        ),
        _spec(
            figure_id="artifact_or_weight_floor",
            filename="ai-dashboard-inference-memory.svg",
            route="essential",
            question="¿Cuánta memoria mínima requieren los pesos?",
            rows=_temporal_rows(inference["artifact_or_weight_floor"]),
            absence=_absence_summary(ledger, "artifact_bytes"),
        ),
        _spec(
            figure_id="h100_capacity_floor",
            filename="ai-dashboard-inference-hardware.svg",
            route="essential",
            question="¿Qué hardware mínimo sugiere ese piso?",
            rows=_temporal_rows(inference["h100_capacity_equivalents"]),
        ),
        _spec(
            figure_id="pareto_inference",
            filename="ai-dashboard-pareto-inference.svg",
            route="essential",
            question="¿Qué opciones quedan en la frontera costo–ECI?",
            rows=_pareto_rows(ledger, eci),
            x_scale="log_cost",
            snapshot_date=str(eci["snapshot"]["as_of"]),
        ),
        _spec(
            figure_id="training_accelerators",
            filename="ai-dashboard-training-accelerators.svg",
            route="annex",
            question="¿Qué flotas concurrentes de entrenamiento están documentadas?",
            rows=_temporal_rows(
                point
                for point in training["accelerators_and_hours"]
                if point.label == "concurrent accelerators"
            ),
            absence=_absence_summary(ledger, "accelerators_concurrent"),
        ),
        _spec(
            figure_id="training_replacement_value",
            filename="ai-dashboard-training-replacement.svg",
            route="annex",
            question="¿Cuál es el valor de reemplazo común de las flotas documentadas?",
            rows=_temporal_rows(training["replacement_value"]),
        ),
        _spec(
            figure_id="inference_tdp_floor",
            filename="ai-dashboard-inference-power.svg",
            route="annex",
            question="¿Qué potencia accelerator-only sugiere el piso de capacidad?",
            rows=_temporal_rows(inference["accelerator_tdp_scenario"]),
        ),
        _spec(
            figure_id="inference_capex_floor",
            filename="ai-dashboard-inference-capex.svg",
            route="annex",
            question="¿Qué CAPEX accelerator-only sugiere el piso de capacidad?",
            rows=_temporal_rows(inference["accelerator_capex_scenario"]),
        ),
    )
