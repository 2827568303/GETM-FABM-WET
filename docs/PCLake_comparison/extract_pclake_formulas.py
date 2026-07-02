"""
从 PCLake+Gras .xls 文件批量提取所有 derivatives 和 parameters 公式
输出到 CSV 供 WET 公式对比文档引用

用法:
    python extract_pclake_formulas.py

输出:
    docs/PCLake_comparison/pclake_derivatives.csv  (所有微分方程/辅助方程)
    docs/PCLake_comparison/pclake_parameters.csv   (所有参数定义)
    docs/PCLake_comparison/pclake_states.csv       (所有状态变量定义)
"""
import xlrd
import csv
import os
from pathlib import Path

# PCLake+Gras .xls 文件路径
XLS_PATH = r'D:\05_硕博学业\01_博士论文\Single run-gras&defult\PCModel-PLUS_Gras_mass-H4-H7\Licence_agreement\I_accept\PCModel1350\PCModel\3.00\Models\PCLake+\6.13.16\PL613162PLUS_Gras_Mode_order_mass_DC_Run.xls'

# 输出目录
OUT_DIR = Path(r'c:\Users\dinod\Desktop\GETM-FABM-WET\docs\PCLake_comparison')
OUT_DIR.mkdir(parents=True, exist_ok=True)


def clean_name(name):
    """清理 PCLake 变量名的前后下划线: _sNH4W_ -> sNH4W"""
    if not name:
        return ''
    s = str(name).strip()
    if s.startswith('_'):
        s = s[1:]
    if s.endswith('_'):
        s = s[:-1]
    return s


def extract_derivatives(wb):
    """提取 derivatives sheet 的所有方程"""
    sh = wb.sheet_by_name('derivatives')
    rows = []
    # 列定义: 0=lId, 5=sName, 6=sUnit, 7=sTargetValue, 8=sEquation(type),
    #         9=sDescription, 10=sRemark, 12-15=code versions (公式)
    for r in range(1, sh.nrows):
        name = clean_name(sh.cell_value(r, 5))
        if not name:
            continue
        unit = str(sh.cell_value(r, 6)).strip() if sh.cell_value(r, 6) else ''
        eq_type = str(sh.cell_value(r, 8)).strip() if sh.cell_value(r, 8) else ''
        desc = str(sh.cell_value(r, 9)).strip() if sh.cell_value(r, 9) else ''
        remark = str(sh.cell_value(r, 10)).strip() if sh.cell_value(r, 10) else ''
        # 取最新版本公式 (col 15)
        formula = str(sh.cell_value(r, 15)).strip() if sh.cell_value(r, 15) else ''
        if formula == '':
            # 回退到 col 12
            formula = str(sh.cell_value(r, 12)).strip() if sh.cell_value(r, 12) else ''

        rows.append({
            'lId': sh.cell_value(r, 0),
            'name': name,
            'unit': unit,
            'equation_type': eq_type,
            'formula': formula,
            'description': desc,
            'remark': remark,
        })

    out_path = OUT_DIR / 'pclake_derivatives.csv'
    with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['lId', 'name', 'unit', 'equation_type',
                                               'formula', 'description', 'remark'])
        writer.writeheader()
        writer.writerows(rows)
    print(f'  derivatives: {len(rows)} rows -> {out_path}')
    return rows


def extract_parameters(wb):
    """提取 parameters sheet"""
    sh = wb.sheet_by_name('parameters')
    rows = []
    for r in range(1, sh.nrows):
        name = clean_name(sh.cell_value(r, 5))
        if not name:
            continue
        unit = str(sh.cell_value(r, 6)).strip() if sh.cell_value(r, 6) else ''
        min_v = sh.cell_value(r, 7) if sh.cell_value(r, 7) != '' else ''
        # 参数 sheet 列较多, 取关键列
        row_data = {
            'lId': sh.cell_value(r, 0),
            'name': name,
            'unit': unit,
            'min_value': min_v,
        }
        # 尝试取更多列 (max value, default value 等)
        for c, key in [(8, 'max_value'), (9, 'default_value'), (10, 'description')]:
            if c < sh.ncols and sh.cell_value(r, c) != '':
                row_data[key] = str(sh.cell_value(r, c)).strip()
            else:
                row_data[key] = ''
        rows.append(row_data)

    out_path = OUT_DIR / 'pclake_parameters.csv'
    with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['lId', 'name', 'unit', 'min_value',
                                               'max_value', 'default_value', 'description'])
        writer.writeheader()
        writer.writerows(rows)
    print(f'  parameters: {len(rows)} rows -> {out_path}')
    return rows


def extract_states(wb):
    """提取 states sheet"""
    sh = wb.sheet_by_name('states')
    rows = []
    for r in range(1, sh.nrows):
        name = clean_name(sh.cell_value(r, 5))
        if not name:
            continue
        row_data = {'lId': sh.cell_value(r, 0), 'name': name}
        for c in range(6, min(sh.ncols, 15)):
            v = sh.cell_value(r, c)
            if v != '':
                row_data[f'col{c}'] = str(v).strip()
        rows.append(row_data)

    out_path = OUT_DIR / 'pclake_states.csv'
    with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
        if rows:
            keys = ['lId', 'name'] + [f'col{c}' for c in range(6, 15)]
            writer = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(rows)
    print(f'  states: {len(rows)} rows -> {out_path}')
    return rows


def search_derivative(rows, keyword):
    """搜索包含关键词的 derivative 行"""
    print(f'\n=== 搜索: {keyword} ===')
    matches = []
    for row in rows:
        if keyword.lower() in row['name'].lower():
            matches.append(row)
            print(f"  [{row['lId']:>4.0f}] {row['name']:<30s} | {row['equation_type']:<25s} | {row['formula'][:100]}")
    if not matches:
        print(f'  (未找到匹配)')
    return matches


def main():
    print(f'读取 PCLake+Gras: {XLS_PATH}')
    wb = xlrd.open_workbook(XLS_PATH)

    print('\n提取中...')
    deriv_rows = extract_derivatives(wb)
    param_rows = extract_parameters(wb)
    state_rows = extract_states(wb)

    # 输出关键过程搜索示例 (便于后续 WET 对比)
    print('\n=== 关键过程搜索示例 ===')
    for kw in ['NitrW', 'PSorpIMW', 'SiMinPaW', 'O2Aer', 'O2BOD', 'PEqIMW', 'KPAdsW',
               'DenitW', 'O2MinOMW', 'DMinDOMW']:
        search_derivative(deriv_rows, kw)

    print(f'\n完成。输出目录: {OUT_DIR}')


if __name__ == '__main__':
    main()
