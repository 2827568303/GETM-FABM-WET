import xlrd
import os

os.chdir('/mnt/c/Users/dinod/Desktop/GETM-FABM-WET/3DWET')

wb = xlrd.open_workbook('PL613162PLUS.xls')

out = open('_pclake_dump.txt', 'w', encoding='utf-8')

def w(s=''):
    out.write(s + '\n')

# ===== STATES SHEET =====
ws = wb.sheet_by_name('states')
w('=' * 100)
w('SHEET: states (state variables & initial conditions) - {} rows'.format(ws.nrows))
w('=' * 100)
w('{:<5} {:<30} {:<30} {:<18} {:<14} {:<14} {}'.format(
    'Id', 'InitStateName', 'StateName', 'Unit', 'Turbid0', 'Clear1', 'Description'))
w('-' * 200)
for i in range(1, ws.nrows):
    idv = ws.cell_value(i, 0)
    initname = ws.cell_value(i, 4)
    sname = ws.cell_value(i, 5)
    unit = ws.cell_value(i, 7)
    turbid = ws.cell_value(i, 8)
    clear = ws.cell_value(i, 9)
    desc = ws.cell_value(i, 15)
    w('{:<5} {:<30} {:<30} {:<18} {:<14} {:<14} {}'.format(
        idv, initname, sname, unit, turbid, clear, desc))

w('')
w('')

# ===== PARAMETERS SHEET =====
ws = wb.sheet_by_name('parameters')
w('=' * 100)
w('SHEET: parameters - {} rows'.format(ws.nrows))
w('=' * 100)
w('{:<5} {:<35} {:<18} {:<12} {:<12} {:<12} {}'.format(
    'Id', 'Name', 'Unit', 'Min', 'Max', 'Default0', 'Description'))
w('-' * 200)
for i in range(1, ws.nrows):
    idv = ws.cell_value(i, 0)
    name = ws.cell_value(i, 5)
    unit = ws.cell_value(i, 6)
    minv = ws.cell_value(i, 7)
    maxv = ws.cell_value(i, 8)
    defv = ws.cell_value(i, 9)
    desc = ws.cell_value(i, 16)
    w('{:<5} {:<35} {:<18} {:<12} {:<12} {:<12} {}'.format(
        idv, name, unit, minv, maxv, defv, desc))

w('')
w('')

# ===== INITIALSTATES SHEET =====
ws = wb.sheet_by_name('initialstates')
w('=' * 100)
w('SHEET: initialstates - {} rows'.format(ws.nrows))
w('=' * 100)
w('{:<5} {:<30} {:<18} {}'.format('Id', 'Name', 'Unit', 'Description'))
w('-' * 100)
for i in range(1, ws.nrows):
    idv = ws.cell_value(i, 0)
    name = ws.cell_value(i, 2)
    unit = ws.cell_value(i, 3)
    desc = ws.cell_value(i, 5)
    w('{:<5} {:<30} {:<18} {}'.format(idv, name, unit, desc))

out.close()
print('Dump complete - written to _pclake_dump.txt')
