from functools import lru_cache
from pathlib import Path
import re
import zipfile
import xml.etree.ElementTree as ET


NS = {
    "main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "rel": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

PRICE_GUIDANCE_SHEET = "双网调控-动态价格引导指数曲线"
PEAK_LOAD_SHEET = "双网调控-电网峰值片区负荷曲线"
TRAINING_CURVE_SHEET = "双网调控-训练迭代曲线"
SUPPLEMENTAL_KPI_SHEET = "总指标&双网协同效果数据"
TRAFFIC_DYNAMIC_SHEETS = {
    "平峰": "交通流调度-平峰场景动态时间块数据",
    "异常": "交通流调度-异常场景动态时间块数据",
}
PRICE_GUIDANCE_KEYS = [
    ("异常", "ccrp", "非自适应"),
    ("异常", "ccrp", "自适应"),
    ("异常", "gep", "非自适应"),
    ("异常", "gep", "自适应"),
    ("平峰", "ccrp", "非自适应"),
    ("平峰", "ccrp", "自适应"),
    ("平峰", "gep", "非自适应"),
    ("平峰", "gep", "自适应"),
]
PRICE_GUIDANCE_STEPS = 770
PEAK_LOAD_STEPS = 59
TRAINING_CURVE_STEPS = 100


def _excel_path() -> Path:
    root = Path(__file__).resolve().parent.parent
    matches = list(root.glob("data_v2*.xlsx")) or list(root.glob("data*.xlsx"))
    if not matches:
        raise FileNotFoundError("未找到 data*.xlsx 数据文件")
    return matches[0]


def _supplemental_excel_path() -> Path:
    return _excel_path()


def _column_index(cell_ref: str) -> int:
    letters = re.match(r"([A-Z]+)", cell_ref).group(1)
    value = 0
    for char in letters:
        value = value * 26 + ord(char) - 64
    return value - 1


def _text(element) -> str:
    if element is None:
        return ""
    return "".join(t.text or "" for t in element.findall(".//main:t", NS))


def _cell_value(cell, shared_strings: list[str]) -> str:
    value_element = cell.find("main:v", NS)
    value = "" if value_element is None else value_element.text or ""
    if cell.attrib.get("t") == "s" and value:
        return shared_strings[int(value)]
    if cell.attrib.get("t") == "inlineStr":
        return _text(cell.find("main:is", NS))
    return value


def _sheet_target(zip_file: zipfile.ZipFile, sheet_name: str) -> str:
    workbook = ET.fromstring(zip_file.read("xl/workbook.xml"))
    rels = ET.fromstring(zip_file.read("xl/_rels/workbook.xml.rels"))
    rel_map = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}

    for sheet in workbook.findall(".//main:sheet", NS):
        if sheet.attrib["name"] != sheet_name:
            continue
        rel_id = sheet.attrib[
            "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"
        ]
        target = rel_map[rel_id].lstrip("/")
        return target if target.startswith("xl/") else f"xl/{target}"

    raise KeyError(f"Excel 中未找到工作表：{sheet_name}")


@lru_cache(maxsize=1)
def load_price_guidance_series() -> dict[tuple[str, str, str], list[float]]:
    with zipfile.ZipFile(_excel_path()) as zip_file:
        shared_strings = []
        if "xl/sharedStrings.xml" in zip_file.namelist():
            shared_root = ET.fromstring(zip_file.read("xl/sharedStrings.xml"))
            shared_strings = [_text(item) for item in shared_root.findall("main:si", NS)]

        target = _sheet_target(zip_file, PRICE_GUIDANCE_SHEET)
        root = ET.fromstring(zip_file.read(target))
        rows = root.findall(".//main:sheetData/main:row", NS)

        row_values = []
        non_empty_columns = set()
        for row in rows:
            values = {}
            for cell in row.findall("main:c", NS):
                value = _cell_value(cell, shared_strings)
                if value == "":
                    continue
                column = _column_index(cell.attrib["r"])
                non_empty_columns.add(column)
                values[column] = value
            row_values.append(values)

        data_columns = sorted(non_empty_columns)[: len(PRICE_GUIDANCE_KEYS)]
        series = {key: [] for key in PRICE_GUIDANCE_KEYS}
        for key, column in zip(PRICE_GUIDANCE_KEYS, data_columns):
            for values in row_values:
                value = values.get(column)
                if value not in (None, ""):
                    series[key].append(float(value))

    return series


