"""Resumen de ventas por región: total con IVA, clientes, puntajes y filas inválidas."""

import csv
import re
import sys
import time
from collections.abc import Iterable, Sequence
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal
from pathlib import Path

from puntaje import puntaje

type Puntaje = float

COLUMNAS: tuple[str, ...] = ("region", "cliente", "monto", "descuento")
IVA = Decimal("0.16")
CENTAVO = Decimal("0.01")
ESPERADO = Decimal("2722.27")

# [0-9] y no \d: \d acepta dígitos Unicode como "١٢".
_MONTO = re.compile(r"[0-9]{1,3}(?:,[0-9]{3})+\.[0-9]{2}|[0-9]+\.[0-9]{2}")
_DESCUENTO = re.compile(r"[0-9]+(?:\.[0-9]+)?|\.[0-9]+")


@dataclass(frozen=True, slots=True)
class Venta:
    linea: int
    region: str
    cliente: str
    monto: Decimal
    descuento: Decimal


@dataclass(frozen=True, slots=True)
class FilaInvalida:
    linea: int
    motivo: str


@dataclass(frozen=True, slots=True)
class Lectura:
    ventas: tuple[Venta, ...]
    errores: tuple[FilaInvalida, ...]
    aviso: str | None = None


@dataclass(frozen=True, slots=True)
class ResumenRegion:
    region: str
    total_con_iva: Decimal  # sin redondear
    clientes: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Puntajes:
    valores: tuple[tuple[str, Puntaje], ...]
    fallos: tuple[tuple[str, str], ...]
    segundos: float


class EncabezadoInvalido(ValueError):
    pass


def parsear_monto(texto: str) -> Decimal:
    limpio = texto.strip()
    if not limpio:
        raise ValueError("monto vacío")
    if not _MONTO.fullmatch(limpio):
        raise ValueError(
            f"monto mal escrito: {texto!r} (se espera 1234.56 o 1,234.56)"
        )
    return Decimal(limpio.replace(",", ""))


def parsear_descuento(texto: str) -> Decimal:
    limpio = texto.strip()
    if not limpio:
        raise ValueError("descuento vacío (sin descuento se escribe 0)")
    if not _DESCUENTO.fullmatch(limpio):
        raise ValueError(f"descuento mal escrito: {texto!r}")
    descuento = Decimal(limpio)
    # Comparación explícita: `if not descuento` trataría el 0 válido como faltante.
    if descuento > 1:
        raise ValueError(f"descuento fuera de [0, 1]: {texto!r}")
    return descuento


def parsear_fila(campos: Sequence[str], linea: int) -> Venta | FilaInvalida:
    if len(campos) == 0:
        return FilaInvalida(linea, "línea vacía")
    if len(campos) != len(COLUMNAS):
        pista = (
            " (¿monto con coma de miles sin comillas?)"
            if len(campos) == len(COLUMNAS) + 1
            else ""
        )
        return FilaInvalida(
            linea,
            f"se esperaban {len(COLUMNAS)} columnas y hay {len(campos)}{pista}",
        )
    region, cliente, monto_txt, descuento_txt = (c.strip() for c in campos)
    if not region:
        return FilaInvalida(linea, "región vacía")
    if not cliente:
        return FilaInvalida(linea, "cliente vacío")
    try:
        monto = parsear_monto(monto_txt)
        descuento = parsear_descuento(descuento_txt)
    except ValueError as error:
        return FilaInvalida(linea, str(error))
    return Venta(linea, region, cliente, monto, descuento)


def leer_ventas(ruta: Path) -> Lectura:
    ventas: list[Venta] = []
    errores: list[FilaInvalida] = []
    with ruta.open(encoding="utf-8-sig", newline="") as archivo:
        lector = csv.reader(archivo, strict=True)
        try:
            encabezado = next(lector, None)
        except csv.Error as error:
            raise EncabezadoInvalido(f"línea 1: {error}") from None
        if encabezado is None:
            return Lectura((), (), aviso="archivo vacío: no tiene ni encabezado")
        if tuple(c.strip() for c in encabezado) != COLUMNAS:
            raise EncabezadoInvalido(
                f"encabezado {encabezado!r}; se esperaba {','.join(COLUMNAS)}"
            )
        while True:
            inicio = lector.line_num + 1  # primera línea física del registro
            try:
                campos = next(lector)
            except StopIteration:
                break
            except csv.Error as error:
                errores.append(FilaInvalida(inicio, f"CSV mal formado: {error}"))
                if lector.line_num < inicio:  # no avanzó: evita ciclo infinito
                    break
                continue
            match parsear_fila(campos, inicio):
                case Venta() as venta:
                    ventas.append(venta)
                case FilaInvalida() as invalida:
                    errores.append(invalida)
    return Lectura(tuple(ventas), tuple(errores))


