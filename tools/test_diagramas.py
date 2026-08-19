"""Guarda: cada SVG del disco es exactamente lo que su generador produce hoy.

gen_diagramas.py es la unica fuente de verdad de los diagramas. Si alguien edita
un .svg a mano, o cambia el generador sin regenerar, esta prueba falla.
"""
import copy
import importlib.util
from pathlib import Path
import re
import subprocess
import sys
import xml.etree.ElementTree as ET

import pytest
import yaml

RAIZ = Path(__file__).resolve().parent.parent
AI_GENERATOR = RAIZ / "tools/gen_ai_hardware_costs.py"
AI_ASSETS = RAIZ / "course/3_arquitectura_de_computadoras/_assets"
AI_SVG_NAMES = (
    "ai-aceleradores-entrenamiento.svg",
    "ai-hbm-entrenamiento.svg",
    "ai-potencia-hardware.svg",
    "ai-capex-hardware.svg",
    "ai-inferencia-capacidad.svg",
)


def _cargar_generador():
    spec = importlib.util.spec_from_file_location(
        "gen_diagramas", RAIZ / "tools/gen_diagramas.py"
    )
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


def _cargar_generador_ai():
    assert AI_GENERATOR.is_file(), (
        "falta tools/gen_ai_hardware_costs.py: las visuales de hardware IA "
        "deben salir de un generador determinista"
    )
    spec = importlib.util.spec_from_file_location(
        "gen_ai_hardware_costs", AI_GENERATOR
    )
    modulo = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modulo)
    return modulo


GEN = _cargar_generador()
SLUGS = list(GEN.DIAGRAMAS)


def test_son_los_ocho_diagramas_esperados():
    assert SLUGS == [
        "d-dag", "d-schema", "d-etl-elt", "d-tidy",
        "d-calidad", "d-idempotencia", "d-tiempo", "d-ciclo",
    ]


@pytest.mark.parametrize("slug", SLUGS)
def test_svg_en_disco_coincide_con_su_generador(slug):
    destino = GEN.ASSETS / f"{slug}.svg"
    assert destino.is_file(), (
        f"falta {destino.name}: corre `python3 tools/gen_diagramas.py`"
    )
    esperado = GEN.DIAGRAMAS[slug]()
    actual = destino.read_text(encoding="utf-8")
    assert actual == esperado, (
        f"{destino.name} no coincide con lo que gen_diagramas.py produce hoy. "
        f"Los SVG no se editan a mano: corre `python3 tools/gen_diagramas.py`."
    )


@pytest.mark.parametrize("slug", SLUGS)
def test_generador_es_determinista(slug):
    assert GEN.DIAGRAMAS[slug]() == GEN.DIAGRAMAS[slug]()


@pytest.mark.parametrize("slug", SLUGS)
def test_svg_cumple_convenciones(slug):
    texto = (GEN.ASSETS / f"{slug}.svg").read_text(encoding="utf-8")
    raiz = texto.split(">")[0]
    assert 'viewBox="' in raiz, f"{slug}: la raiz no declara viewBox"
    # Sin width/height propios el navegador incrusta el <svg> con el tamano por
    # omision de un elemento reemplazado (~300x150 px) y se ve minusculo.
    assert "width=" in raiz and "height=" in raiz, f"{slug}: raiz sin width/height"
    assert 'role="img"' in raiz, f"{slug}: la raiz no declara role=img"
    assert "<title>" in texto, f"{slug}: sin <title> descriptivo"
    titulo = texto.split("<title>")[1].split("</title>")[0]
    assert len(titulo) > 30, f"{slug}: el <title> es demasiado escueto"
    # Fondo propio + fill explicito en todo texto: el diagrama se lee igual con
    # tema claro y con tema oscuro, sin heredar color del sitio.
    assert f'fill="{GEN.FONDO}"' in texto, f"{slug}: sin fondo propio"
    assert "<text" in texto, f"{slug}: sin texto"
    for fragmento in texto.split("<text")[1:]:
        assert "fill=" in fragmento.split(">")[0], (
            f"{slug}: hay un <text> sin fill explicito"
        )


@pytest.mark.parametrize("slug", SLUGS)
def test_svg_es_xml_bien_formado(slug):
    from xml.etree import ElementTree

    ElementTree.fromstring((GEN.ASSETS / f"{slug}.svg").read_text(encoding="utf-8"))


