from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from ai_model_dashboard import (
    CapacityScenario,
    ParetoPoint,
    PlotPoint,
    build_inference_series,
    build_training_series,
    pareto_frontier,
)


def metric(status, value=None, unit=None, source_ids=("S_TEST",), **extra):
    cell = {"status": status, "value": value, "source_ids": list(source_ids)}
    if unit is not None:
        cell["unit"] = unit
    cell.update(extra)
    return cell


def sample_ledger():
    missing = metric("UNDISCLOSED_BY_CREATOR")
    return {
        "dashboard_models": [
            {
                "id": "DM_A",
                "canonical_name": "Modelo A",
                "year": metric("DERIVED", "2023", "year"),
                "metrics": {
                    "parameters_total": metric("FACT", 100, "parameter", ("S_A",)),
                    "parameters_active": metric("DERIVED", 80, "parameter_per_token", ("S_A",)),
                    "training_flop": metric("DERIVED", "6e6", "FLOP", ("S_A",), low="5e6", high="7e6"),
                    "accelerators_concurrent": metric("FACT", 4, "H100_GPU", ("S_A",)),
                    "accelerator_hours": metric("FACT", 40, "H100_GPU_hour", ("S_A",)),
                    "accelerator_power_basis": metric("FACT", 700, "W_per_H100_GPU", ("S_A",), basis="configurable_TDP"),
                    "artifact_bytes": metric("FACT", 81_000_000_000, "byte", ("S_ART_A",), precision="BF16"),
                    "weight_floor_bf16": metric("DERIVED", 200, "byte", ("S_A",)),
                    "weight_floor_fp8": metric("DERIVED", 100, "byte", ("S_A",)),
                    "weight_floor_int8": metric("DERIVED", 100, "byte", ("S_A",)),
                    "weight_floor_int4": metric("DERIVED", 50, "byte", ("S_A",)),
                },
            },
            {
                "id": "DM_B",
                "canonical_name": "Modelo B",
                "year": metric("DERIVED", "2022", "year", ("S_B",)),
                "metrics": {
                    "parameters_total": metric("FACT", 50, "parameter", ("S_B",)),
                    "parameters_active": missing,
                    "training_flop": missing,
                    "accelerators_concurrent": missing,
                    "accelerator_hours": missing,
                    "accelerator_power_basis": missing,
                    "artifact_bytes": missing,
                    "weight_floor_bf16": metric("DERIVED", 100, "byte", ("S_B",)),
                    "weight_floor_fp8": metric("DERIVED", 50, "byte", ("S_B",)),
                    "weight_floor_int8": metric("DERIVED", 50, "byte", ("S_B",)),
                    "weight_floor_int4": metric("DERIVED", 25, "byte", ("S_B",)),
                },
            },
        ]
    }


def test_training_series_excludes_missing_and_preserves_native_units():
    series = build_training_series(sample_ledger())

    assert tuple(series) == (
        "parameters_total_active",
        "training_flop",
        "accelerators_and_hours",
        "power_or_energy_envelope",
        "replacement_value",
    )
    assert [(p.model_id, p.label) for p in series["parameters_total_active"]] == [
        ("DM_B", "total"),
        ("DM_A", "active"),
        ("DM_A", "total"),
    ]
    assert [(p.unit, p.value) for p in series["accelerators_and_hours"]] == [
        ("H100_GPU", Decimal("4")),
        ("H100_GPU_hour", Decimal("40")),
    ]
    flop = series["training_flop"][0]
    assert (flop.value, flop.low, flop.high) == (
        Decimal("6e6"), Decimal("5e6"), Decimal("7e6")
    )
    assert all(point.value > 0 for points in series.values() for point in points)


def test_training_power_bases_are_not_combined_and_unsupported_replacement_is_empty():
    series = build_training_series(sample_ledger())

    power = series["power_or_energy_envelope"][0]
    assert (power.value, power.unit, power.label, power.claim_scope) == (
        Decimal("2800"),
        "W",
        "configurable_TDP",
        "accelerator_only_power_envelope_not_measured_wall_energy",
    )
    assert set(power.source_ids) == {"S_A"}
    assert series["replacement_value"] == []


def test_training_power_propagates_estimated_input_ranges():
    ledger = sample_ledger()
    metrics = ledger["dashboard_models"][0]["metrics"]
    metrics["accelerators_concurrent"].update(
        status="ESTIMATE", value=4, low=3, high=5
    )
    metrics["accelerator_power_basis"].update(
        status="ESTIMATE", value=700, low=600, high=800
    )

    point = build_training_series(ledger)["power_or_energy_envelope"][0]

    assert (point.status, point.value, point.low, point.high) == (
        "ESTIMATE", Decimal("2800"), Decimal("1800"), Decimal("4000")
    )


def test_real_training_power_keeps_each_published_basis_separate():
    ledger_path = Path(__file__).parent / "data" / "ai_hardware_costs.yaml"
    ledger = yaml.safe_load(ledger_path.read_text(encoding="utf-8"))

    points = build_training_series(ledger)["power_or_energy_envelope"]

    assert {(point.model_id, point.value, point.label) for point in points} == {
        ("DM_BLOOM_176B", Decimal("153600"), "sum_of_standard_TDP"),
        ("DM_PALM_540B", Decimal("1179648"), "sum_of_measured_max"),
        ("DM_LLAMA31_405B", Decimal("11468800"), "sum_of_configurable_TDP"),
    }
    assert all(point.claim_scope.endswith("not_measured_wall_energy") for point in points)


