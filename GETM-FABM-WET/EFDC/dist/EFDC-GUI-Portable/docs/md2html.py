# -*- coding: utf-8 -*-
"""Tiny Markdown -> HTML converter for the user guide (headings, lists, tables,
images, code fences, bold, inline code, blockquote, hr). No external deps.

python -X utf8 docs/md2html.py 使用指南.md 使用指南.html
"""
import html
import os
import re
import sys


def inline(s):
    s = html.escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"!\[([^\]]*)\]\(([^)]+)\)", r'<img alt="\1" src="\2">', s)
    return s


def convert(md):
    out, i = [], 0
    lines = md.splitlines()
    in_code = False
    list_type = None
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("```"):
            if in_code:
                out.append("</code></pre>")
                in_code = False
            else:
                out.append('<pre><code>')
                in_code = True
            i += 1
            continue
        if in_code:
            out.append(html.escape(ln))
            i += 1
            continue

        if re.match(r"^\s*\|.*\|\s*$", ln):
            rows = []
            while i < len(lines) and re.match(r"^\s*\|.*\|\s*$", lines[i]):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.match(r"^:?-{2,}:?$", c) for c in cells):
                    rows.append(cells)
                i += 1
            out.append("<table>")
            for k, cells in enumerate(rows):
                tag = "th" if k == 0 else "td"
                out.append("<tr>" + "".join("<%s>%s</%s>" % (tag, inline(c), tag) for c in cells) + "</tr>")
            out.append("</table>")
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", ln)
        if m:
            n = len(m.group(1))
            out.append("<h%d>%s</h%d>" % (n, inline(m.group(2)), n))
            i += 1
            continue

        if re.match(r"^\s*---+\s*$", ln):
            out.append("<hr>")
            i += 1
            continue

        m = re.match(r"^>\s?(.*)$", ln)
        if m:
            buf = []
            while i < len(lines) and re.match(r"^>\s?", lines[i]):
                buf.append(re.sub(r"^>\s?", "", lines[i]))
                i += 1
            out.append("<blockquote>%s</blockquote>" % "<br>".join(inline(x) for x in buf))
            continue

        m = re.match(r"^\s*([-*])\s+(.*)$", ln)
        if m:
            out.append("<ul>")
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                out.append("<li>%s</li>" % inline(re.sub(r"^\s*[-*]\s+", "", lines[i])))
                i += 1
            out.append("</ul>")
            continue

        m = re.match(r"^\s*(\d+)\.\s+(.*)$", ln)
        if m:
            out.append("<ol>")
            while i < len(lines) and re.match(r"^\s*\d+\.\s+", lines[i]):
                out.append("<li>%s</li>" % inline(re.sub(r"^\s*\d+\.\s+", "", lines[i])))
                i += 1
            out.append("</ol>")
            continue

        if ln.strip() == "":
            i += 1
            continue

        out.append("<p>%s</p>" % inline(ln))
        i += 1
    return "\n".join(out)


TEMPLATE = """<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EFDC Explorer 8.4 便携版 · 使用指南</title>
<style>
 body{font-family:"Microsoft YaHei","微软雅黑",system-ui,sans-serif;max-width:960px;margin:32px auto;padding:0 20px;line-height:1.75;color:#222;background:#fff}
 h1{border-bottom:3px solid #1a6fb5;padding-bottom:8px;color:#0d4c80}
 h2{margin-top:38px;border-left:5px solid #1a6fb5;padding-left:10px;color:#0d4c80}
 h3{margin-top:24px;color:#12527f}
 table{border-collapse:collapse;width:100%;margin:14px 0;font-size:15px}
 th,td{border:1px solid #d0d7de;padding:7px 10px;text-align:left;vertical-align:top}
 th{background:#eef4fa}
 tr:nth-child(even) td{background:#fafbfc}
 code{background:#f2f3f5;padding:1px 5px;border-radius:4px;font-family:Consolas,monospace;font-size:14px}
 pre{background:#f6f8fa;border:1px solid #e1e4e8;border-radius:6px;padding:12px;overflow:auto}
 pre code{background:none;padding:0}
 img{max-width:100%;border:1px solid #d0d7de;border-radius:6px;margin:12px 0;box-shadow:0 2px 6px rgba(0,0,0,.08)}
 blockquote{border-left:4px solid #b3d4f0;background:#f4f9fd;margin:16px 0;padding:10px 16px;color:#333}
 ul,ol{padding-left:26px}
 hr{border:none;border-top:1px solid #e1e4e8;margin:28px 0}
</style></head>
<body>
@BODY@
</body></html>
"""

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "使用指南.md"
    dst = sys.argv[2] if len(sys.argv) > 2 else "使用指南.html"
    md = open(src, encoding="utf-8").read()
    open(dst, "w", encoding="utf-8").write(TEMPLATE.replace("@BODY@", convert(md)))
    print("wrote", dst, os.path.getsize(dst), "bytes")

