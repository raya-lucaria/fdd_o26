from decimal import Decimal
from pathlib import Path

import pytest
import yaml

from ai_hardware_costs import (
    accelerator_capex,
    accelerator_hours,
    aggregate_peaks,
    bits_to_bytes,
    gb_to_gib,
    gib_to_gb,
    installed_hbm_gb,
    installed_hbm_gib,
    kw_to_mw,
    peak_rate_tflops,
    system_capex,
    watts_to_kw,
    weight_floor_gb,
)


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tools" / "data" / "ai_hardware_costs.yaml"
PAGE = (
    ROOT
    / "course"
    / "3_arquitectura_de_computadoras"
    / "4_ai_escala_y_decision"
    / "0_index.md"
)
ALLOWED = {
    "FACT",
    "DERIVED",
    "ESTIMATE",
    "SCENARIO",
    "UNDISCLOSED_BY_CREATOR",
    "NOT_FOUND",
    "ESTIMATION_NOT_IDENTIFIABLE",
    "NOT_APPLICABLE",
}
POSITIVE = {"FACT", "DERIVED", "ESTIMATE", "SCENARIO"}
NEGATIVE = {
    "UNDISCLOSED_BY_CREATOR",
    "NOT_FOUND",
    "ESTIMATION_NOT_IDENTIFIABLE",
    "NOT_APPLICABLE",
}
REQUIRED_CORPUS = {
    "announcement",
    "model_card",
    "system_card",
    "technical_paper",
    "repository_configuration",
}
REQUIRED_MODELS = {
    "GPT-3 175B",
    "BLOOM 176B",
    "PaLM 540B",
    "Llama 3.1 405B",
    "DeepSeek-V3",
    "GPT-5.6 Sol",
    "Claude Sonnet 5",
    "Gemini 3.1 Pro",
    "Kimi K3",
    "Qwen3.8-Max",
}
PRICE_BASIS_FIELDS = {
    "transaction_unit",
    "minimum_quantity",
    "price_date",
    "geography",
    "currency",
    "condition",
    "channel",
    "taxes",
    "support",
    "network",
    "storage",
    "included_components",
    "excluded_components",
}


