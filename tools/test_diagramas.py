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
DASHBOARD_GENERATOR = RAIZ / "tools/gen_ai_model_dashboard.py"
DASHBOARD_SVG_NAMES = (
    "ai-training-parameters.svg",
    "ai-training-flop.svg",
    "ai-training-accelerators.svg",
    "ai-training-power.svg",
    "ai-training-replacement-value.svg",
    "ai-inference-memory.svg",
    "ai-inference-accelerators.svg",
    "ai-inference-power.svg",
    "ai-inference-capex.svg",
    "ai-inference-parameters.svg",
    "ai-pareto-training.svg",
    "ai-pareto-inference.svg",
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


def _cargar_generador_dashboard():
    assert DASHBOARD_GENERATOR.is_file(), (
        "falta tools/gen_ai_model_dashboard.py: el dashboard debe salir de "
        "un generador determinista"
    )
    spec = importlib.util.spec_from_file_location(
        "gen_ai_model_dashboard", DASHBOARD_GENERATOR
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


def test_dashboard_generator_produce_exactamente_doce_assets(tmp_path):
    """Omitir o agregar una gráfica rompe el recorrido de 5+5+2 aprobado."""
    generador = _cargar_generador_dashboard()

    creados = generador.render_dashboard(
        generador.DATA_PATH, generador.ECI_PATH, tmp_path
    )

    assert tuple(generador.SVG_FILENAMES) == DASHBOARD_SVG_NAMES
    assert [path.name for path in creados] == list(DASHBOARD_SVG_NAMES)
    assert {path.name for path in tmp_path.glob("*.svg")} == set(DASHBOARD_SVG_NAMES)


def test_dashboard_svg_conserva_semantica_accesible_y_mobile(tmp_path):
    """Perder fuentes, alcance o talla móvil vuelve ambiguo el dato dibujado."""
    generador = _cargar_generador_dashboard()
    paths = generador.render_dashboard(
        generador.DATA_PATH, generador.ECI_PATH, tmp_path
    )
    ns = "{http://www.w3.org/2000/svg}"
    allowed = {"FACT", "DERIVED", "ESTIMATE", "SCENARIO"}

    for path in paths:
        root = ET.parse(path).getroot()
        width = float(root.attrib["viewBox"].split()[2])
        title = root.find(f"{ns}title")
        desc = root.find(f"{ns}desc")
        sizes = [
            float(node.attrib["font-size"])
            for node in root.iter()
            if "font-size" in node.attrib
        ]
        quantitative = [
            node for node in root.iter()
            if node.attrib.get("data-quantitative") == "true"
        ]

        assert width <= 640
        assert title is not None and title.text and len(title.text) > 20
        assert desc is not None and desc.text and len(desc.text) > 60
        assert root.attrib.get("role") == "img"
        assert root.attrib.get("aria-labelledby") == "title desc"
        assert sizes and min(sizes) * min(1, 390 / width) >= 16
        for node in quantitative:
            assert node.attrib["data-model-id"].startswith("DM_")
            assert node.attrib["data-status"] in allowed
            assert node.attrib["data-source-ids"]
            assert node.attrib["data-value"]
            assert node.attrib["data-unit"]
            assert node.attrib["data-claim-scope"]
            assert node.attrib["data-marker"]
            if node.attrib["data-status"] == "ESTIMATE":
                assert float(node.attrib["data-low"]) > 0
                assert float(node.attrib["data-high"]) >= float(node.attrib["data-low"])
                fallback = " ".join(node.itertext()) + node.attrib.get("aria-label", "")
                assert node.attrib["data-low"] in fallback
                assert node.attrib["data-high"] in fallback


def test_dashboard_svg_no_depende_solo_del_color_y_no_inventa_ausencias(tmp_path):
    """Quitar color no debe confundir estados ni convertir missing en cero."""
    generador = _cargar_generador_dashboard()
    paths = generador.render_dashboard(
        generador.DATA_PATH, generador.ECI_PATH, tmp_path
    )

    statuses = {}
    for path in paths:
        root = ET.parse(path).getroot()
        for node in root.iter():
            status = node.attrib.get("data-status")
            marker = node.attrib.get("data-marker")
            if status and marker:
                statuses.setdefault(status, set()).add(marker)
            if node.attrib.get("data-quantitative") == "true":
                assert float(node.attrib["data-value"]) > 0
    assert statuses["FACT"] == {"circle"}
    assert statuses["DERIVED"] == {"square"}
    assert statuses["ESTIMATE"] == {"diamond"}
    assert statuses["SCENARIO"] == {"triangle"}

    replacement = (tmp_path / "ai-training-replacement-value.svg").read_text()
    assert "No hay una serie comparable" in replacement
    assert 'data-quantitative="true"' not in replacement


def test_dashboard_ejes_y_pareto_dic_en_exactamente_que_comparan(tmp_path):
    """Un eje sin año, log o ECI permite leer una comparación distinta."""
    generador = _cargar_generador_dashboard()
    generador.render_dashboard(generador.DATA_PATH, generador.ECI_PATH, tmp_path)

    for name in DASHBOARD_SVG_NAMES[:10]:
        xml = (tmp_path / name).read_text(encoding="utf-8")
        assert "Año de publicación" in xml
        if name != "ai-training-replacement-value.svg":
            assert "Igual distancia = multiplicar" in xml
    for name in DASHBOARD_SVG_NAMES[10:]:
        xml = (tmp_path / name).read_text(encoding="utf-8")
        assert "Capacidad general según ECI" in xml
        assert "inteligencia" not in xml.lower()
        assert "frontera-segura" in xml
        assert "frontera-posible" in xml


def test_dashboard_series_dobles_no_mezclan_total_activo_ni_conteo_horas(tmp_path):
    """Dos magnitudes en un panel necesitan una segunda marca, no sólo color."""
    generador = _cargar_generador_dashboard()
    generador.render_dashboard(generador.DATA_PATH, generador.ECI_PATH, tmp_path)
    for name, expected in (
        ("ai-training-parameters.svg", {"total", "active"}),
        ("ai-training-accelerators.svg", {"concurrent accelerators", "accelerator-hours"}),
    ):
        root = ET.parse(tmp_path / name).getroot()
        nodes = [
            node for node in root.iter()
            if node.attrib.get("data-quantitative") == "true"
        ]
        assert {node.attrib["data-series"] for node in nodes} == expected
        series_markers = {
            series: {node.attrib["data-series-marker"] for node in nodes
                     if node.attrib["data-series"] == series}
            for series in expected
        }
        assert len({tuple(markers) for markers in series_markers.values()}) == 2
        legends = [node for node in root.iter() if node.attrib.get("data-legend") == "true"]
        assert legends and all("data-series" in node.attrib for node in legends)

    accelerators = ET.parse(tmp_path / "ai-training-accelerators.svg").getroot()
    panels = [node.attrib["data-series-panel"] for node in accelerators.iter()
              if "data-series-panel" in node.attrib]
    assert set(panels) == {"concurrent accelerators", "accelerator-hours"}


def test_dashboard_leyenda_parametros_usa_aro_neutro_no_estado(tmp_path):
    """Color/forma codifican evidencia; sólo el aro distingue total de activo."""
    generador = _cargar_generador_dashboard()
    generador.render_dashboard(generador.DATA_PATH, generador.ECI_PATH, tmp_path)
    for name in ("ai-training-parameters.svg", "ai-inference-parameters.svg"):
        root = ET.parse(tmp_path / name).getroot()
        legends = {
            node.attrib["data-series"]: node for node in root.iter()
            if node.attrib.get("data-legend") == "true"
        }
        assert set(legends) == {"total", "active"}
        assert {node.attrib["fill"] for node in legends.values()} == {"#cbd5e1"}
        assert legends["total"].attrib["data-series-marker"] == "single"
        assert legends["active"].attrib["data-series-marker"] == "outer-ring"
        nodes = [node for node in root.iter()
                 if node.attrib.get("data-quantitative") == "true"]
        for node in nodes:
            rings = [child for child in node
                     if child.attrib.get("data-series-ring") == "true"]
            assert bool(rings) == (node.attrib["data-series"] == "active")
            assert node.attrib["data-marker"] == {
                "FACT": "circle", "DERIVED": "square",
                "ESTIMATE": "diamond", "SCENARIO": "triangle",
            }[node.attrib["data-status"]]


def test_dashboard_subtitulos_distinguen_modelos_de_observaciones(tmp_path):
    """Total/activo y artefacto/piso pueden aportar dos marcas por modelo."""
    generador = _cargar_generador_dashboard()
    paths = generador.render_dashboard(
        generador.DATA_PATH, generador.ECI_PATH, tmp_path
    )
    for path in paths[:10]:
        root = ET.parse(path).getroot()
        nodes = [node for node in root.iter()
                 if node.attrib.get("data-quantitative") == "true"]
        expected = f"{len({node.attrib['data-model-id'] for node in nodes})} modelos · {len(nodes)} observaciones"
        assert expected in " ".join(root.itertext()), path.name


def test_dashboard_pareto_serializa_y_dibuja_intervalos_reconstruibles(tmp_path):
    """Usar sólo puntos centrales falsearía costo, ECI y dominancia por rangos."""
    generador = _cargar_generador_dashboard()
    generador.render_dashboard(generador.DATA_PATH, generador.ECI_PATH, tmp_path)
    root = ET.parse(tmp_path / "ai-pareto-inference.svg").getroot()
    nodes = {
        node.attrib["data-model-id"]: node for node in root.iter()
        if node.attrib.get("data-pareto-interval") == "true"
    }
    expected = {
        "DM_GEMMA3_27B": ("30000", "30000", "124.67", "133.1"),
        "DM_LLAMA31_8B": ("30000", "30000", "105.01", "121.29"),
        "DM_QWEN3_235B_A22B": ("180000", "180000", "134.85", "140.96"),
    }
    for model_id, bounds in expected.items():
        node = nodes[model_id]
        actual = tuple(node.attrib[key] for key in (
            "data-cost-low", "data-cost-high", "data-score-low", "data-score-high"
        ))
        assert actual == bounds
        assert node.attrib["data-frontier"] in {"safe", "possible", "dominated"}
        assert any(child.attrib.get("data-interval-geometry") == "true"
                   for child in node.iter())
    xml = ET.tostring(root, encoding="unicode")
    assert "segura en todo el rango" in xml
    assert "posible en algún valor del rango" in xml
    assert not any(node.tag.endswith("polyline") for node in root.iter())


def test_dashboard_pareto_ordena_etiquetas_y_no_cruza_guias(tmp_path):
    """Una guía cruzada vuelve ambigua la correspondencia punto-modelo."""
    generador = _cargar_generador_dashboard()
    generador.render_dashboard(generador.DATA_PATH, generador.ECI_PATH, tmp_path)
    for name in ("ai-pareto-training.svg", "ai-pareto-inference.svg"):
        root = ET.parse(tmp_path / name).getroot()
        leaders = [node for node in root.iter()
                   if node.attrib.get("data-pareto-leader") == "true"]
        intervals = [node for node in root.iter()
                     if node.attrib.get("data-pareto-interval") == "true"]
        assert len(leaders) == len(intervals)
        segments = [tuple(float(node.attrib[key]) for key in ("x1", "y1", "x2", "y2"))
                    for node in leaders]
        for index, a in enumerate(segments):
            for b in segments[index + 1:]:
                assert not generador.segments_cross(a, b), (name, a, b)
        if leaders:
            assert len(leaders) == len({node.attrib["data-model-id"] for node in leaders})


def test_dashboard_pareto_audita_titulo_x_y_nota_log_por_separado(tmp_path):
    """El título de costo y la nota log no deben compartir caja ni quedar sin auditar."""
    generador = _cargar_generador_dashboard()
    generador.render_dashboard(generador.DATA_PATH, generador.ECI_PATH, tmp_path)
    for name in ("ai-pareto-training.svg", "ai-pareto-inference.svg"):
        root = ET.parse(tmp_path / name).getroot()
        roles = {node.attrib.get("data-axis-role") for node in root.iter()}
        assert {"x-title", "x-log-note"} <= roles
        for role in ("x-title", "x-log-note"):
            node = next(node for node in root.iter()
                        if node.attrib.get("data-axis-role") == role)
            assert node.attrib.get("data-axis-label") == "true"


def test_dashboard_generacion_es_byte_a_byte_determinista(tmp_path):
    """Orden de diccionarios o timestamps no deben alterar el artefacto."""
    generador = _cargar_generador_dashboard()
    first = generador.render_dashboard(
        generador.DATA_PATH, generador.ECI_PATH, tmp_path / "a"
    )
    second = generador.render_dashboard(
        generador.DATA_PATH, generador.ECI_PATH, tmp_path / "b"
    )

    assert [path.read_bytes() for path in first] == [path.read_bytes() for path in second]
    assert all(
        path.read_bytes() == (AI_ASSETS / path.name).read_bytes()
        for path in first
    )


def test_dashboard_chromium_bbox_y_texto_390_1440(tmp_path):
    """Recortes o etiquetas directas superpuestas hacen ilegible la gráfica real."""
    playwright = pytest.importorskip("playwright.sync_api")
    generador = _cargar_generador_dashboard()
    paths = generador.render_dashboard(
        generador.DATA_PATH, generador.ECI_PATH, tmp_path / "assets"
    )

    with playwright.sync_playwright() as runtime:
        browser = runtime.chromium.launch(headless=True)
        page = browser.new_page()
        for viewport, container in ((390, 334), (1440, 600)):
            page.set_viewport_size({"width": viewport, "height": 900})
            for path in paths:
                svg = path.read_text(encoding="utf-8")
                page.set_content(
                    f'<main style="width:{container}px;margin:0">{svg}</main>'
                )
                result = page.locator("svg").evaluate(
                    """svg => {
                      const vb = svg.viewBox.baseVal;
                      const scale = svg.getBoundingClientRect().width / vb.width;
                      const texts = [...svg.querySelectorAll('text')];
                      const boxes = texts.map(node => {
                        const box = node.getBBox();
                        return {x: box.x, y: box.y, right: box.x + box.width,
                                bottom: box.y + box.height,
                                px: parseFloat(node.getAttribute('font-size')) * scale,
                                text: node.textContent};
                      });
                      const direct = [...svg.querySelectorAll('[data-direct-label="true"]')]
                        .map(node => node.getBBox());
                      const obstacles = [...svg.querySelectorAll('[data-quantitative="true"], [data-axis-label="true"], [data-interval-geometry="true"]')]
                        .map(node => node.getBBox());
                      const axis = [...svg.querySelectorAll('[data-axis-label="true"]')]
                        .map(node => node.getBBox());
                      const overlaps = [];
                      for (let i=0; i<direct.length; i++) for (let j=i+1; j<direct.length; j++) {
                        const a=direct[i], b=direct[j];
                        if (Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x)>1 &&
                            Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y)>1) overlaps.push([i,j]);
                      }
                      const obstacleOverlaps = [];
                      for (let i=0; i<direct.length; i++) for (let j=0; j<obstacles.length; j++) {
                        const a=direct[i], b=obstacles[j];
                        if (Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x)>1 &&
                            Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y)>1) obstacleOverlaps.push([i,j]);
                      }
                      const axisOverlaps = [];
                      for (let i=0; i<axis.length; i++) for (let j=i+1; j<axis.length; j++) {
                        const a=axis[i], b=axis[j];
                        if (Math.min(a.x+a.width,b.x+b.width)-Math.max(a.x,b.x)>1 &&
                            Math.min(a.y+a.height,b.y+b.height)-Math.max(a.y,b.y)>1) axisOverlaps.push([i,j]);
                      }
                      return {boxes, overlaps, obstacleOverlaps, axisOverlaps, width: vb.width, height: vb.height};
                    }"""
                )
                assert result["boxes"], path.name
                assert min(box["px"] for box in result["boxes"]) >= 16, path.name
                for box in result["boxes"]:
                    assert box["x"] >= -1 and box["right"] <= result["width"] + 1, (path.name, box)
                    assert box["y"] >= -1 and box["bottom"] <= result["height"] + 1, (path.name, box)
                assert not result["overlaps"], (path.name, result["overlaps"])
                assert not result["obstacleOverlaps"], (path.name, result["obstacleOverlaps"])
                assert not result["axisOverlaps"], (path.name, result["axisOverlaps"])
        browser.close()