def total_con_iva(venta: Venta) -> Decimal:
    return venta.monto * (1 - venta.descuento) * (1 + IVA)


def resumir_por_region(ventas: Iterable[Venta]) -> tuple[ResumenRegion, ...]:
    totales: dict[str, Decimal] = {}
    clientes: dict[str, set[str]] = {}
    for venta in ventas:
        totales[venta.region] = totales.get(venta.region, Decimal(0)) + total_con_iva(venta)
        clientes.setdefault(venta.region, set()).add(venta.cliente)
    return tuple(
        ResumenRegion(region, totales[region], tuple(sorted(clientes[region])))
        for region in sorted(totales)
    )


def total_general(resumen: Iterable[ResumenRegion]) -> Decimal:
    return sum((r.total_con_iva for r in resumen), start=Decimal(0))


def redondear_centavos(valor: Decimal) -> Decimal:
    return valor.quantize(CENTAVO, rounding=ROUND_HALF_UP)


def cuadra(total: Decimal, esperado: Decimal = ESPERADO) -> bool:
    return redondear_centavos(total) == esperado


def calcular_puntajes(clientes: Iterable[str]) -> Puntajes:
    unicos = sorted(set(clientes))
    valores: dict[str, Puntaje] = {}
    fallos: dict[str, str] = {}
    inicio = time.perf_counter()
    if unicos:
        with ProcessPoolExecutor() as pool:
            futuros = {pool.submit(puntaje, cliente): cliente for cliente in unicos}
            for futuro in as_completed(futuros):
                cliente = futuros[futuro]
                try:
                    valores[cliente] = futuro.result()
                except Exception as error:  # incluye BrokenProcessPool
                    fallos[cliente] = f"{type(error).__name__}: {error}"
    segundos = time.perf_counter() - inicio
    return Puntajes(
        tuple(sorted(valores.items())), tuple(sorted(fallos.items())), segundos
    )


def imprimir_reporte(
    lectura: Lectura,
    resumen: tuple[ResumenRegion, ...],
    puntajes: Puntajes,
    total: Decimal,
) -> None:
    if lectura.aviso is not None:
        print(f"AVISO: {lectura.aviso}")

    print("== Totales por región (con IVA 16 %) ==")
    for r in resumen:
        print(f"{r.region}: {redondear_centavos(r.total_con_iva)}  "
              f"clientes: {', '.join(r.clientes)}")
    if not resumen:
        print("(sin ventas válidas)")

    print("\n== Puntaje por cliente ==")
    for cliente, valor in puntajes.valores:
        print(f"{cliente}: {valor}")
    for cliente, motivo in puntajes.fallos:
        print(f"{cliente}: ERROR {motivo}")
    print(f"(puntajes calculados en {puntajes.segundos:.3f} s)")

    print(f"\n== Filas no leídas: {len(lectura.errores)} ==")
    for e in lectura.errores:
        print(f"línea {e.linea}: {e.motivo}")

    print(f"\nTotal general: {total}")
    print(f"¿Igual a {ESPERADO}? {'sí' if total == ESPERADO else 'no'}")


def main(argv: Sequence[str] | None = None) -> int:
    args = sys.argv[1:] if argv is None else argv
    ruta = Path(args[0]) if args else Path("ventas.csv")
    inicio = time.perf_counter()
    try:
        lectura = leer_ventas(ruta)
    except FileNotFoundError:
        print(f"No existe {ruta}", file=sys.stderr)
        return 2
    except (EncabezadoInvalido, UnicodeDecodeError) as error:
        print(f"No se puede leer {ruta}: {error}", file=sys.stderr)
        return 2
    resumen = resumir_por_region(lectura.ventas)
    puntajes = calcular_puntajes(v.cliente for v in lectura.ventas)
    total = redondear_centavos(total_general(resumen))
    imprimir_reporte(lectura, resumen, puntajes, total)
    print(f"Tiempo total: {time.perf_counter() - inicio:.3f} s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
