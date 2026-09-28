"""坐标系工具：预设 CRS、pyproj 重投影、地方坐标系平移拟合。

前处理模块在"湖泊边界"与"底部高程"两个 shapefile 坐标系不一致时的对齐策略：
- 标准坐标系（WGS84 / CGCS2000 / 北京54 / 西安80 / UTM ...）→ pyproj 精确重投影
- 地方/未知坐标系（无法用标准 CRS 描述）→ 按两文件包围盒中心平移拟合。
  两个文件描述的是同一片湖体，包围盒对齐后残差通常在数百米内，
  对公里级变化的水深插值无实质影响。
"""
from pyproj import CRS, Transformer

WGS84 = CRS.from_epsg(4326)

# 三种国产大地基准的椭球 proj4 片段
_DATUMS = {
    "cgcs2000": ("CGCS2000", "+ellps=GRS80"),
    "beijing54": ("北京54", "+ellps=krass"),
    "xian80": ("西安80", "+a=6378140 +rf=298.257"),
}

# 预设 id → proj4 / EPSG 字符串（标准 3°高斯带，含 500km 假东）
PRESETS = {
    "wgs84_ll": "EPSG:4326",
    "cgcs2000_ll": "EPSG:4490",
    "utm47n": "EPSG:32647",
    "utm48n": "EPSG:32648",
}
for _cm in (102, 105):
    for _key, (_label, _ell) in _DATUMS.items():
        PRESETS[f"{_key}_gk{_cm}"] = (
            f"+proj=tmerc +lat_0=0 +lon_0={_cm} +k=1 "
            f"+x_0=500000 +y_0=0 {_ell} +units=m +no_defs")

PRESET_LABELS = {
    "wgs84_ll": "WGS84 经纬度",
    "cgcs2000_ll": "CGCS2000 经纬度",
    "utm47n": "WGS84 / UTM 47N",
    "utm48n": "WGS84 / UTM 48N",
}
for _cm in (102, 105):
    for _key, (_label, _ell) in _DATUMS.items():
        PRESET_LABELS[f"{_key}_gk{_cm}"] = f"{_label} 高斯3°带 CM{_cm}°"


def build_crs(preset_id, epsg_code=""):
    """根据预设 id 构造 pyproj CRS。

    preset_id 为 'auto'/空 → None（维持自动检测）；
    'epsg' → 由 epsg_code 构造；否则查 PRESETS 表。
    无法识别时返回 None。
    """
    if not preset_id or preset_id == "auto":
        return None
    if preset_id == "epsg":
        code = (epsg_code or "").strip()
        if not code.isdigit():
            return None
        try:
            return CRS.from_epsg(int(code))
        except Exception:
            return None
    spec = PRESETS.get(preset_id)
    if not spec:
        return None
    try:
        # spec 可能是 "EPSG:xxxx" 或 proj4 字符串，from_user_input 两者都支持
        return CRS.from_user_input(spec)
    except Exception:
        return None


def preset_label(preset_id, epsg_code=""):
    """预设 id 的人类可读名称（用于日志与前端回显）。"""
    if preset_id == "epsg":
        code = (epsg_code or "").strip()
        return f"EPSG:{code}" if code else "EPSG"
    return PRESET_LABELS.get(preset_id, preset_id)


def utm_crs(zone):
    """北半球 WGS84 UTM 带（zone 1-60 → EPSG 32601-32660）。"""
    return CRS.from_epsg(32600 + int(zone))


def make_transformer(src_crs, dst_crs):
    """构造 x,y 顺序的单次 Transformer（重复使用，避免逐点重建开销）。"""
    return Transformer.from_crs(src_crs, dst_crs, always_xy=True)


def crs_from_wkt(wkt_text):
    """把 .prj 的 WKT 字符串解析成 pyproj CRS（如 Albers/UTM/经纬度）。

    解析失败（非标准 WKT）返回 None，调用方回退到平移拟合。
    """
    try:
        return CRS.from_wkt(wkt_text)
    except Exception:
        return None


def fit_translation_offset(src_bbox, dst_bbox):
    """包围盒中心平移拟合：返回 (dx, dy) 使 src+(dx,dy) 的中心对齐 dst。"""
    dx = (dst_bbox[0] + dst_bbox[2] - src_bbox[0] - src_bbox[2]) / 2.0
    dy = (dst_bbox[1] + dst_bbox[3] - src_bbox[1] - src_bbox[3]) / 2.0
    return dx, dy
