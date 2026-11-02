"""Apply responsive, bounded demonstration defaults without altering physics."""
from datetime import datetime, timedelta
import re


def configure_demo(case):
    inp = case / 'getm.inp'
    text = inp.read_text(encoding='utf-8')
    start = datetime.strptime(re.search(r"(?im)^\s*start\s*=\s*['\"]([^'\"]+)", text)[1],
                              '%Y-%m-%d %H:%M:%S')
    replacements = {'timestep': '2', 'stop': repr(str(start + timedelta(minutes=20))),
                    'step_2d': '30', 'step_3d': '30', 'sync_2d': '1', 'sync_3d': '1',
                    'save_3d': '.false.', 'check_cfl': '.true.', 'save_initial': '.true.',
                    'hotstart': '.false.'}
    for key, value in replacements.items():
        text = re.sub(r'(?im)^(\s*' + key + r'\s*=\s*)[^\r\n!]+',
                      lambda m, value=value: m[1] + value, text)
    inp.write_text(text, encoding='utf-8')
    (case / 'output.yaml').write_text('output:\n   time_unit: second\n   time_step: 60\n'
        '   sync_interval: 1\n   variables:\n      - source: *\n', encoding='utf-8')
    (case / 'README.txt').write_text(
        f'{case.name}：湖泊耦合功能示例\n'
        '默认模拟20分钟，步长2秒，每60秒输出全部已注册科学变量。\n'
        '水动力、生态、鱼类及温室气体按本案例模型配置启用。\n'
        '关闭重复的旧式3D文件写入；output.nc保留三维水体与所有已注册变量。\n'
        '可在运行控制中开启GETM原生3D输出，以分析额外水动力诊断。\n'
        '日期界面采用年份+年内儒略日DOY；原生输入及NetCDF仍遵循ISO/CF规范。\n'
        '这些是短时功能演示参数，不代表湖泊长期预测或观测率定结论。\n'
        '延长模拟前请检查驱动覆盖、时间步长、输出频率与数值稳定性。\n', encoding='utf-8-sig')
