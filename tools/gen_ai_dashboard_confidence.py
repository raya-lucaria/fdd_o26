#!/usr/bin/env python3
"""Annotate every dashboard ledger cell in the optional annex.

The annex remains hand-curated prose, while this narrow deterministic pass
keeps its 624 per-cell confidence labels synchronized with the YAML ledger.
"""

from pathlib import Path
import sys

import yaml

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from ai_model_dashboard import (  # noqa: E402
    CapacityScenario,
    build_inference_series,
    build_training_series,
    cell_confidence,
)


ROOT = TOOLS.parent
DATA = TOOLS / "data/ai_hardware_costs.yaml"
ANNEX = (
    ROOT
    / "course/3_arquitectura_de_computadoras/4_ai_escala_y_decision/A_evidencia_dashboard/0_index.md"
)


def annotate(text: str, ledger: dict) -> str:
    for model in ledger["dashboard_models"]:
        heading = f"### {model['canonical_name']} — `{model['id']}`"
        start = text.index(heading)
        end = text.find("\n### ", start + len(heading))
        if end < 0:
            end = text.index("\n## Corpus negativo", start)
        section = text[start:end]
        cells = {
            "year": model["year"],
            "architecture": model["architecture"],
            **model["metrics"],
        }
        for metric_id, cell in cells.items():
            prefix = f"- **{metric_id}:**"
            lines = section.splitlines()
            index = next(i for i, line in enumerate(lines) if line.startswith(prefix))
            line = lines[index]
            marker = " · **source_ids:**"
            before, after = line.split(marker, 1)
            before = before.split(" · **confianza:**", 1)[0]
            lines[index] = (
                f"{before} · **confianza:** {cell_confidence(cell, cells)}"
                f"{marker}{after}"
            )
            section = "\n".join(lines)
        text = text[:start] + section + text[end:]
    return text


def rebuild_visual_tables(text: str, ledger: dict) -> str:
    names = {
        model["id"]: model["canonical_name"]
        for model in ledger["dashboard_models"]
    }
    training = build_training_series(ledger)
    inference = build_inference_series(ledger, CapacityScenario())
    charts = {
        "ai-training-parameters.svg": training["parameters_total_active"],
        "ai-training-flop.svg": training["training_flop"],
        "ai-training-accelerators.svg": training["accelerators_and_hours"],
        "ai-training-power.svg": training["power_or_energy_envelope"],
        "ai-training-replacement-value.svg": training["replacement_value"],
        "ai-inference-memory.svg": inference["artifact_or_weight_floor"],
        "ai-inference-accelerators.svg": inference["h100_capacity_equivalents"],
        "ai-inference-power.svg": inference["accelerator_tdp_scenario"],
        "ai-inference-capex.svg": inference["accelerator_capex_scenario"],
        "ai-inference-parameters.svg": inference["parameters_total_active"],
    }
    for filename, points in charts.items():
        token = f"### `{filename}`"
        start = text.index(token)
        end = text.index("\n### `", start + len(token))
        rows = []
        for point in points:
            value = (
                str(point.value)
                if point.low is None and point.high is None
                else f"{point.low or point.value}–{point.high or point.value}"
            )
            rows.append(
                f"| {names[point.model_id]} · {point.year} · {point.label} | "
                f"`{point.status}` · {value} {point.unit} | {point.claim_scope} · "
                f"{', '.join(point.source_ids)} · confianza: `{point.confidence}` |"
            )
        if not rows:
            rows = ["| Sin puntos | 0 puntos; valor comparable no identificable | La ausencia no equivale a cero. |"]
        section = (
            f"### `{filename}` · {len(points)} puntos\n\n"
            "| Modelo · año · serie | Estado · valor | Alcance · fuentes · confianza |\n"
            "|---|---|---|\n" + "\n".join(rows) + "\n"
        )
        text = text[:start] + section + text[end:]
    return text


def main() -> None:
    ledger = yaml.safe_load(DATA.read_text(encoding="utf-8"))
    current = ANNEX.read_text(encoding="utf-8")
    ANNEX.write_text(rebuild_visual_tables(annotate(current, ledger), ledger), encoding="utf-8")


if __name__ == "__main__":
    main()
