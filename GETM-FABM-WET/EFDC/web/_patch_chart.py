#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 index.html 的 drawChart 换成"每条曲线独立归一化"的版本（一次性补丁脚本）"""
import io, sys

P = r"C:\Users\23801\Desktop\GETM-FABM-WET-260928\GETM-FABM-WET\EFDC\web\index.html"
s = io.open(P, encoding="utf-8").read()

start_marker = "  const t = series.t, el = series.elev"
end_marker = "/* ---------------- 时钟 ---------------- */"
i = s.index(start_marker)
j = s.index(end_marker)

new = """  const t = series.t, el = series.elev, ve = series.vele, vn = series.veln;
  const t0 = t[0], t1 = t[t.length - 1] || t0 + 1;
  const X = v => padL + (t1 === t0 ? pw / 2 : (v - t0) / (t1 - t0) * pw);

  function scaleOf(arr) {
    const a = arr.filter(v => isFinite(v));
    if (!a.length) return [0, 1];
    let lo = Math.min.apply(null, a), hi = Math.max.apply(null, a);
    if (hi - lo < 1e-9) hi = lo + (Math.abs(lo) > 1 ? Math.abs(lo) * 1e-4 : 1);
    return [lo, hi];
  }

  const defs = [
    {arr: el, color: '#58a6ff', name: '水位'},
    {arr: ve, color: '#3fb950', name: '东向流速'},
    {arr: vn, color: '#d29922', name: '北向流速'}
  ];

  const eLo = scaleOf(el);
  g.fillStyle = '#8b949e'; g.font = '10px monospace';
  g.fillText(eLo[1].toFixed(2), 3, padT + 8);
  g.fillText(eLo[0].toFixed(2), 3, padT + ph);
  g.fillText('水位(m)', 3, padT + ph + 12);

  defs.forEach(function (def, di) {
    const arr = def.arr;
    if (!arr || !arr.length) return;
    const sc = scaleOf(arr), lo = sc[0], hi = sc[1];
    g.beginPath(); g.strokeStyle = def.color; g.lineWidth = 1.6;
    arr.forEach(function (v, i) {
      const y = padT + ph - (isFinite(v) ? (v - lo) / (hi - lo) * ph : ph / 2);
      if (i) g.lineTo(X(t[i]), y); else g.moveTo(X(t[i]), y);
    });
    g.stroke();
    const last = arr[arr.length - 1];
    if (isFinite(last)) {
      g.fillStyle = def.color;
      g.font = '10px monospace';
      g.fillText(def.name + ' ' + last.toFixed(2), padL + 4, padT + 12 * (di + 1));
    }
  });

  g.fillStyle = '#8b949e'; g.font = '10px monospace';
  g.fillText('t=' + t0.toFixed(1) + 'd', padL, H - 6);
  g.fillText(t1.toFixed(1) + 'd', W - 52, H - 6);
}

"""

s = s[:i] + new + s[j:]
io.open(P, "w", encoding="utf-8").write(s)
print("patched drawChart ok")