def get_price_guidance_series(scenario: str, method: str) -> dict[str, list[float]]:
    series = load_price_guidance_series()
    selected = {
        "非自适应": series[(scenario, method, "非自适应")],
        "自适应": series[(scenario, method, "自适应")],
    }

    normalized = {}
    for name, values in selected.items():
        clipped = values[:PRICE_GUIDANCE_STEPS]
        if clipped and len(clipped) < PRICE_GUIDANCE_STEPS:
            clipped = clipped + [clipped[-1]] * (PRICE_GUIDANCE_STEPS - len(clipped))
        normalized[name] = clipped

    return {
        "非自适应": normalized["非自适应"],
        "自适应": normalized["自适应"],
    }


def _sheet_rows(zip_file: zipfile.ZipFile, sheet_name: str, shared_strings: list[str]) -> list[dict[int, str]]:
    target = _sheet_target(zip_file, sheet_name)
    root = ET.fromstring(zip_file.read(target))
    rows = []
    for row in root.findall(".//main:sheetData/main:row", NS):
        values = {}
        for cell in row.findall("main:c", NS):
            value = _cell_value(cell, shared_strings)
            if value != "":
                values[_column_index(cell.attrib["r"])] = value
        rows.append(values)
    return rows


def _shared_strings(zip_file: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zip_file.namelist():
        return []
    shared_root = ET.fromstring(zip_file.read("xl/sharedStrings.xml"))
    return [_text(item) for item in shared_root.findall("main:si", NS)]


@lru_cache(maxsize=1)
def load_peak_area_load_series() -> dict[tuple[str, str], dict[str, list[float]]]:
    with zipfile.ZipFile(_excel_path()) as zip_file:
        shared_strings = _shared_strings(zip_file)
        rows = _sheet_rows(zip_file, PEAK_LOAD_SHEET, shared_strings)

    header_indexes = [
        index for index, row in enumerate(rows)
        if row.get(0) == "ccrp" and row.get(2) == "gep"
    ]
    scenarios = ["异常", "平峰"]
    result = {}

    for scenario, header_index in zip(scenarios, header_indexes):
        data_rows = rows[header_index + 1:header_index + 1 + PEAK_LOAD_STEPS]
        result[(scenario, "ccrp")] = {
            "优化前": [float(row[0]) for row in data_rows],
            "优化后": [float(row[1]) for row in data_rows],
        }
        result[(scenario, "gep")] = {
            "优化前": [float(row[2]) for row in data_rows],
            "优化后": [float(row[3]) for row in data_rows],
        }

    return result


def get_peak_area_load_series(scenario: str, method: str) -> dict[str, list[float]]:
    return load_peak_area_load_series()[(scenario, method)]


@lru_cache(maxsize=1)
def load_training_curve_series() -> dict[str, list[float]]:
    with zipfile.ZipFile(_excel_path()) as zip_file:
        shared_strings = _shared_strings(zip_file)
        rows = _sheet_rows(zip_file, TRAINING_CURVE_SHEET, shared_strings)

    header = rows[0]
    columns = {name: index for index, name in header.items()}
    data_rows = rows[1:1 + TRAINING_CURVE_STEPS]

    return {
        "avg": [float(row[columns["avg"]]) for row in data_rows],
        "std": [float(row[columns["std"]]) for row in data_rows],
        "max": [float(row[columns["max"]]) for row in data_rows],
    }


@lru_cache(maxsize=2)
def load_traffic_dynamic_records(scenario: str) -> dict[tuple[str, int], list[dict]]:
    sheet_name = TRAFFIC_DYNAMIC_SHEETS[scenario]
    with zipfile.ZipFile(_excel_path()) as zip_file:
        shared_strings = _shared_strings(zip_file)
        rows = _sheet_rows(zip_file, sheet_name, shared_strings)

    header = rows[0]
    columns = {name: index for index, name in header.items()}
    grouped = {}

    for row in rows[1:]:
        rule = row[columns["rule"]]
        block_id = int(float(row[columns["block_id"]]))
        key = (rule, block_id)
        grouped.setdefault(key, []).append({
            "rule": rule,
            "edge_id": row[columns["edge_id"]],
            "edge_u": row[columns["edge_u"]],
            "edge_u_lng": float(row[columns["edge_u_lng"]]),
            "edge_u_lat": float(row[columns["edge_u_lat"]]),
            "edge_v": row[columns["edge_v"]],
            "edge_v_lng": float(row[columns["edge_v_lng"]]),
            "edge_v_lat": float(row[columns["edge_v_lat"]]),
            "block_id": block_id,
            "flow_count": float(row[columns["flow_count"]]),
            "congestion_index": float(row[columns["congestion_index"]]),
        })

    return grouped


def get_traffic_dynamic_records(scenario: str, rule: str, block_id: int) -> list[dict]:
    return load_traffic_dynamic_records(scenario)[(rule, block_id)]


@lru_cache(maxsize=1)
def load_kpi_comparison() -> dict[str, dict[str, float]]:
    with zipfile.ZipFile(_supplemental_excel_path()) as zip_file:
        shared_strings = _shared_strings(zip_file)
        rows = _sheet_rows(zip_file, SUPPLEMENTAL_KPI_SHEET, shared_strings)

    result = {"平峰": {}, "异常": {}}
    current_scenario = None
    for row in rows:
        label = row.get(7)
        value = row.get(8)
        if label == "平峰场景":
            current_scenario = "平峰"
            continue
        if label == "异常场景":
            current_scenario = "异常"
            continue
        if current_scenario and label and value is not None:
            metric_name = {
                "交通拥堵时间减少": "拥堵时间减少",
                "电网峰值负荷降低": "峰值负荷降低",
            }.get(label, label)
            result[current_scenario][metric_name] = float(value) * 100

    return {
        scenario: {metric: round(value, 2) for metric, value in metrics.items()}
        for scenario, metrics in result.items()
    }


def get_kpi_comparison(scenario: str) -> dict[str, float]:
    return load_kpi_comparison()[scenario]


@lru_cache(maxsize=1)
def load_synergy_radar_data() -> dict[str, dict[str, list[float]]]:
    with zipfile.ZipFile(_supplemental_excel_path()) as zip_file:
        shared_strings = _shared_strings(zip_file)
        rows = _sheet_rows(zip_file, SUPPLEMENTAL_KPI_SHEET, shared_strings)

    result = {}
    current_scenario = None
    metrics = ["拥堵时间", "调度效率", "电网局部压力", "峰值片区负荷"]

    for row in rows:
        if row.get(0) == "平峰":
            current_scenario = "平峰"
            result[current_scenario] = {"GEP": [], "CCRP": []}
            continue
        if row.get(0) == "异常":
            current_scenario = "异常"
            result[current_scenario] = {"GEP": [], "CCRP": []}
            continue
        if not current_scenario or row.get(0) not in ("ccrp", "gep"):
            continue

        values = [float(row[index]) for index in (2, 3, 4, 5)]
        method = row[0].upper()
        if row.get(1, "").startswith("soc_adaptive"):
            result[current_scenario][method] = values
        elif not result[current_scenario][method]:
            result[current_scenario][method] = values

    return {
        scenario: {"指标": metrics, **methods}
        for scenario, methods in result.items()
    }


def get_synergy_radar_data(scenario: str) -> dict[str, list[float]]:
    return load_synergy_radar_data()[scenario]