@pytest.mark.parametrize("slug", SLUGS)
def test_ningun_texto_del_svg_es_una_frase(slug):
    """El texto largo va al pie de figura en Markdown, no pintado dentro del SVG.

    Dentro del SVG solo caben etiquetas. El framework ya no encoge estos SVG de
    figura al ancho del viewport (regla `max-width: none` en el CSS del sitio,
    con scroll horizontal por debajo del umbral de portatil): el riesgo no es
    que una frase quede en unos 5px en movil, sino que un parrafo entero
    pintado a mano en el SVG no se pueda seleccionar, buscar ni traducir como
    el resto de la prosa. Se exceptuan los <text> con font-size de 14 o mas: a
    esa talla un rotulo corto (el titulo del encabezado, una etiqueta de eje)
    sigue siendo una etiqueta y no un parrafo. Se extrae el font-size de cada
    nodo en vez de exceptuar por posicion: es mas robusto que asumir que los
    dos primeros <text> son siempre encabezado y subtitulo.
    """
    import re

    texto = (GEN.ASSETS / f"{slug}.svg").read_text(encoding="utf-8")
    nodos = re.findall(r'<text[^>]*font-size="([\d.]+)"[^>]*>([^<]*)</text>', texto)
    largos = [
        contenido for size, contenido in nodos
        if float(size) < 14 and len(contenido.split()) > 6
    ]
    assert not largos, (
        f"{slug}: hay texto de mas de 6 palabras a menos de 14px dentro del SVG: {largos}"
    )


def test_el_generador_no_pinta_pies_de_figura():
    fuente = (RAIZ / "tools/gen_diagramas.py").read_text(encoding="utf-8")
    assert "def pie(" not in fuente, (
        "pie() volvio a gen_diagramas.py: el texto largo va al Markdown"
    )


def test_ai_hardware_declara_exactamente_cinco_svg_y_los_regenera(tmp_path):
    """Agregar u omitir una lámina rompería el recorrido docente aprobado."""
    generador = _cargar_generador_ai()

    assert tuple(generador.SVG_FILENAMES) == AI_SVG_NAMES
    creados = generador.render_all(generador.DATA_PATH, tmp_path)
    assert [path.name for path in creados] == list(AI_SVG_NAMES)
    assert {path.name for path in tmp_path.glob("*.svg")} == set(AI_SVG_NAMES)


