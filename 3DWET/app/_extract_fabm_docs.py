"""Scan the FABM model sources (src/*/src/*.F90) and collect, for every model:

  * state / bottom variables : name -> (units, long_name, default, minimum)
  * parameters               : name -> (units, description, default)

The result is dumped to app/fabm_docs.json, which the web GUI uses to show a
human readable explanation for every row in the "parameters" and
"initial conditions" pages (FABM itself only stores the English strings).

Run:  python app/_extract_fabm_docs.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "fabm_docs.json"

#  model  key in fabm.yaml  ->  source file(s) that define it
SRC_GLOBS = ["src/wet/src/*.F90", "src/**/src/*.F90"]

CALL_RE = re.compile(
    r"self%?(get_parameter|register_state_variable|register_bottom_state_variable|"
    r"register_variable|register_diagnostic_variable|register_horizontal_diagnostic_variable)\s*\(",
    re.IGNORECASE)

# (id, 'name', 'units'?, 'longname'?, default=..., minimum=...)
ARGS_RE = re.compile(r"'([^']*)'")


def split_args(text):
    """Split a Fortran argument list on top-level commas."""
    out, depth, cur, quote = [], 0, "", False
    for ch in text:
        if ch == "'":
            quote = not quote
        if ch == "," and not quote and depth == 0:
            out.append(cur.strip())
            cur = ""
            continue
        if ch in "([":
            depth += 1
        elif ch in ")]":
            depth -= 1
        cur += ch
    if cur.strip():
        out.append(cur.strip())
    return out


def paren_delta(line):
    """Unbalanced parentheses outside Fortran string literals.

    Literals may contain ')' (e.g. 'method: 0=no trans.; 1=constant)'), which
    would otherwise terminate a multi-line call too early.
    """
    in_str = False
    delta = 0
    for ch in line:
        if ch == "'":
            in_str = not in_str
            continue
        if in_str:
            continue
        if ch == "(":
            delta += 1
        elif ch == ")":
            delta -= 1
    return delta


def parse_file(path):
    """Yield (kind, name, units, long_name, default) tuples from one source file."""
    rows = []
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return rows
    lines = text.split("\n")
    # a registration call may span several lines -> join until the matching ')'
    i = 0
    while i < len(lines):
        m = CALL_RE.search(lines[i])
        if not m:
            i += 1
            continue
        kind = m.group(1).lower().replace("register_", "")
        buf = lines[i][m.end():]
        i += 1
        depth = paren_delta(buf)
        while depth > 0 and i < len(lines):
            depth += paren_delta(lines[i])
            buf += "\n" + lines[i]
            i += 1
        args = [a.strip() for a in split_args(buf)]
        # drop the trailing ")" leftovers
        args = [a for a in args if a and a != ")"]
        # positional part = leading literals such as 'sC', 'gC/m2', 'C'
        strings = [s[1:-1] for s in args if s.startswith("'")]
        #  both get_parameter and register_* put the name in the first literal
        #  argument; only the leading `self%id_xxx` handle is not a literal
        offset = 0
        if len(strings) >= offset + 3:
            name = strings[offset]
            units = strings[offset + 1]
            label = strings[offset + 2]
        elif len(strings) >= offset + 2:
            name, units, label = strings[offset], strings[offset + 1], ""
        else:
            continue
        # defensive cleanup: drop spill-over from a following line
        label = label.split("\n")[0].strip()
        for cut in ("default=", "initial_value="):
            if cut in label:
                label = label.split(cut)[0].strip()
        default = ""
        for a in args:
            low = a.lower()
            if low.startswith("default=") or low.startswith("initial_value="):
                v = a.split("=", 1)[1].strip().rstrip("_rk").strip()
                if v:
                    default = v
        rows.append((kind, name, units, label, default))
    return rows


def model_key_of(path, models):
    """Guess the fabm.yaml model key ('wet/om_pool', ...) from the source path."""
    rel = path.relative_to(ROOT).as_posix()      # e.g. src/wet/src/om_pool.F90
    parts = rel.split("/")
    if len(parts) >= 3:
        library = parts[1]                        # wet / npzd / ...
        stem = path.stem.lower()                  # om_pool
        cand = f"{library}/{stem}"
        if cand in models:
            return cand
        # fall back to matching on the model name only
        for m in models:
            if m.split("/")[-1] == stem:
                return m
    return None


def main():
    models = set()
    for case in (ROOT / "case").glob("*/fabm.yaml"):
        try:
            import yaml
            data = yaml.safe_load(case.read_text(encoding="utf-8")) or {}
            for inst in (data.get("instances") or {}).values():
                if isinstance(inst, dict) and inst.get("model"):
                    models.add(inst["model"])
        except Exception:
            pass
    print("models referenced by cases:", len(models), file=sys.stderr)

    files = set()
    for pat in SRC_GLOBS:
        files |= set(ROOT.glob(pat))

    docs = {}
    for path in sorted(files):
        if not path.is_file() or path.suffix != ".F90":
            continue
        key = model_key_of(path, models)
        if key is None:
            continue
        entry = docs.setdefault(key, {"variables": {}, "parameters": {}})
        for kind, name, units, label, default in parse_file(path):
            if kind in ("state_variable", "variable", "bottom_state_variable"):
                entry["variables"].setdefault(name, {
                    "units": units, "label": label, "default": default})
            else:
                entry["parameters"].setdefault(name, {
                    "units": units, "label": label, "default": default})

    OUT.write_text(json.dumps(docs, ensure_ascii=False, indent=1), encoding="utf-8")
    nv = sum(len(v["variables"]) for v in docs.values())
    np_ = sum(len(v["parameters"]) for v in docs.values())
    print(f"wrote {OUT.relative_to(ROOT)}: {len(docs)} models, "
          f"{nv} variables, {np_} parameters", file=sys.stderr)


if __name__ == "__main__":
    main()