def load_yaml(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8"))


def test_training_tables_expose_ledger_ids_for_each_included_case():
    """Dropping an ID would make a displayed training figure untraceable."""
    data = load_yaml(DATA)
    section = PAGE.read_text(encoding="utf-8").split(
        "## Costo físico del hardware", 1
    )[1]

    documented = [
        case for case in data["training_cases"] if case["include_in_documented_table"]
    ]
    assert documented
    for case in documented:
        assert case["id"] in section
        assert case["model_id"] in section
        for field in (
            "accelerators_concurrent",
            "accelerator_hours",
            "hbm_physical_installed",
            "accelerator_power",
            "attributed_training_capex",
        ):
            cell = case["metrics"][field]
            assert cell["status"] in section
            for source_id in cell.get("source_ids", []):
                assert source_id in section


def test_training_scenario_is_unattributed_and_uses_the_ledger_valuation():
    """Attaching the didactic valuation to a model would turn a scenario into fact."""
    data = load_yaml(DATA)
    section = PAGE.read_text(encoding="utf-8").split(
        "### Escenarios equivalentes, no entrenamientos atribuidos", 1
    )[1]
    valuation = next(
        item
        for item in data["valuations"]
        if item["id"] == "V_H100_30K_DIDACTIC_SCENARIO"
    )

    assert valuation["id"] in section
    assert "Sin modelo atribuido" in section
    assert "SCENARIO" in section
    assert "Thinkmate" not in section


def test_ledger_has_cutoff_and_cell_level_evidence():
    data = load_yaml(DATA)

    assert data["cutoff"] == "2026-08-18"
    assert {
        "sources",
        "hardware",
        "models",
        "training_cases",
        "inference_scenarios",
        "valuations",
    } <= data.keys()
    for case in data["training_cases"]:
        for field in case["metrics"].values():
            assert field["status"] in ALLOWED
            assert field.get("source_ids") or field["status"] in {
                "NOT_FOUND",
                "ESTIMATION_NOT_IDENTIFIABLE",
                "NOT_APPLICABLE",
            }


def evidence_cells(value):
    if isinstance(value, dict):
        if "status" in value:
            yield value
        for child in value.values():
            yield from evidence_cells(child)
    elif isinstance(value, list):
        for child in value:
            yield from evidence_cells(child)


def test_all_evidence_cells_resolve_sources_and_explain_absence():
    data = load_yaml(DATA)
    source_ids = set(data["sources"])

    for cell in evidence_cells(data):
        assert cell["status"] in ALLOWED
        assert set(cell.get("source_ids", [])) <= source_ids
        if cell["status"] in POSITIVE:
            assert cell.get("source_ids")
            assert cell.get("value") is not None
            assert cell.get("unit")
        elif cell["status"] == "UNDISCLOSED_BY_CREATOR":
            assert cell.get("source_ids")
            assert cell.get("value") is None
        elif cell["status"] == "NOT_FOUND":
            assert cell.get("searched_on") == data["cutoff"]
            assert cell.get("corpus_checked")
            assert all(
                reference in source_ids
                or (
                    isinstance(reference, str)
                    and reference.startswith(("https://", "http://"))
                )
                for reference in cell["corpus_checked"]
            )
            assert any(
                reference in source_ids for reference in cell["corpus_checked"]
            )
            assert cell.get("value") is None
        elif cell["status"] == "ESTIMATION_NOT_IDENTIFIABLE":
            assert cell.get("missing_observables")
            assert cell.get("value") is None
        elif cell["status"] == "NOT_APPLICABLE":
            assert cell.get("note")
            assert cell.get("value") is None


def test_minimum_corpus_and_current_model_audits_are_present():
    data = load_yaml(DATA)
    models = {model["canonical_name"]: model for model in data["models"]}

    assert REQUIRED_MODELS <= models.keys()
    for model in models.values():
        assert model["id"].startswith("M_")
        assert REQUIRED_CORPUS == model["corpus"].keys()
        assert {
            "canonical_name",
            "release_date",
            "availability",
            "region",
        } <= model["facts"].keys()


def test_documented_training_requires_same_scope_observables():
    data = load_yaml(DATA)

    for case in data["training_cases"]:
        metrics = case["metrics"]
        if not case["include_in_documented_table"]:
            continue
        assert metrics["hardware_type"]["status"] == "FACT"
        assert metrics["accelerators_concurrent"]["status"] == "FACT"
        assert metrics["accelerator_hours"]["status"] in {"FACT", "DERIVED"} or metrics[
            "duration_hours"
        ]["status"] in {"FACT", "DERIVED"}
        scope = case["scope"]
        for name in ("hardware_type", "accelerators_concurrent"):
            assert metrics[name]["scope"] == scope
        measured_time = [
            metrics[name]
            for name in ("accelerator_hours", "duration_hours")
            if metrics[name]["status"] in {"FACT", "DERIVED"}
        ]
        assert measured_time
        assert all(field["scope"] == scope for field in measured_time)


def test_closed_current_models_do_not_receive_attributed_estimates():
    data = load_yaml(DATA)
    current_closed = {
        case["model_id"]: case
        for case in data["training_cases"]
        if case["category"] == "current_closed"
    }

    assert current_closed
    for case in current_closed.values():
        assert not case["include_in_documented_table"]
        assert (
            case["metrics"]["attributed_training_capex"]["status"]
            == "ESTIMATION_NOT_IDENTIFIABLE"
        )
        assert all(
            field["status"] != "ESTIMATE" for field in case["metrics"].values()
        )


def test_valuations_declare_complete_price_basis_and_one_boundary():
    data = load_yaml(DATA)

    def basis_value(value):
        return value.get("value") if isinstance(value, dict) else value

    assert data["valuations"]
    for valuation in data["valuations"]:
        assert valuation["id"].startswith("V_")
        assert valuation["boundary"] in {"accelerator-only", "system-based"}
        assert PRICE_BASIS_FIELDS <= valuation["price_basis"].keys()
        assert valuation["price"]["unit"] == basis_value(
            valuation["price_basis"]["currency"]
        )
        assert basis_value(valuation["price_basis"]["channel"]) not in {
            "api",
            "cloud_rental",
            "accelerator_hour_rental",
        }
        if valuation["boundary"] == "accelerator-only":
            assert basis_value(valuation["price_basis"]["transaction_unit"]) in {
                "card",
                "module",
            }
        else:
            assert basis_value(valuation["price_basis"]["transaction_unit"]) in {
                "server",
                "rack",
            }
            excluded = basis_value(valuation["price_basis"]["excluded_components"])
            assert "accelerators_already_inside_system" in excluded


def test_primary_sources_are_owned_by_the_applicable_claimant():
    data = load_yaml(DATA)
    sources = data["sources"]

    def assert_support(cell, allowed_tags, allowed_owners, required_owners=()):
        referenced = [sources[source_id] for source_id in cell["source_ids"]]
        assert referenced
        assert all(source["source_class"] == "primary" for source in referenced)
        assert all(source["claim_owner"] in allowed_owners for source in referenced)
        assert all(set(source["primary_for"]) & allowed_tags for source in referenced)
        owners = {source["claim_owner"] for source in referenced}
        assert set(required_owners) <= owners

    model_claim_tags = {
        "canonical_name": {"canonical_name"},
        "release_date": {"release"},
        "availability": {"availability"},
        "service_availability": {"availability"},
        "region": {"region"},
        "parameters_total": {"parameters"},
        "parameters_active": {"parameters"},
        "open_weight_artifact": {"open_weight_artifact"},
        "artifact_release_date": {"artifact_release"},
    }
    corpus_claim_tags = {
        "announcement": {"announcement_audit"},
        "model_card": {"model_card_audit"},
        "system_card": {"system_card_audit"},
        "technical_paper": {"technical_paper_audit"},
        "repository_configuration": {"repository_configuration"},
    }
    hardware_claim_tags = {
        "hbm_physical": {"hbm_physical"},
        "hbm_usable": {"hbm_usable"},
        "peak_theoretical_rate": {"peak_theoretical_rate"},
        "accelerator_power": {"accelerator_power"},
    }
    training_claim_tags = {
        "parameters_total": {"parameters"},
        "parameters_active": {"parameters"},
        "training_tokens": {"training_tokens"},
        "hardware_type": {"training_hardware"},
        "accelerators_concurrent": {"training_hardware"},
        "accelerator_hours": {"accelerator_hours", "training_duration"},
        "duration_hours": {"training_duration"},
        "reported_duration_bound": {"training_duration"},
        "training_precision": {"training_precision"},
        "training_compute_flop": {"training_compute"},
        "mfu": {"mfu"},
        "hbm_physical_installed": {"training_hardware", "hbm_physical"},
        "peak_theoretical_rate": {"training_hardware", "peak_theoretical_rate"},
        "accelerator_power": {"training_hardware", "accelerator_power"},
        "historical_acquisition_price": {"historical_acquisition_price"},
        "attributed_training_capex": {"attributed_training_capex"},
    }

    for model in data["models"]:
        for name, cell in model["facts"].items():
            if cell["status"] in POSITIVE:
                assert_support(
                    cell, model_claim_tags[name], {"model_creator"}, {"model_creator"}
                )
        for name, cell in model["corpus"].items():
            if cell["status"] in POSITIVE:
                assert_support(
                    cell,
                    corpus_claim_tags[name],
                    {"model_creator"},
                    {"model_creator"},
                )

    for hardware in data["hardware"]:
        for name, cell in hardware["specs"].items():
            if cell["status"] in POSITIVE:
                assert_support(
                    cell,
                    hardware_claim_tags[name],
                    {"hardware_manufacturer"},
                    {"hardware_manufacturer"},
                )

    hardware_derived = {
        "hbm_physical_installed",
        "peak_theoretical_rate",
        "accelerator_power",
    }
    for case in data["training_cases"]:
        for name, cell in case["metrics"].items():
            if cell["status"] not in {"FACT", "DERIVED"}:
                continue
            if name == "historical_acquisition_price":
                assert_support(
                    cell,
                    training_claim_tags[name],
                    {"seller", "purchase_record"},
                )
            elif name == "attributed_training_capex":
                assert_support(
                    cell,
                    training_claim_tags[name],
                    {"seller", "purchase_record", "model_creator"},
                )
            elif name in hardware_derived and cell["status"] == "DERIVED":
                assert_support(
                    cell,
                    training_claim_tags[name],
                    {"model_creator", "hardware_manufacturer"},
                    {"model_creator", "hardware_manufacturer"},
                )
            else:
                assert_support(
                    cell,
                    training_claim_tags[name],
                    {"model_creator"},
                    {"model_creator"},
                )

    for scenario in data["inference_scenarios"]:
        for cell in scenario["metrics"].values():
            if cell["status"] == "SCENARIO":
                referenced = [sources[source_id] for source_id in cell["source_ids"]]
                assert all(source["claim_owner"] == "course_design" for source in referenced)
                assert all(
                    source["source_class"] == "binding_specification"
                    for source in referenced
                )
                assert all("inference_target" in source["primary_for"] for source in referenced)

    for valuation in data["valuations"]:
        price = valuation["price"]
        if price["status"] == "FACT":
            assert_support(
                price, {"replacement_price"}, {"seller", "purchase_record"}
            )
        elif price["status"] == "SCENARIO":
            referenced = [sources[source_id] for source_id in price["source_ids"]]
            assert all(source["claim_owner"] == "course_design" for source in referenced)
            assert all("didactic_scenarios" in source["primary_for"] for source in referenced)
        basis_claim_tags = {
            "transaction_unit": {"transaction_unit"},
            "minimum_quantity": {"minimum_quantity"},
            "price_date": {"scope_rules"},
            "geography": {"geography"},
            "currency": {"currency"},
            "condition": {"condition"},
            "channel": {"channel"},
            "taxes": {"taxes"},
            "support": {"support"},
            "network": {"network"},
            "storage": {"storage"},
            "included_components": {"included_components"},
            "excluded_components": {"scope_rules"},
        }
        for name, cell in valuation["price_basis"].items():
            if not isinstance(cell, dict) or cell.get("status") not in POSITIVE:
                continue
            if cell["status"] == "FACT":
                assert_support(
                    cell,
                    basis_claim_tags[name],
                    {"seller", "purchase_record"},
                )
            elif cell["status"] == "SCENARIO":
                referenced = [sources[source_id] for source_id in cell["source_ids"]]
                assert all(
                    source["claim_owner"] == "course_design" for source in referenced
                )
                assert all(
                    source["source_class"] == "binding_specification"
                    for source in referenced
                )
                assert all(
                    set(source["primary_for"]) & basis_claim_tags[name]
                    for source in referenced
                )


def test_fact_prices_have_persistent_transaction_evidence():
    data = load_yaml(DATA)

    for valuation in data["valuations"]:
        if valuation["price"]["status"] != "FACT":
            continue
        price_sources = [
            data["sources"][source_id]
            for source_id in valuation["price"]["source_ids"]
        ]
        assert any(source.get("persistent_evidence") for source in price_sources)


def test_qwen_service_and_open_base_artifact_are_separate_models():
    data = load_yaml(DATA)
    models = {model["id"]: model for model in data["models"]}
    service = models["M_QWEN38_MAX_SERVICE"]
    artifact = models["M_QWEN38_2_4T_A95B"]
    cases = {case["model_id"]: case for case in data["training_cases"]}

    assert service["canonical_name"] == "Qwen3.8-Max"
    assert service["source_ids"] == ["S_QWEN38_ANNOUNCEMENT"]
    assert service["facts"]["availability"]["value"] == "hosted_on_QwenCloud"
    assert "open_weight_artifact" not in service["facts"]

    assert artifact["canonical_name"] == "Qwen3.8-2.4T-A95B"
    assert artifact["facts"]["availability"]["value"] == "open_weights"
    assert artifact["facts"]["release_date"]["value"] == "2026-08-12"
    assert artifact["corpus"]["model_card"]["source_ids"] == [
        "S_QWEN38_MODELSCOPE"
    ]
    assert artifact["corpus"]["repository_configuration"]["status"] == "FACT"
    assert artifact["corpus"]["repository_configuration"]["source_ids"] == [
        "S_QWEN38_MODELSCOPE"
    ]

    assert cases["M_QWEN38_MAX_SERVICE"]["category"] == "current_closed"
    assert cases["M_QWEN38_2_4T_A95B"]["category"] == "current_open"
    assert cases["M_QWEN38_2_4T_A95B"]["scope"] == (
        "Qwen3_8_2_4T_A95B_base_training"
    )


def test_unpersisted_thinkmate_configuration_has_no_unqualified_claims():
    data = load_yaml(DATA)
    valuation = next(
        item
        for item in data["valuations"]
        if item["id"] == "V_THINKMATE_QH14_H100_REPLACEMENT_20260818"
    )

    assert all(
        isinstance(cell, dict) and "status" in cell
        for cell in valuation["price_basis"].values()
    )

    for field in ("taxes", "support", "network", "storage", "included_components"):
        cell = valuation["price_basis"][field]
        assert cell["status"] == "ESTIMATION_NOT_IDENTIFIABLE"
        assert cell["value"] is None
        assert cell["missing_observables"]

    excluded = valuation["price_basis"]["excluded_components"]
    assert excluded["status"] == "SCENARIO"
    assert excluded["source_ids"] == ["S_COURSE_DESIGN"]
    assert "accelerators_already_inside_system" in excluded["value"]
    assert all("ConnectX" not in str(value) for value in valuation["price_basis"].values())

    supported = {
        "transaction_unit": "server",
        "geography": "United_States_online_storefront",
        "currency": "USD",
        "channel": "seller_online_configurator",
    }
    for field, expected in supported.items():
        cell = valuation["price_basis"][field]
        assert cell["status"] == "FACT"
        assert cell["value"] == expected
        assert cell["source_ids"] == ["S_THINKMATE_HGX_H100_CONFIGURATOR"]

    for field in ("minimum_quantity", "condition"):
        assert valuation["price_basis"][field]["status"] == (
            "ESTIMATION_NOT_IDENTIFIABLE"
        )

    assert valuation["price_basis"]["price_date"]["status"] == "SCENARIO"


def test_power_evidence_preserves_basis_and_boundary():
    data = load_yaml(DATA)
    allowed_hardware_bases = {
        "configurable_TDP",
        "maximum_power_consumption",
        "standard_TDP",
        "measured_max",
    }
    allowed_aggregate_bases = {
        "sum_of_configurable_TDP",
        "sum_of_maximum_power_consumption",
        "sum_of_standard_TDP",
        "sum_of_measured_max",
    }

    for hardware in data["hardware"]:
        assert "nominal_power" not in hardware["specs"]
        power = hardware["specs"]["accelerator_power"]
        if power["status"] in POSITIVE:
            assert power["power_basis"] in allowed_hardware_bases
            assert power["boundary"] in {"accelerator_chip", "accelerator_module"}

    for case in data["training_cases"]:
        assert "nominal_accelerator_power" not in case["metrics"]
        power = case["metrics"]["accelerator_power"]
        if power["status"] in POSITIVE:
            assert power["power_basis"] in allowed_aggregate_bases
            assert power["boundary"] == "accelerator-only"


def test_eight_accelerator_example_preserves_each_quantity_boundary():
    """A wrong multiplier would break the physical example students reconstruct."""
    assert installed_hbm_gb(8, 80) == Decimal("640")
    assert accelerator_hours(8, 24) == Decimal("192")
    assert accelerator_capex(8, 30_000) == Decimal("240000")


def test_system_capex_counts_each_component_once():
    """Adding each network component once prevents an accidental double count."""
    network = [(2, Decimal("12000")), (1, Decimal("8000"))]
    assert system_capex(
        4,
        Decimal("400000"),
        network,
        price_basis={
            "boundary": "system-based",
            "transaction_unit": "server",
            "network": "excluded",
        },
    ) == Decimal("1632000")


def test_mixed_peak_conventions_are_rejected_before_values_are_aggregated():
    """Changing precision must not produce a single comparable peak series."""
    with pytest.raises(ValueError, match="homogeneous peak convention"):
        aggregate_peaks([{"precision": "BF16"}, {"precision": "FP8"}])


def test_peak_rate_requires_complete_dense_precision_and_accumulation_convention():
    """Omitting sparsity could silently mix dense and sparse manufacturer peaks."""
    with pytest.raises(ValueError, match="sparsity"):
        peak_rate_tflops(
            8,
            Decimal("312"),
            {"precision": "BF16", "accumulation": "FP32"},
        )


def test_aggregate_peaks_rejects_different_hardware_even_when_precision_matches():
    """Per-chip peak values are only additive for homogeneous hardware."""
    entries = [
        {
            "hardware_id": "A100-SXM-80GB",
            "precision": "BF16",
            "sparsity": "dense",
            "accumulation": "FP32",
            "tflops": Decimal("312"),
        },
        {
            "hardware_id": "H100-SXM-80GB",
            "precision": "BF16",
            "sparsity": "dense",
            "accumulation": "FP32",
            "tflops": Decimal("989.5"),
        },
    ]
    with pytest.raises(ValueError, match="homogeneous hardware"):
        aggregate_peaks(entries)


def test_aggregate_peaks_adds_only_one_homogeneous_peak_series():
    """Dropping an entry would understate a peak series with compatible conventions."""
    entries = [
        {
            "hardware_id": "A100-SXM-80GB",
            "precision": "BF16",
            "sparsity": "dense",
            "accumulation": "FP32",
            "tflops": Decimal("312"),
        },
        {
            "hardware_id": "A100-SXM-80GB",
            "precision": "BF16",
            "sparsity": "dense",
            "accumulation": "FP32",
            "tflops": Decimal("312"),
        },
    ]
    assert aggregate_peaks(entries) == Decimal("624")


def test_weight_floor_uses_decimal_gb_and_never_binary_gib_implicitly():
    """Treating GB as GiB changes the reported floor without a visible unit change."""
    assert weight_floor_gb(Decimal("35e9"), 8) == Decimal("35")
    assert installed_hbm_gib(8, 80) == Decimal("640")
    assert gb_to_gib(Decimal("14")) == Decimal("13.03851604461669921875")
    assert gib_to_gb(Decimal("13.03851604461669921875")) == Decimal("14")


def test_unit_conversions_keep_power_energy_bits_and_accelerator_time_distinct():
    """Changing a divisor or labeling accelerator-hours as energy is a category error."""
    assert watts_to_kw(1000) == Decimal("1")
    assert kw_to_mw(1000) == Decimal("1")
    assert bits_to_bytes(32) == Decimal("4")
    with pytest.raises(ValueError, match="accelerator-hours are not kWh"):
        accelerator_hours(8, 24, unit="kWh")


def test_capex_boundaries_reject_a_system_price_as_an_accelerator_price():
    """Adding a server price under accelerator-only would double count its GPUs."""
    with pytest.raises(ValueError, match="accelerator-only"):
        accelerator_capex(
            8,
            Decimal("30000"),
            price_basis={"boundary": "system-based", "transaction_unit": "server"},
        )


def test_system_boundary_requires_network_outside_the_system_price():
    """A network item already included in a server price must not be added again."""
    with pytest.raises(ValueError, match="network_parts"):
        system_capex(
            1,
            Decimal("400000"),
            [(1, Decimal("12000"))],
            price_basis={
                "boundary": "system-based",
                "transaction_unit": "server",
                "network_included": True,
            },
        )


def test_negative_quantities_and_prices_are_rejected():
    """A negative accelerator, HBM, or price would make a physical total nonsensical."""
    with pytest.raises(ValueError, match="non-negative"):
        installed_hbm_gb(-1, 80)
    with pytest.raises(ValueError, match="non-negative"):
        accelerator_capex(1, Decimal("-1"))
    with pytest.raises(ValueError, match="non-negative"):
        weight_floor_gb(Decimal("1e9"), -8)


def test_system_capex_reads_canonical_network_basis_before_adding_parts():
    """Ignoring the ledger's network field would double count included network."""
    with pytest.raises(ValueError, match="network_parts"):
        system_capex(
            1,
            Decimal("400000"),
            [(1, Decimal("12000"))],
            price_basis={
                "boundary": "system-based",
                "transaction_unit": "server",
                "network": "included",
            },
        )


def test_system_capex_requires_a_network_basis_when_adding_network_parts():
    """Unknown network inclusion cannot establish the system CAPEX boundary."""
    with pytest.raises(ValueError, match="price_basis"):
        system_capex(1, Decimal("400000"), [(1, Decimal("12000"))])


def test_aggregate_peaks_normalizes_convention_strings_before_comparing():
    """Whitespace alone must not split an otherwise homogeneous peak series."""
    entries = [
        {
            "hardware_id": "A100-SXM-80GB",
            "precision": " BF16 ",
            "sparsity": " dense ",
            "accumulation": " FP32 ",
            "tflops": Decimal("312"),
        },
        {
            "hardware_id": "A100-SXM-80GB",
            "precision": "BF16",
            "sparsity": "dense",
            "accumulation": "FP32",
            "tflops": Decimal("312"),
        },
    ]
    assert aggregate_peaks(entries) == Decimal("624")


def test_aggregate_peaks_rejects_unhashable_convention_values_as_value_errors():
    """A malformed convention must not escape as a set/hash implementation error."""
    entries = [
        {
            "hardware_id": "A100-SXM-80GB",
            "precision": ["BF16"],
            "sparsity": "dense",
            "accumulation": "FP32",
            "tflops": Decimal("312"),
        }
    ]
    with pytest.raises(ValueError, match="peak convention requires precision"):
        aggregate_peaks(entries)


def test_peak_rate_calculates_one_complete_theoretical_rate_series():
    """Using a rate as if it were work would require a different, forbidden calculation."""
    assert peak_rate_tflops(
        8,
        Decimal("312"),
        {"precision": "BF16", "sparsity": "dense", "accumulation": "FP32"},
    ) == Decimal("2496")


@pytest.mark.parametrize(
    ("call", "invalid"),
    [
        (lambda value: installed_hbm_gb(1, value), 0.5),
        (
            lambda value: peak_rate_tflops(
                1,
                value,
                {"precision": "BF16", "sparsity": "dense", "accumulation": "FP32"},
            ),
            0.5,
        ),
        (
            lambda value: aggregate_peaks(
                [
                    {
                        "hardware_id": "A100-SXM-80GB",
                        "precision": "BF16",
                        "sparsity": "dense",
                        "accumulation": "FP32",
                        "tflops": value,
                    }
                ]
            ),
            0.5,
        ),
        (lambda value: accelerator_hours(1, value), 0.5),
        (lambda value: accelerator_capex(1, value), 0.5),
        (
            lambda value: system_capex(
                1,
                value,
                [],
                price_basis={
                    "boundary": "system-based",
                    "transaction_unit": "server",
                    "network": "excluded",
                },
            ),
            0.5,
        ),
        (lambda value: weight_floor_gb(value, 8), 0.5),
    ],
)
def test_calculation_interfaces_reject_binary_floats(call, invalid):
    """Accepting a float would silently inject binary rounding into a Decimal ledger."""
    with pytest.raises(TypeError, match="not float"):
        call(invalid)


@pytest.mark.parametrize("invalid", [Decimal("NaN"), Decimal("Infinity")])
@pytest.mark.parametrize(
    "call",
    [
        lambda value: installed_hbm_gb(1, value),
        lambda value: peak_rate_tflops(
            1,
            value,
            {"precision": "BF16", "sparsity": "dense", "accumulation": "FP32"},
        ),
        lambda value: aggregate_peaks(
            [
                {
                    "hardware_id": "A100-SXM-80GB",
                    "precision": "BF16",
                    "sparsity": "dense",
                    "accumulation": "FP32",
                    "tflops": value,
                }
            ]
        ),
        lambda value: accelerator_hours(1, value),
        lambda value: accelerator_capex(1, value),
        lambda value: system_capex(
            1,
            value,
            [],
            price_basis={
                "boundary": "system-based",
                "transaction_unit": "server",
                "network": "excluded",
            },
        ),
        lambda value: weight_floor_gb(value, 8),
        lambda value: bits_to_bytes(value),
    ],
)
def test_decimal_interfaces_reject_non_finite_values(call, invalid):
    """NaN and infinity cannot represent a physical quantity or price."""
    with pytest.raises(ValueError, match="finite"):
        call(invalid)