def test_inference_scenario_is_capacity_floor_not_sla():
    series = build_inference_series(sample_ledger(), CapacityScenario())

    capacity = next(p for p in series["h100_capacity_equivalents"] if p.model_id == "DM_A")
    power = next(p for p in series["accelerator_tdp_scenario"] if p.model_id == "DM_A")
    capex = next(p for p in series["accelerator_capex_scenario"] if p.model_id == "DM_A")
    assert capacity.value == Decimal("2")  # ceil(81 GB / 80 GB)
    assert capacity.claim_scope == "capacity_floor_not_sla"
    selected = next(p for p in series["artifact_or_weight_floor"] if p.model_id == "DM_A")
    assert (selected.value, selected.claim_scope) == (
        Decimal("81000000000"), "artifact_bytes_for_matching_precision"
    )
    assert (power.value, power.status, power.unit) == (Decimal("1400"), "SCENARIO", "W")
    assert (capex.value, capex.status, capex.unit) == (Decimal("60000"), "SCENARIO", "USD")
    assert all(point.claim_scope != "SLA" for points in series.values() for point in points)


def test_inference_precision_selects_floor_and_rejects_unknown_precision():
    series = build_inference_series(sample_ledger(), CapacityScenario(precision="INT4"))
    int4 = series["artifact_or_weight_floor"]
    assert [(point.model_id, point.value, point.label) for point in int4] == [
        ("DM_B", Decimal("25"), "INT4 weight floor"),
        ("DM_A", Decimal("50"), "INT4 weight floor"),
    ]
    capacity = next(p for p in series["h100_capacity_equivalents"] if p.model_id == "DM_A")
    assert capacity.value == Decimal("1")
    assert capacity.source_ids == ("S_A", "S_COURSE_DESIGN")
    with pytest.raises(ValueError, match="precision"):
        CapacityScenario(precision="FP16")


@pytest.mark.parametrize(
    "constructor, kwargs",
    [
        (PlotPoint, dict(model_id="A", year=2024, value=0, unit="FLOP", status="FACT", low=None, high=None, source_ids=("S",), label="x", claim_scope="x")),
        (ParetoPoint, dict(model_id="A", cost_low=0, cost_high=1, score_low=1, score_high=2)),
        (CapacityScenario, dict(hbm_gb=0)),
    ],
)
def test_log_axis_contract_rejects_non_positive_values(constructor, kwargs):
    with pytest.raises(ValueError, match="positive"):
        constructor(**kwargs)


def test_plot_points_require_traceability_and_scope():
    base = dict(
        model_id="A", year=2024, value=1, unit="FLOP", status="FACT",
        low=None, high=None, source_ids=("S_A",), label="training",
        claim_scope="training work",
    )
    for missing_field in ("model_id", "unit", "status", "source_ids", "label", "claim_scope"):
        invalid = dict(base)
        invalid[missing_field] = () if missing_field == "source_ids" else ""
        with pytest.raises(ValueError, match="traceability"):
            PlotPoint(**invalid)


@pytest.mark.parametrize(
    "invalid",
    [
        {"value": Decimal("NaN")},
        {"value": Decimal("Infinity")},
        {"year": 0},
        {"year": "2024"},
        {"source_ids": "S_NOT_A_TUPLE"},
    ],
)
def test_plot_points_reject_non_finite_year_and_string_sources(invalid):
    kwargs = dict(
        model_id="A", year=2024, value=1, unit="FLOP", status="FACT",
        low=None, high=None, source_ids=("S_A",), label="training",
        claim_scope="training work",
    )
    kwargs.update(invalid)
    with pytest.raises(ValueError):
        PlotPoint(**kwargs)


def test_pareto_marks_safe_and_possible_frontiers_without_midpoints():
    result = pareto_frontier([
        ParetoPoint("A", cost_low=10, cost_high=12, score_low=70, score_high=72),
        ParetoPoint("B", cost_low=20, cost_high=22, score_low=69, score_high=71),
        ParetoPoint("C", cost_low=18, cost_high=30, score_low=71, score_high=75),
    ])
    assert result.safe_ids == ("A",)
    assert result.possible_ids == ("A", "C", "B")
    assert set(result.safe_ids) <= set(result.possible_ids)


def test_overlapping_pareto_intervals_can_both_be_possible():
    result = pareto_frontier([
        ParetoPoint("A", 10, 20, 70, 80),
        ParetoPoint("B", 5, 25, 75, 85),
    ])
    assert result.safe_ids == ()
    assert result.possible_ids == ("B", "A")


def test_pareto_strict_ties_overlap_and_permutation_are_stable():
    points = [
        ParetoPoint("TIE_B", 10, 10, 70, 70),
        ParetoPoint("TIE_A", 10, 10, 70, 70),
        ParetoPoint("OVERLAP", 9, 12, 69, 71),
    ]
    forward = pareto_frontier(points)
    reverse = pareto_frontier(list(reversed(points)))
    assert forward == reverse
    assert forward.possible_ids == ("OVERLAP", "TIE_A", "TIE_B")
    assert set(forward.safe_ids) <= set(forward.possible_ids)


def test_pareto_validates_intervals_and_is_deterministic():
    with pytest.raises(ValueError, match="interval"):
        ParetoPoint("bad", cost_low=2, cost_high=1, score_low=3, score_high=4)
    points = [
        ParetoPoint("Z", 20, 20, 80, 80),
        ParetoPoint("A", 10, 10, 70, 70),
    ]
    assert pareto_frontier(points).possible_ids == ("A", "Z")
    with pytest.raises(ValueError, match="unique"):
        pareto_frontier([points[0], points[0]])
