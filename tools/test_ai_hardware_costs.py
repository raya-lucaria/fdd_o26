from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tools" / "data" / "ai_hardware_costs.yaml"
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

    assert data["valuations"]
    for valuation in data["valuations"]:
        assert valuation["id"].startswith("V_")
        assert valuation["boundary"] in {"accelerator-only", "system-based"}
        assert PRICE_BASIS_FIELDS <= valuation["price_basis"].keys()
        assert valuation["price"]["unit"] == valuation["price_basis"]["currency"]
        assert valuation["price_basis"]["channel"] not in {
            "api",
            "cloud_rental",
            "accelerator_hour_rental",
        }
        if valuation["boundary"] == "accelerator-only":
            assert valuation["price_basis"]["transaction_unit"] in {"card", "module"}
        else:
            assert valuation["price_basis"]["transaction_unit"] in {"server", "rack"}
            assert "accelerators_already_inside_system" in valuation["price_basis"][
                "excluded_components"
            ]


def test_primary_sources_are_owned_by_the_applicable_claimant():
    data = load_yaml(DATA)
    sources = data["sources"]

    def owners(cell):
        return {sources[source_id]["claim_owner"] for source_id in cell["source_ids"]}

    def source_classes(cell):
        return {sources[source_id]["source_class"] for source_id in cell["source_ids"]}

    for model in data["models"]:
        for cell in model["facts"].values():
            if cell["status"] in POSITIVE:
                assert owners(cell) == {"model_creator"}
                assert source_classes(cell) == {"primary"}
        for cell in model["corpus"].values():
            if cell["status"] in POSITIVE:
                assert owners(cell) == {"model_creator"}
                assert source_classes(cell) == {"primary"}

    for hardware in data["hardware"]:
        for cell in hardware["specs"].values():
            if cell["status"] in POSITIVE:
                assert owners(cell) == {"hardware_manufacturer"}
                assert source_classes(cell) == {"primary"}

    hardware_derived = {
        "hbm_physical_installed",
        "peak_theoretical_rate",
        "accelerator_power",
    }
    for case in data["training_cases"]:
        for name, cell in case["metrics"].items():
            if cell["status"] == "FACT":
                assert "model_creator" in owners(cell)
                assert source_classes(cell) == {"primary"}
            elif cell["status"] == "DERIVED":
                assert "model_creator" in owners(cell)
                assert source_classes(cell) == {"primary"}
                if name in hardware_derived:
                    assert "hardware_manufacturer" in owners(cell)

    for scenario in data["inference_scenarios"]:
        for cell in scenario["metrics"].values():
            if cell["status"] == "SCENARIO":
                assert owners(cell) == {"course_design"}
                assert source_classes(cell) == {"binding_specification"}

    for valuation in data["valuations"]:
        for cell in evidence_cells(valuation):
            if cell["status"] == "FACT":
                assert owners(cell) == {"seller"}
                assert source_classes(cell) == {"primary"}
            elif cell["status"] == "SCENARIO":
                assert owners(cell) == {"course_design"}
                assert source_classes(cell) == {"binding_specification"}


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


def test_qwen_service_and_open_base_artifact_are_not_conflated():
    data = load_yaml(DATA)
    qwen = next(model for model in data["models"] if model["id"] == "M_QWEN38_MAX")
    qwen_case = next(
        case for case in data["training_cases"] if case["model_id"] == qwen["id"]
    )

    assert qwen["facts"]["availability"]["value"] == (
        "hosted_Qwen3.8-Max_with_open_Qwen3.8-2.4T-A95B_base_artifact"
    )
    assert qwen["facts"]["service_availability"]["value"] == (
        "Qwen3.8-Max_on_QwenCloud"
    )
    assert qwen["facts"]["open_weight_artifact"]["value"] == (
        "Qwen3.8-2.4T-A95B"
    )
    assert qwen["facts"]["artifact_release_date"]["value"] == "2026-08-12"
    assert qwen["corpus"]["model_card"]["scope"] == (
        "Qwen3.8-2.4T-A95B_open_base_artifact"
    )
    assert qwen_case["category"] == "current_open"
    assert not qwen_case["include_in_documented_table"]


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
