"""Validation helpers for explicitly non-scientific engineering proxy cases."""
from dataclasses import dataclass
import hashlib
from pathlib import Path, PurePosixPath
import re


ALLOWED_ROLES = {"measured", "derived", "synthetic_proxy", "upstream_reference", "missing"}
ALLOWED_PROVENANCE_STATUS = ALLOWED_ROLES | {"proxy"}
REQUIRED_GETM_INPUTS = {
    "bathymetry.nc", "fabm.yaml", "fabm_init.nc", "getm.inp", "getm_fabm.inp",
    "gotmturb.nml", "meteo.nc", "output.yaml",
}
_SHA256 = re.compile(r"^[0-9a-f]{64}$")


@dataclass(frozen=True)
class ManifestValidation:
    valid: bool
    target_lake: str | None = None
    warning: str | None = None
    manifest: dict | None = None


def _fail(message):
    return ManifestValidation(False, warning=message)


def validate_manifest(value, case_root):
    """Validate schema and on-disk provenance; never infer status from names."""
    if not isinstance(value, dict):
        return _fail("代理工程 manifest 必须是 JSON 对象")
    if value.get("schema_version") != 1 or value.get("kind") != "engineering_proxy":
        return _fail("代理工程 manifest schema 或 kind 不受支持")
    target = value.get("target_lake")
    if not isinstance(target, str) or not target.strip():
        return _fail("代理工程 manifest 缺少 target_lake")
    if value.get("validation_status") != "not_scientifically_validated":
        return _fail("代理工程科学验证状态必须为 not_scientifically_validated")
    if not isinstance(value.get("prepared"), bool):
        return _fail("代理工程 manifest 缺少布尔 prepared 状态")
    for field in ("geometry", "forcing"):
        detail = value.get(field)
        if (not isinstance(detail, dict)
                or detail.get("status") not in ALLOWED_PROVENANCE_STATUS
                or not isinstance(detail.get("description"), str)
                or not detail["description"].strip()):
            return _fail(f"代理工程 manifest 缺少有效 {field} 状态")
    sources = value.get("sources")
    if not isinstance(sources, list) or not sources:
        return _fail("代理工程 manifest 必须列出源输入或明确缺失项")

    prepared = value["prepared"]
    blockers = value.get("blockers", [])
    if not isinstance(blockers, list) or any(not isinstance(item, str) or not item.strip()
                                               for item in blockers):
        return _fail("代理工程 blockers 必须是非空字符串列表")
    if prepared and blockers:
        return _fail("已准备案例不能同时声明 blocker")
    if not prepared and not blockers:
        return _fail("未准备案例必须列出具体 blocker")
    if prepared and any(detail["status"] == "missing"
                        for detail in (value["geometry"], value["forcing"])):
        return _fail("已准备案例不能缺少空间几何或强迫")

    root = Path(case_root).resolve()
    missing_count = 0
    present_paths = set()
    for index, item in enumerate(sources):
        prefix = f"sources[{index}]"
        if not isinstance(item, dict):
            return _fail(f"{prefix} 必须为对象")
        role = item.get("role")
        source_path = item.get("path")
        purpose = item.get("purpose")
        if role not in ALLOWED_ROLES:
            return _fail(f"{prefix} role 无效")
        if not isinstance(source_path, str) or not source_path.strip():
            return _fail(f"{prefix} 缺少相对路径")
        if not isinstance(purpose, str) or not purpose.strip():
            return _fail(f"{prefix} 缺少用途")
        relative = PurePosixPath(source_path.replace("\\", "/"))
        if relative.is_absolute() or ".." in relative.parts:
            return _fail(f"{prefix} 路径必须位于案例目录内")
        if role == "missing":
            missing_count += 1
            if item.get("status") != "missing":
                return _fail(f"{prefix} 缺失输入必须显式标记 status=missing")
            if "sha256" in item or "bytes" in item:
                return _fail(f"{prefix} 缺失输入不能声明文件摘要或字节数")
            continue
        if item.get("status") == "missing":
            return _fail(f"{prefix} 缺失源不能声明为 {role}")
        path = (root / Path(*relative.parts)).resolve()
        try:
            path.relative_to(root)
        except ValueError:
            return _fail(f"{prefix} 路径解析后越出案例目录")
        if path.is_symlink():
            return _fail(f"{prefix} 不允许通过符号链接声明源文件")
        if not path.is_file():
            return _fail(f"{prefix} 源文件不存在")
        present_paths.add(relative.as_posix())
        digest = item.get("sha256")
        size = item.get("bytes")
        if not isinstance(digest, str) or not _SHA256.fullmatch(digest):
            return _fail(f"{prefix} 缺少有效 SHA-256")
        if not isinstance(size, int) or isinstance(size, bool) or size < 0:
            return _fail(f"{prefix} 缺少有效字节数")
        if path.stat().st_size != size:
            return _fail(f"{prefix} 字节数与源文件不匹配")
        hasher = hashlib.sha256()
        with path.open("rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                hasher.update(chunk)
        if hasher.hexdigest() != digest:
            return _fail(f"{prefix} SHA-256 与源文件不匹配")

    if prepared and missing_count:
        return _fail("已准备案例不能包含缺失输入")
    if prepared:
        absent = sorted(REQUIRED_GETM_INPUTS - present_paths)
        if absent:
            return _fail("已准备案例缺少 GETM 必需输入: " + ", ".join(absent))
        getm_path = root / "getm.inp"
        getm_text = getm_path.read_text(encoding="utf-8", errors="replace").lower()
        river_method = re.search(r"\briver_method\s*=\s*(\d+)", getm_text)
        has_river_pair = {"riverinfo.dat", "rivers.nc"}.issubset(present_paths)
        if not has_river_pair and (river_method is None or river_method.group(1) != "0"):
            return _fail("未提供 riverinfo.dat 和 rivers.nc 时，GETM 必须显式设置 river_method=0")
    return ManifestValidation(True, target.strip(), None, value)


def load_manifest(case_root):
    """Read and validate proxy manifest; absent/invalid stays an ordinary case."""
    path = Path(case_root) / "proxy_engineering.json"
    if not path.is_file():
        return _fail("未找到代理工程 manifest")
    try:
        import json
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return _fail(f"代理工程 manifest 无法读取: {exc}")
    return validate_manifest(value, case_root)