def test_ai_hardware_generator_se_puede_importar_desde_la_raiz():
    """La fuente de verdad debe servir tanto como script como módulo de tools."""
    result = subprocess.run(
        [
            sys.executable,
            "-c",
            "from tools.gen_ai_hardware_costs import load_chart_metadata; "
            "assert len(load_chart_metadata()) == 5",
        ],
        cwd=RAIZ,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_ai_hardware_utilidades_puras_respetan_escala_formato_y_estado():
    """Una interpolación lineal o marcadores iguales falsearían la codificación."""
    generador = _cargar_generador_ai()

    assert generador.log_position(1, 1, 1000, 20, 320) == pytest.approx(20)
    assert generador.log_position(10, 1, 1000, 20, 320) == pytest.approx(120)
    assert generador.log_position(1000, 1, 1000, 20, 320) == pytest.approx(320)
    with pytest.raises(ValueError, match="positive"):
        generador.log_position(0, 1, 1000, 20, 320)
    assert generador.format_si(153600, "W") == "153.6 kW"
    assert generador.format_si(11468800, "W") == "11.47 MW"
    assert generador.format_si(30000, "USD") == "USD 30,000"
    assert {
        generador.marker_for_status(status)
        for status in ("FACT", "DERIVED", "SCENARIO")
    } == {"circle", "square", "diamond"}
    root = generador.svg_header(360, 240, "Título suficientemente largo", "Desc")
    assert root.attrib["viewBox"] == "0 0 360 240"
    assert root.find("{http://www.w3.org/2000/svg}title").text.startswith("Título")


@pytest.mark.parametrize("name", AI_SVG_NAMES)
def test_ai_hardware_svg_es_accesible_y_legible_en_movil(name):
    """Un lienzo ancho o texto pequeño obligaría a hacer zoom a 390 px."""
    path = AI_ASSETS / name
    assert path.is_file(), f"falta {name}: corre `python3 tools/gen_ai_hardware_costs.py`"
    root = ET.parse(path).getroot()
    namespace = "{http://www.w3.org/2000/svg}"
    title = root.find(f"{namespace}title")
    desc = root.find(f"{namespace}desc")

    assert title is not None and title.text and len(title.text) > 24
    assert desc is not None and desc.text and len(desc.text) > 60
    assert root.attrib["role"] == "img"
    assert root.attrib["aria-labelledby"] == "title desc"
    viewbox = [float(value) for value in root.attrib["viewBox"].split()]
    assert viewbox[:2] == [0, 0]
    assert viewbox[2] <= 360
    sizes = [
        float(node.attrib["font-size"])
        for node in root.iter()
        if "font-size" in node.attrib
    ]
    # Raya deja 28 px de margen por lado en un viewport Chromium de 390 px.
    mobile_content_width = 390 - 2 * 28
    mobile_scale = min(1, mobile_content_width / viewbox[2])
    assert sizes and min(sizes) * mobile_scale >= 16
    assert root.attrib.get("style") == "max-width:100%;height:auto"


def test_ai_hardware_log_ticks_son_potencias_y_no_grafican_ausencias():
    """Cero o un estado ausente en log inventaría una posición cuantitativa."""
    generador = _cargar_generador_ai()
    negative = {
        "UNDISCLOSED_BY_CREATOR",
        "NOT_FOUND",
        "ESTIMATION_NOT_IDENTIFIABLE",
        "NOT_APPLICABLE",
    }

    for chart in generador.load_chart_metadata(generador.DATA_PATH):
        if chart["scale"] != "log":
            continue
        assert chart["scale_note"] == "Igual distancia representa multiplicación."
        assert chart["ticks"] == sorted(chart["ticks"])
        assert all(tick > 0 and 10 ** round(generador.math.log10(tick)) == tick
                   for tick in chart["ticks"])
        assert not negative & set(chart["plotted_statuses"])
        assert all(point["value"] > 0 for point in chart["points"])
        for point in chart["points"]:
            if "low" in point or "high" in point:
                assert {"low", "high"} <= set(point)
                assert 0 < point["low"] <= point["high"]


def _write_ai_ledger(tmp_path, data):
    path = tmp_path / "ledger.yaml"
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def _assert_ai_svg_text_geometry(root, name):
    """Check source-space text bounds with a conservative system-ui metric."""
    boxes = []
    for node in root.iter("{http://www.w3.org/2000/svg}text"):
        text = "".join(node.itertext())
        size = float(node.attrib["font-size"])
        width = len(text) * size * 0.62
        x = float(node.attrib["x"])
        anchor = node.attrib.get("text-anchor", "start")
        if anchor == "middle":
            left, right = x - width / 2, x + width / 2
        elif anchor == "end":
            left, right = x - width, x
        else:
            left, right = x, x + width
        y = float(node.attrib["y"])
        box = (left, y - size, right, y + size * 0.25, text)
        assert left >= 8 and right <= 352, (
            f"{name}: {text!r} sale del viewBox: x={left:.1f}..{right:.1f}"
        )
        boxes.append(box)

    for index, first in enumerate(boxes):
        for second in boxes[index + 1:]:
            horizontal = min(first[2], second[2]) - max(first[0], second[0])
            vertical = min(first[3], second[3]) - max(first[1], second[1])
            assert horizontal <= 1 or vertical <= 1, (
                f"{name}: textos solapados {first[4]!r} y {second[4]!r}"
            )


def test_ai_hardware_intervalos_completos_llegan_a_metadata_y_svg(tmp_path):
    """Descartar low/high oculta el rango y deja sólo un punto engañoso."""
    generador = _cargar_generador_ai()
    data = yaml.safe_load(generador.DATA_PATH.read_text(encoding="utf-8"))
    mutated = copy.deepcopy(data)
    first = next(
        case for case in mutated["training_cases"]
        if case["include_in_documented_table"]
    )
    first["metrics"]["accelerators_concurrent"].update(low=300, high=500)
    mutated["valuations"][0]["price"].update(low=25000, high=35000)
    ledger = _write_ai_ledger(tmp_path, mutated)
    charts = {
        chart["id"]: chart for chart in generador.load_chart_metadata(ledger)
    }

    assert (charts["accelerators"]["points"][0]["low"],
            charts["accelerators"]["points"][0]["high"]) == (300, 500)
    assert (charts["capex"]["points"][0]["low"],
            charts["capex"]["points"][0]["high"]) == (200000, 280000)

    generated = tmp_path / "assets"
    generador.render_all(ledger, generated)
    accelerator_xml = (generated / AI_SVG_NAMES[0]).read_text(encoding="utf-8")
    capex_xml = (generated / AI_SVG_NAMES[3]).read_text(encoding="utf-8")
    assert "300–500 aceleradores [FACT]" in accelerator_xml
    assert "USD 200,000–USD 280,000" in capex_xml
    assert "[DERIVED]" in capex_xml
    for xml, label, low, high in (
        (accelerator_xml, "BLOOM 176B", "300", "500"),
            (capex_xml, "accelerator-only · supuesto docente 2026", "200000", "280000"),
    ):
        root = ET.fromstring(xml)
        intervals = [
            node for node in root.iter()
            if node.attrib.get("data-interval") == "true"
            and node.attrib.get("data-label") == label
        ]
        assert len(intervals) == 1
        assert intervals[0].attrib["data-low"] == low
        assert intervals[0].attrib["data-high"] == high
        assert {
            node.attrib.get("data-interval-end")
            for node in root.iter()
            if node.attrib.get("data-label") == label
        } >= {"low", "high"}
    _assert_ai_svg_text_geometry(
        ET.fromstring(accelerator_xml), "ai-aceleradores-intervalo-sintetico.svg"
    )
    _assert_ai_svg_text_geometry(
        ET.fromstring(capex_xml), "ai-capex-intervalo-sintetico.svg"
    )


@pytest.mark.parametrize("endpoint", ["low", "high"])
def test_ai_hardware_intervalo_con_un_solo_extremo_falla(tmp_path, endpoint):
    """Aceptar medio intervalo convierte evidencia incompleta en una banda."""
    generador = _cargar_generador_ai()
    data = yaml.safe_load(generador.DATA_PATH.read_text(encoding="utf-8"))
    first = next(
        case for case in data["training_cases"]
        if case["include_in_documented_table"]
    )
    first["metrics"]["accelerators_concurrent"][endpoint] = 300
    ledger = _write_ai_ledger(tmp_path, data)

    with pytest.raises(ValueError, match="both low and high"):
        generador.load_chart_metadata(ledger)


def test_ai_hardware_estado_ausente_con_extremos_no_se_grafica(tmp_path):
    """Un rango en una celda ausente no autoriza inventar una posición."""
    generador = _cargar_generador_ai()
    data = yaml.safe_load(generador.DATA_PATH.read_text(encoding="utf-8"))
    deepseek = next(
        case for case in data["training_cases"]
        if case["id"] == "T_DEEPSEEK_V3_PRETRAINING"
    )
    deepseek["metrics"]["accelerator_power"].update(low=1, high=2)
    ledger = _write_ai_ledger(tmp_path, data)
    generated = tmp_path / "assets"
    generador.render_all(ledger, generated)
    root = ET.parse(generated / "ai-potencia-hardware.svg").getroot()

    assert not any(
        node.attrib.get("data-row") == "true"
        and node.attrib.get("data-label") == "DeepSeek-V3"
        for node in root.iter()
    )


@pytest.mark.parametrize("name", AI_SVG_NAMES)
def test_ai_hardware_svg_codifica_estado_con_forma_y_texto(name):
    """Quitar color no debe borrar la diferencia entre FACT, DERIVED y SCENARIO."""
    root = ET.parse(AI_ASSETS / name).getroot()
    plotted = [node for node in root.iter() if "data-status" in node.attrib]

    assert plotted
    assert all(node.attrib.get("data-marker") for node in plotted)
    assert all(node.attrib.get("data-label") for node in plotted)
    xml = ET.tostring(root, encoding="unicode")
    for node in plotted:
        assert f"[{node.attrib['data-status']}]" in xml


@pytest.mark.parametrize("name", AI_SVG_NAMES)
def test_ai_hardware_texto_permanece_dentro_del_lienzo_y_sin_solaparse(name):
    """Cada renglón visible debe caber y quedar separado de los demás."""
    root = ET.parse(AI_ASSETS / name).getroot()
    _assert_ai_svg_text_geometry(root, name)


def test_ai_hardware_svg_en_disco_coincide_y_es_determinista(tmp_path):
    """Editar SVG a mano o depender de orden no estable cambia el artefacto."""
    generador = _cargar_generador_ai()
    primera = generador.render_all(generador.DATA_PATH, tmp_path / "primera")
    segunda = generador.render_all(generador.DATA_PATH, tmp_path / "segunda")

    for uno, dos, name in zip(primera, segunda, AI_SVG_NAMES, strict=True):
        assert uno.read_bytes() == dos.read_bytes()
        assert uno.read_bytes() == (AI_ASSETS / name).read_bytes()
        assert not re.search(rb"(?:timestamp|generated-at|uuid)", uno.read_bytes(), re.I)


def test_ai_capex_nota_ausente_queda_dentro_de_su_panel():
    """La segunda línea del fallback no debe cruzar el borde del panel system-based."""
    root = ET.parse(AI_ASSETS / "ai-capex-hardware.svg").getroot()
    namespace = "{http://www.w3.org/2000/svg}"
    note = next(
        node for node in root.iter(f"{namespace}text")
        if node.text == "no se grafica."
    )
    panels = [
        node for node in root.iter(f"{namespace}rect")
        if node.attrib.get("x") == "12" and node.attrib.get("width") == "336"
    ]
    system_panel = max(panels, key=lambda node: float(node.attrib["y"]))
    note_bottom = float(note.attrib["y"]) + float(note.attrib["font-size"]) * 0.25
    panel_bottom = float(system_panel.attrib["y"]) + float(system_panel.attrib["height"])
    assert note_bottom <= panel_bottom - 4
