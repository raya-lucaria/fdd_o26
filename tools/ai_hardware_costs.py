"""Cálculos dimensionales para el ledger de costos de hardware de IA.

Cada función nombra la unidad de su resultado.  En particular, un pico se
expresa en TFLOP/s y este módulo no lo convierte en trabajo de entrenamiento;
un accelerator-hour es asignación de hardware, no energía en kWh.
"""

from collections.abc import Iterable, Mapping, Sequence
from decimal import Decimal, InvalidOperation
from typing import Any


_THOUSAND = Decimal("1000")
_BYTES_PER_GB = Decimal("1000000000")
_BYTES_PER_GIB = Decimal(2) ** 30
_PEAK_CONVENTION_FIELDS = ("precision", "sparsity", "accumulation")
_OPTIONAL_PEAK_CONVENTION_FIELDS = ("tensor_mode",)


def _decimal(value: Decimal | int | str, name: str) -> Decimal:
    """Return an exact decimal, rejecting binary floats and non-finite values."""
    if isinstance(value, bool) or isinstance(value, float):
        raise TypeError(f"{name} must be Decimal, int, or decimal string; not float")
    try:
        result = Decimal(value)
    except (InvalidOperation, TypeError, ValueError) as error:
        raise TypeError(f"{name} must be Decimal, int, or decimal string") from error
    if not result.is_finite():
        raise ValueError(f"{name} must be finite")
    return result


def _nonnegative(value: Decimal | int | str, name: str) -> Decimal:
    result = _decimal(value, name)
    if result < 0:
        raise ValueError(f"{name} must be non-negative")
    return result


def _count(value: int, name: str) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer count")
    if value < 0:
        raise ValueError(f"{name} must be non-negative")
    return Decimal(value)


def _convention(convention: Mapping[str, Any]) -> tuple[str, ...]:
    if not isinstance(convention, Mapping):
        raise TypeError("convention must be a mapping")

    values: list[str] = []
    for field in _PEAK_CONVENTION_FIELDS:
        value = convention.get(field)
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"peak convention requires {field}")
        values.append(value.strip())

    for field in _OPTIONAL_PEAK_CONVENTION_FIELDS:
        value = convention.get(field)
        if value is None:
            values.append("")
        elif isinstance(value, str) and value.strip():
            values.append(value.strip())
        else:
            raise ValueError(f"peak convention {field} must be a non-empty string")
    return tuple(values)


def installed_hbm_gb(count: int, hbm_gb: Decimal | int | str) -> Decimal:
    """Return physical HBM installed in decimal GB, never usable model memory."""
    return _count(count, "count") * _nonnegative(hbm_gb, "hbm_gb")


def installed_hbm_gib(count: int, hbm_gib: Decimal | int | str) -> Decimal:
    """Return physical HBM installed in binary GiB, explicitly separate from GB."""
    return _count(count, "count") * _nonnegative(hbm_gib, "hbm_gib")


def peak_rate_tflops(
    count: int,
    per_chip_tflops: Decimal | int | str,
    convention: Mapping[str, Any],
) -> Decimal:
    """Return one theoretical peak-rate series in TFLOP/s.

    ``convention`` must state precision, dense/sparse convention, and
    accumulation.  It is deliberately a rate-only operation: multiplying the
    result by time does not establish observed or real FLOP of training.
    """
    _convention(convention)
    return _count(count, "count") * _nonnegative(
        per_chip_tflops, "per_chip_tflops"
    )


def _entry_convention(entry: Mapping[str, Any]) -> tuple[str, ...]:
    convention = entry.get("convention", entry)
    if not isinstance(convention, Mapping):
        raise TypeError("peak entry convention must be a mapping")
    return _convention(convention)


def _normalized_entry_convention(entry: Mapping[str, Any]) -> tuple[str | None, ...]:
    """Normalize declared fields before comparing incomplete peak conventions."""
    convention = entry.get("convention", entry)
    if not isinstance(convention, Mapping):
        raise TypeError("peak entry convention must be a mapping")

    fields = _PEAK_CONVENTION_FIELDS + _OPTIONAL_PEAK_CONVENTION_FIELDS
    values: list[str | None] = []
    for field in fields:
        value = convention.get(field)
        if value is None:
            values.append(None)
        elif isinstance(value, str) and value.strip():
            values.append(value.strip())
        else:
            raise ValueError(f"peak convention requires {field}")
    return tuple(values)


