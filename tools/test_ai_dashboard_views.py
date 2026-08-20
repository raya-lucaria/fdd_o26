from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from ai_model_dashboard import ParetoPoint, build_figure_specs, pareto_frontier


ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def corpus():
    return {
        "ledger": yaml.safe_load(
            (ROOT / "tools/data/ai_hardware_costs.yaml").read_text(encoding="utf-8")
        ),
        "eci": yaml.safe_load(
            (ROOT / "tools/data/eci_snapshot_2026-08-18.yaml").read_text(
                encoding="utf-8"
            )
        ),
    }


def spec_by_id(specs, figure_id):
    return next(spec for spec in specs if spec.figure_id == figure_id)


def test_figure_specs_define_five_essential_and_four_optional(corpus):
    """Removing a teaching view must fail before the renderer can omit it."""
    specs = build_figure_specs(corpus)

    assert len(specs) == 9
    assert sum(spec.route == "essential" for spec in specs) == 5
    assert sum(spec.route == "annex" for spec in specs) == 4
    assert all(4 <= len(spec.compact_rows) <= 6 for spec in specs if spec.route == "essential")


def test_figure_rows_preserve_exact_decimal_bounds_from_ledger(corpus):
    """The view model must not round large integers before audit-table output."""
    flop = spec_by_id(build_figure_specs(corpus), "training_flop")
    source = {
        model["id"]: model["metrics"]["training_flop"]
        for model in corpus["ledger"]["dashboard_models"]
    }

    for row in flop.rows:
        cell = source[row.model_id]
        expected_low = Decimal(str(cell.get("low", cell["value"])))
        expected_high = Decimal(str(cell.get("high", cell["value"])))
        assert isinstance(row.low, Decimal)
        assert isinstance(row.high, Decimal)
        assert (row.low, row.high) == (expected_low, expected_high)

    t5 = next(row for row in flop.rows if row.model_id == "DM_T5_11B")
    assert t5.low == t5.high == Decimal("66000000000000000000000")


def test_missing_training_compute_is_not_a_zero_mark(corpus):
    """Turning a missing training-compute cell into a plotted zero is a bug."""
    spec = spec_by_id(build_figure_specs(corpus), "training_flop")

    assert all(row.low > 0 for row in spec.rows)
    assert spec.absence.counts["UNDISCLOSED"] > 0


def test_essential_rows_are_bounded_and_compact_rows_are_real_rows(corpus):
    """A compact table must reuse plotted rows and essentials must stay readable."""
    specs = build_figure_specs(corpus)

    for spec in specs:
        if spec.route == "essential":
            assert len(spec.rows) <= 15
            assert len(spec.direct_label_ids) <= 5
        assert set(spec.compact_rows) <= set(spec.rows)


def test_temporal_selection_and_offsets_are_permutation_stable(corpus):
    """Reordering YAML models must not randomize the selected teaching marks."""
    original = build_figure_specs(corpus)
    reordered = {
        **corpus,
        "ledger": {
            **corpus["ledger"],
            "dashboard_models": list(reversed(corpus["ledger"]["dashboard_models"])),
        },
    }

    assert build_figure_specs(reordered) == original
    for spec in original:
        if spec.x_scale == "year":
            for year in {row.year for row in spec.rows}:
                offsets = [row.x_offset for row in spec.rows if row.year == year]
                assert sum(offsets) == pytest.approx(0)


def test_pareto_rows_reconstruct_frontier_from_their_bounds(corpus):
    """A frontier badge must be derived from the exact plotted uncertainty bounds."""
    spec = spec_by_id(build_figure_specs(corpus), "pareto_inference")

    frontier = pareto_frontier([
        ParetoPoint(
            row.model_id,
            cost_low=row.cost_low,
            cost_high=row.cost_high,
            score_low=row.low,
            score_high=row.high,
        )
        for row in spec.rows
    ])
    expected = {
        model_id: "safe" for model_id in frontier.safe_ids
    } | {
        model_id: "possible" for model_id in frontier.possible_ids
        if model_id not in frontier.safe_ids
    }

    assert len(spec.rows) == 8
    assert {row.frontier for row in spec.rows} == {"safe", "possible", "dominated"}
    assert all(row.cost_low > 0 and row.cost_low <= row.cost_high for row in spec.rows)
    assert {
        row.model_id: row.frontier for row in spec.rows
    } == {
        row.model_id: expected.get(row.model_id, "dominated") for row in spec.rows
    }
