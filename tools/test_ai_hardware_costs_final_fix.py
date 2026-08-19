from decimal import Decimal
import importlib.util
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "tools/data/ai_hardware_costs.yaml"
PAGE = ROOT / "course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/0_index.md"
GENERATOR = ROOT / "tools/gen_ai_hardware_costs.py"


def data():
    return yaml.safe_load(DATA.read_text(encoding="utf-8"))


def generator():
    spec = importlib.util.spec_from_file_location("final_fix_generator", GENERATOR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_math_conventions_are_comparable_and_explicit():
    ledger = data()
    charts = {item["id"]: item for item in generator().load_chart_metadata(DATA)}
    power = charts["power"]
    assert len(power["panels"]) == 4
    assert len({row["panel"] for row in power["rows"]}) == 4
    assert len({row["power_basis"] for row in power["points"]}) == len(power["points"])
    assert all("no es consumo medido" not in panel for panel in power["panels"])
    hbm = charts["physical_hbm"]
    for row in hbm["points"]:
        expected = Decimal(str(row["value"])) * (Decimal(2) ** 30 if row["native_unit"] == "GiB" else Decimal(10) ** 9)
        assert Decimal(str(row["canonical_bytes"])) == expected
    peak = next(h for h in ledger["hardware"] if h["id"] == "H_NVIDIA_H100_SXM_80GB")["specs"]["peak_theoretical_rate"]
    assert peak["value"] == 989.5 and peak["approximate"] is True
    assert {"precision", "sparsity", "accumulation"} <= peak.keys()
    assert "FLOPS" not in PAGE.read_text(encoding="utf-8")


def test_complete_didactic_scenario_drives_capex_chart():
    ledger = data()
    scenario = ledger["didactic_scenarios"][0]
    assert scenario["id"] == "D_H100_8X_24H"
    for name in ("hbm_physical", "peak_rate", "power", "accelerator_hours", "energy", "capex"):
        cell = scenario["outputs"][name]
        assert {"status", "value", "unit", "formula", "inputs", "boundary", "source_ids"} <= cell.keys()
    assert scenario["outputs"]["capex"]["value"] == 240000
    capex = next(c for c in generator().load_chart_metadata(DATA) if c["id"] == "capex")
    assert capex["points"][0]["value"] == 240000
    assert capex["points"][0]["quantity"] == 8


def test_evidence_dates_artifacts_and_inference_states_are_explicit():
    ledger = data()
    for case in ledger["training_cases"]:
        assert "training_date_or_range" in case["metrics"]
    open_records = [m for m in ledger["models"] if m["canonical_name"] in {"Kimi K3", "Qwen3.8-2.4T-A95B"}]
    assert all("artifact_identity" in m["facts"] for m in open_records)
    partial = ledger["inference_scenarios"][0]["metrics"]["official_partial_benchmark"]
    assert partial["status"] == "FACT" and partial["not_used_for_sizing"] is True
    case = ledger["inference_capacity_cases"][0]
    assert case["capacity"]["total_gb"]["status"] == "DERIVED"
    assert case["capacity_assessment"]["status"] == "SCENARIO"
    assert "54.022 GiB" in PAGE.read_text(encoding="utf-8")


def test_pedagogy_mobile_language_and_glossary():
    text = PAGE.read_text(encoding="utf-8")
    assert 'estimated_time: "55 minutos"' in text
    assert "subtables" not in text and "ledger vertical" not in text
    for term in ("HBM", "TDP", "TGP", "CAPEX", "MFU", "SLA", "OOM", "TP", "PP", "DP", "TTFT"):
        assert f"**{term}**" in text
    assert "ESTIMATION_NOT_IDENTIFIABLE" in text and "NOT_FOUND" in text
    assert all(len(line.split("|")) <= 6 for line in text.splitlines() if line.startswith("|"))
    assert "word-break: break-all" not in text and "overflow-wrap: anywhere" not in text