def _entry_hardware(entry: Mapping[str, Any]) -> str:
    value = entry.get("hardware_id", entry.get("hardware"))
    if not isinstance(value, str) or not value.strip():
        raise ValueError("peak entry requires hardware_id")
    return value.strip()


def _entry_rate(entry: Mapping[str, Any]) -> Decimal:
    rate_keys = ("tflops", "rate_tflops", "peak_tflops")
    present = [key for key in rate_keys if key in entry]
    if len(present) != 1:
        raise ValueError("peak entry requires exactly one TFLOP/s rate")
    return _nonnegative(entry[present[0]], present[0])


def aggregate_peaks(entries: Iterable[Mapping[str, Any]]) -> Decimal:
    """Sum TFLOP/s only when hardware and all peak conventions are identical."""
    if isinstance(entries, (str, bytes)):
        raise TypeError("entries must be an iterable of peak mappings")
    entries = list(entries)
    if not entries:
        raise ValueError("entries must not be empty")
    if not all(isinstance(entry, Mapping) for entry in entries):
        raise TypeError("entries must contain peak mappings")

    normalized_conventions = [_normalized_entry_convention(entry) for entry in entries]
    if len(set(normalized_conventions)) != 1:
        raise ValueError("aggregate_peaks requires a homogeneous peak convention")
    _entry_convention(entries[0])

    hardware = [_entry_hardware(entry) for entry in entries]
    if len(set(hardware)) != 1:
        raise ValueError("aggregate_peaks requires homogeneous hardware")

    return sum((_entry_rate(entry) for entry in entries), Decimal("0"))


def accelerator_hours(
    count: int,
    wall_hours: Decimal | int | str,
    *,
    unit: str = "accelerator-hours",
) -> Decimal:
    """Return allocated accelerator-hours; this quantity is not electrical energy."""
    if unit != "accelerator-hours":
        if unit == "kWh":
            raise ValueError("accelerator-hours are not kWh")
        raise ValueError("accelerator_hours uses the unit accelerator-hours")
    return _count(count, "count") * _nonnegative(wall_hours, "wall_hours")


def _basis_value(value: Any) -> Any:
    """Read a literal or the ``value`` in an evidence cell from the ledger."""
    if isinstance(value, Mapping) and "value" in value:
        return value["value"]
    return value


def _validate_price_basis(
    price_basis: Mapping[str, Any] | None,
    expected_boundary: str,
) -> Mapping[str, Any] | None:
    if price_basis is None:
        return None
    if not isinstance(price_basis, Mapping):
        raise TypeError("price_basis must be a mapping")

    boundary = _basis_value(price_basis.get("boundary", expected_boundary))
    if boundary != expected_boundary:
        raise ValueError(
            f"price_basis boundary must be {expected_boundary}; "
            "accelerator-only and system-based are mutually exclusive"
        )

    transaction_unit = _basis_value(price_basis.get("transaction_unit"))
    allowed_units = (
        {"card", "module"}
        if expected_boundary == "accelerator-only"
        else {"server", "rack"}
    )
    if transaction_unit not in allowed_units:
        allowed = ", ".join(sorted(allowed_units))
        raise ValueError(
            f"{expected_boundary} price_basis transaction_unit must be {allowed}"
        )
    return price_basis


def accelerator_capex(
    count: int,
    unit_price_usd: Decimal | int | str,
    *,
    price_basis: Mapping[str, Any] | None = None,
) -> Decimal:
    """Return accelerator-only CAPEX in USD; it contains no server or network."""
    _validate_price_basis(price_basis, "accelerator-only")
    return _count(count, "count") * _nonnegative(unit_price_usd, "unit_price_usd")


def _network_is_explicitly_outside_system(
    price_basis: Mapping[str, Any] | None,
) -> bool:
    """Whether the ledger proves that network parts are outside the system price."""
    if price_basis is None:
        return False
    if "network" in price_basis:
        value = _basis_value(price_basis["network"])
        return isinstance(value, str) and value in {
            "excluded",
            "not_included",
            "outside_system",
        }

    # Compatibility for callers that used the original provisional alias.
    value = _basis_value(price_basis.get("network_included"))
    return value is False or value in {"excluded", "not_included"}


def system_capex(
    systems: int,
    system_price_usd: Decimal | int | str,
    network_parts: Sequence[tuple[int, Decimal | int | str]],
    *,
    price_basis: Mapping[str, Any] | None = None,
) -> Decimal:
    """Return system CAPEX plus only network that is outside those systems."""
    _validate_price_basis(price_basis, "system-based")
    if not isinstance(network_parts, Sequence) or isinstance(network_parts, (str, bytes)):
        raise TypeError("network_parts must be a sequence of (quantity, unit price)")
    if network_parts and not _network_is_explicitly_outside_system(price_basis):
        raise ValueError(
            "network_parts require price_basis.network to declare network outside "
            "the system price"
        )

    network_total = Decimal("0")
    for part in network_parts:
        if not isinstance(part, tuple) or len(part) != 2:
            raise TypeError("each network part must be a (quantity, unit price) tuple")
        quantity, unit_price = part
        network_total += _count(quantity, "network quantity") * _nonnegative(
            unit_price, "network unit price"
        )
    return _count(systems, "systems") * _nonnegative(
        system_price_usd, "system_price_usd"
    ) + network_total


def weight_floor_gb(
    parameters: Decimal | int | str, bits: Decimal | int | str
) -> Decimal:
    """Return the decimal-GB weight floor, excluding metadata and runtime memory."""
    return (
        _nonnegative(parameters, "parameters")
        * _nonnegative(bits, "bits")
        / Decimal(8)
        / _BYTES_PER_GB
    )


def inference_capacity_floor(
    parameters: Decimal | int | str,
    bits: Decimal | int | str,
    quant_overhead: Decimal | int | str,
    runtime_gb: Decimal | int | str,
    kv_gb: Decimal | int | str,
    workspace_gb: Decimal | int | str,
    reserve_fraction: Decimal | int | str,
) -> dict[str, Decimal]:
    """Expose the decimal-GB components of an inference capacity floor."""
    weights_gb = weight_floor_gb(parameters, bits)
    quant_overhead_gb = weights_gb * _nonnegative(
        quant_overhead, "quant_overhead"
    )
    quantized_weights_gb = weights_gb + quant_overhead_gb
    runtime_gb = _nonnegative(runtime_gb, "runtime_gb")
    kv_gb = _nonnegative(kv_gb, "kv_gb")
    workspace_gb = _nonnegative(workspace_gb, "workspace_gb")
    reserve_fraction = _nonnegative(reserve_fraction, "reserve_fraction")
    if reserve_fraction >= 1:
        raise ValueError("reserve_fraction must be less than one")
    before_reserve_gb = (
        quantized_weights_gb
        + runtime_gb
        + kv_gb
        + workspace_gb
    )
    reserve_gb = before_reserve_gb * reserve_fraction
    return {
        "weights_gb": weights_gb,
        "quant_overhead_gb": quant_overhead_gb,
        "quantized_weights_gb": quantized_weights_gb,
        "runtime_gb": runtime_gb,
        "kv_gb": kv_gb,
        "workspace_gb": workspace_gb,
        "before_reserve_gb": before_reserve_gb,
        "reserve_gb": reserve_gb,
        "total_gb": before_reserve_gb + reserve_gb,
    }


def watts_to_kw(watts: Decimal | int | str) -> Decimal:
    """Convert physical power from W to kW; this does not calculate energy."""
    return _nonnegative(watts, "watts") / _THOUSAND


def kw_to_mw(kw: Decimal | int | str) -> Decimal:
    """Convert physical power from kW to MW; this does not calculate energy."""
    return _nonnegative(kw, "kw") / _THOUSAND


def bits_to_bytes(bits: Decimal | int | str) -> Decimal:
    """Convert a bit quantity to bytes without changing GB/GiB convention."""
    return _nonnegative(bits, "bits") / Decimal(8)


def gb_to_gib(gb: Decimal | int | str) -> Decimal:
    """Convert decimal GB to binary GiB using their explicit byte definitions."""
    return _nonnegative(gb, "gb") * _BYTES_PER_GB / _BYTES_PER_GIB


def gib_to_gb(gib: Decimal | int | str) -> Decimal:
    """Convert binary GiB to decimal GB using their explicit byte definitions."""
    return _nonnegative(gib, "gib") * _BYTES_PER_GIB / _BYTES_PER_GB
